"""
FLUX Trade Buddy - Enhanced Image Generation with Gallery Management
A professional console-themed interface for generating, comparing, and managing FLUX images.
"""

import os
import time
import uuid
from pathlib import Path

import gradio as gr
import numpy as np
import torch
from einops import rearrange
from PIL import ExifTags, Image
from transformers import pipeline

from flux.assets import AssetCatalog, AssetLinks
from flux.cli import SamplingOptions
from flux.sampling import denoise, get_noise, get_schedule, prepare, unpack
from flux.theme import get_custom_css_for_gradio, get_gradio_theme
from flux.trade_buddy import PromptLibrary, TradeBuddy
from flux.util import (
    configs,
    embed_watermark,
    load_ae,
    load_clip,
    load_flow_model,
    load_t5,
    track_usage_via_api,
)

NSFW_THRESHOLD = 0.85


def get_models(name: str, device: torch.device, offload: bool, is_schnell: bool):
    t5 = load_t5(device, max_length=256 if is_schnell else 512)
    clip = load_clip(device)
    model = load_flow_model(name, device="cpu" if offload else device)
    ae = load_ae(name, device="cpu" if offload else device)
    nsfw_classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection", device=device)
    return model, ae, t5, clip, nsfw_classifier


class FluxTradeBuddy:
    def __init__(self, model_name: str, device: str, offload: bool, track_usage: bool):
        self.device = torch.device(device)
        self.offload = offload
        self.model_name = model_name
        self.is_schnell = model_name == "flux-schnell"
        self.model, self.ae, self.t5, self.clip, self.nsfw_classifier = get_models(
            model_name,
            device=self.device,
            offload=self.offload,
            is_schnell=self.is_schnell,
        )
        self.track_usage = track_usage
        self.trade_buddy = TradeBuddy()
        self.prompt_library = PromptLibrary()
        self.asset_catalog = AssetCatalog()
        self.last_generation = None

    @torch.inference_mode()
    def generate_image(
        self,
        width,
        height,
        num_steps,
        guidance,
        seed,
        prompt,
        init_image=None,
        image2image_strength=0.0,
        add_sampling_metadata=True,
        save_to_gallery=True,
        tags_str="",
    ):
        seed = int(seed)
        if seed == -1:
            seed = None

        opts = SamplingOptions(
            prompt=prompt,
            width=width,
            height=height,
            num_steps=num_steps,
            guidance=guidance,
            seed=seed,
        )

        if opts.seed is None:
            opts.seed = torch.Generator(device="cpu").seed()
        print(f"🎨 Generating '{opts.prompt}' with seed {opts.seed}")
        t0 = time.perf_counter()

        if init_image is not None:
            if isinstance(init_image, np.ndarray):
                init_image = torch.from_numpy(init_image).permute(2, 0, 1).float() / 255.0
                init_image = init_image.unsqueeze(0)
            init_image = init_image.to(self.device)
            init_image = torch.nn.functional.interpolate(init_image, (opts.height, opts.width))
            if self.offload:
                self.ae.encoder.to(self.device)
            init_image = self.ae.encode(init_image.to())
            if self.offload:
                self.ae = self.ae.cpu()
                torch.cuda.empty_cache()

        x = get_noise(
            1,
            opts.height,
            opts.width,
            device=self.device,
            dtype=torch.bfloat16,
            seed=opts.seed,
        )
        timesteps = get_schedule(
            opts.num_steps,
            x.shape[-1] * x.shape[-2] // 4,
            shift=(not self.is_schnell),
        )
        if init_image is not None:
            t_idx = int((1 - image2image_strength) * num_steps)
            t = timesteps[t_idx]
            timesteps = timesteps[t_idx:]
            x = t * x + (1.0 - t) * init_image.to(x.dtype)

        if self.offload:
            self.t5, self.clip = self.t5.to(self.device), self.clip.to(self.device)
        inp = prepare(t5=self.t5, clip=self.clip, img=x, prompt=opts.prompt)

        if self.offload:
            self.t5, self.clip = self.t5.cpu(), self.clip.cpu()
            torch.cuda.empty_cache()
            self.model = self.model.to(self.device)

        x = denoise(self.model, **inp, timesteps=timesteps, guidance=opts.guidance)

        if self.offload:
            self.model.cpu()
            torch.cuda.empty_cache()
            self.ae.decoder.to(x.device)

        x = unpack(x.float(), opts.height, opts.width)
        with torch.autocast(device_type=self.device.type, dtype=torch.bfloat16):
            x = self.ae.decode(x)

        if self.offload:
            self.ae.decoder.cpu()
            torch.cuda.empty_cache()

        t1 = time.perf_counter()
        print(f"✅ Done in {t1 - t0:.1f}s.")

        x = x.clamp(-1, 1)
        x = embed_watermark(x.float())
        x = rearrange(x[0], "c h w -> h w c")

        img = Image.fromarray((127.5 * (x + 1.0)).cpu().byte().numpy())
        nsfw_score = [x["score"] for x in self.nsfw_classifier(img) if x["label"] == "nsfw"][0]

        if nsfw_score < NSFW_THRESHOLD:
            filename = f"output/trade_buddy/{uuid.uuid4()}.jpg"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            exif_data = Image.Exif()
            if init_image is None:
                exif_data[ExifTags.Base.Software] = "AI generated;txt2img;flux;trade-buddy"
            else:
                exif_data[ExifTags.Base.Software] = "AI generated;img2img;flux;trade-buddy"
            exif_data[ExifTags.Base.Make] = "Black Forest Labs - Trade Buddy"
            exif_data[ExifTags.Base.Model] = self.model_name
            if add_sampling_metadata:
                exif_data[ExifTags.Base.ImageDescription] = prompt
            img.save(filename, format="jpeg", exif=exif_data, quality=95, subsampling=0)

            if self.track_usage:
                track_usage_via_api(self.model_name, 1)

            # Save to Trade Buddy gallery
            if save_to_gallery:
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                self.last_generation = self.trade_buddy.add_generation(
                    image_path=filename,
                    prompt=prompt,
                    seed=opts.seed,
                    model=self.model_name,
                    width=opts.width,
                    height=opts.height,
                    steps=opts.num_steps,
                    guidance=opts.guidance,
                    tags=tags,
                )
                gallery_info = f"✅ Saved to gallery! ID: {self.last_generation.id}"
            else:
                gallery_info = "Not saved to gallery"

            stats = self.trade_buddy.get_stats()
            stats_text = f"📊 Gallery Stats: {stats['total']} images | Avg Rating: {stats['avg_rating']}⭐"

            return img, str(opts.seed), filename, None, f"{gallery_info}\n{stats_text}"
        else:
            return None, str(opts.seed), None, "⚠️ Your generated image may contain NSFW content.", ""

    def get_gallery_html(self, search_term="", tag_filter="", sort_by="recent"):
        """Generate HTML for gallery view."""
        if search_term:
            generations = self.trade_buddy.search_by_prompt(search_term)
        elif tag_filter:
            generations = self.trade_buddy.search_by_tag(tag_filter)
        elif sort_by == "top_rated":
            generations = self.trade_buddy.get_top_rated(20)
        else:
            generations = self.trade_buddy.get_recent(20)

        html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; padding: 10px;">'
        
        for gen in generations:
            if os.path.exists(gen.image_path):
                stars = "⭐" * gen.rating if gen.rating > 0 else "☆☆☆☆☆"
                tags_html = " ".join([f'<span style="background: #00d4ff; color: #1a1a1a; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">{tag}</span>' for tag in gen.tags])
                
                html += f'''
                <div style="background: #2d2d2d; border: 1px solid #444; border-radius: 8px; padding: 10px; color: #fff;">
                    <img src="file/{gen.image_path}" style="width: 100%; border-radius: 4px; margin-bottom: 8px;">
                    <div style="font-size: 0.85em; margin-bottom: 5px;">{stars}</div>
                    <div style="font-size: 0.75em; color: #ccc; margin-bottom: 5px; max-height: 60px; overflow: hidden;">{gen.prompt[:100]}...</div>
                    <div style="font-size: 0.7em; color: #aaa;">Seed: {gen.seed} | Steps: {gen.steps}</div>
                    <div style="margin-top: 5px;">{tags_html}</div>
                </div>
                '''
        
        html += '</div>'
        return html if generations else "<p style='color: #ccc; text-align: center; padding: 40px;'>No images found. Start generating!</p>"

    def get_prompt_suggestions(self, category="nature"):
        """Get prompt suggestions from library."""
        prompts = self.prompt_library.get_by_category(category)
        if prompts:
            examples = []
            for key, data in list(prompts.items())[:3]:
                examples.extend(data.get("examples", []))
            return "\n\n".join(examples[:5])
        return "No suggestions available"


def create_demo(
    model_name: str,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    offload: bool = False,
    track_usage: bool = False,
):
    generator = FluxTradeBuddy(model_name, device, offload, track_usage)
    is_schnell = model_name == "flux-schnell"

    # Get theme
    theme = get_gradio_theme()
    custom_css = get_custom_css_for_gradio()

    with gr.Blocks(theme=theme, css=custom_css, title="FLUX Trade Buddy") as demo:
        gr.Markdown(
            f"""
            # 🎨 FLUX Trade Buddy - Professional Image Generation Studio
            ### Model: {model_name} | Your AI Art Management System
            Generate, Compare, and Manage your AI creations like a pro!
            """
        )

        with gr.Tabs():
            # Generation Tab
            with gr.TabItem("🎨 Generate", id=0):
                with gr.Row():
                    with gr.Column(scale=1):
                        prompt = gr.Textbox(
                            label="Prompt",
                            value='a photo of a forest with mist swirling around the tree trunks. The word "FLUX" is painted over it in big, red brush strokes with visible texture',
                            lines=3,
                        )
                        
                        with gr.Row():
                            prompt_category = gr.Dropdown(
                                choices=["nature", "portrait", "abstract"],
                                label="Prompt Templates",
                                value="nature",
                            )
                            load_suggestions_btn = gr.Button("💡 Get Suggestions", size="sm")
                        
                        prompt_suggestions = gr.Textbox(
                            label="Prompt Ideas",
                            lines=3,
                            interactive=False,
                        )
                        
                        tags_input = gr.Textbox(
                            label="Tags (comma separated)",
                            placeholder="landscape, nature, forest",
                        )
                        
                        do_img2img = gr.Checkbox(label="Image to Image", value=False, interactive=not is_schnell)
                        init_image = gr.Image(label="Input Image", visible=False)
                        image2image_strength = gr.Slider(
                            0.0, 1.0, 0.8, step=0.1, label="Noising strength", visible=False
                        )

                        with gr.Accordion("⚙️ Advanced Options", open=False):
                            width = gr.Slider(128, 8192, 1360, step=16, label="Width")
                            height = gr.Slider(128, 8192, 768, step=16, label="Height")
                            num_steps = gr.Slider(1, 50, 4 if is_schnell else 50, step=1, label="Number of steps")
                            guidance = gr.Slider(
                                1.0, 10.0, 3.5, step=0.1, label="Guidance", interactive=not is_schnell
                            )
                            seed = gr.Textbox(-1, label="Seed (-1 for random)")
                            add_sampling_metadata = gr.Checkbox(
                                label="Add sampling parameters to metadata?", value=True
                            )
                            save_to_gallery = gr.Checkbox(
                                label="💾 Save to Trade Buddy Gallery", value=True
                            )

                        generate_btn = gr.Button("🚀 Generate Image", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        output_image = gr.Image(label="Generated Image")
                        seed_output = gr.Number(label="Used Seed")
                        gallery_status = gr.Textbox(label="Gallery Status", lines=2)
                        warning_text = gr.Textbox(label="Warning", visible=False)
                        download_btn = gr.File(label="📥 Download Full-Resolution")

                def update_img2img(do_img2img):
                    return {
                        init_image: gr.update(visible=do_img2img),
                        image2image_strength: gr.update(visible=do_img2img),
                    }

                def load_suggestions(category):
                    return generator.get_prompt_suggestions(category)

                do_img2img.change(update_img2img, do_img2img, [init_image, image2image_strength])
                load_suggestions_btn.click(load_suggestions, [prompt_category], [prompt_suggestions])

                generate_btn.click(
                    fn=generator.generate_image,
                    inputs=[
                        width,
                        height,
                        num_steps,
                        guidance,
                        seed,
                        prompt,
                        init_image,
                        image2image_strength,
                        add_sampling_metadata,
                        save_to_gallery,
                        tags_input,
                    ],
                    outputs=[output_image, seed_output, download_btn, warning_text, gallery_status],
                )

            # Gallery Tab
            with gr.TabItem("🖼️ Gallery", id=1):
                gr.Markdown("### Your Image Collection")
                
                with gr.Row():
                    search_input = gr.Textbox(label="🔍 Search by prompt", placeholder="Enter keywords...")
                    tag_filter = gr.Textbox(label="🏷️ Filter by tag", placeholder="Enter tag...")
                    sort_dropdown = gr.Dropdown(
                        choices=["recent", "top_rated"],
                        label="Sort by",
                        value="recent",
                    )
                    refresh_btn = gr.Button("🔄 Refresh", size="sm")
                
                gallery_view = gr.HTML()
                
                def refresh_gallery(search="", tag="", sort="recent"):
                    return generator.get_gallery_html(search, tag, sort)
                
                # Initial load
                demo.load(refresh_gallery, inputs=[search_input, tag_filter, sort_dropdown], outputs=[gallery_view])
                refresh_btn.click(refresh_gallery, inputs=[search_input, tag_filter, sort_dropdown], outputs=[gallery_view])
                search_input.change(refresh_gallery, inputs=[search_input, tag_filter, sort_dropdown], outputs=[gallery_view])
                tag_filter.change(refresh_gallery, inputs=[search_input, tag_filter, sort_dropdown], outputs=[gallery_view])
                sort_dropdown.change(refresh_gallery, inputs=[search_input, tag_filter, sort_dropdown], outputs=[gallery_view])

            # Stats Tab
            with gr.TabItem("📊 Stats", id=2):
                gr.Markdown("### Trade Buddy Statistics")
                stats_display = gr.JSON(label="Gallery Statistics")
                refresh_stats_btn = gr.Button("🔄 Refresh Stats")
                
                def get_stats():
                    return generator.trade_buddy.get_stats()
                
                demo.load(get_stats, outputs=[stats_display])
                refresh_stats_btn.click(get_stats, outputs=[stats_display])
            
            # Assets Tab
            with gr.TabItem("🔗 Assets", id=3):
                gr.Markdown("### FLUX Asset Library - Example Images & Resources")
                
                with gr.Row():
                    asset_category = gr.Dropdown(
                        choices=["all", "examples", "docs"],
                        label="Category",
                        value="all",
                    )
                    refresh_assets_btn = gr.Button("🔄 Refresh Assets")
                
                assets_html = gr.HTML()
                
                gr.Markdown("### 📋 Quick Asset Links")
                quick_links_html = gr.HTML(value=AssetLinks.get_links_html())
                
                def show_assets(category):
                    if category == "all":
                        return generator.asset_catalog.get_html_gallery()
                    else:
                        return generator.asset_catalog.get_html_gallery(category=category)
                
                demo.load(show_assets, inputs=[asset_category], outputs=[assets_html])
                refresh_assets_btn.click(show_assets, inputs=[asset_category], outputs=[assets_html])
                asset_category.change(show_assets, inputs=[asset_category], outputs=[assets_html])

        gr.Markdown(
            """
            ---
            ### 💡 Trade Buddy Features:
            - **Generate**: Create stunning images with FLUX
            - **Gallery**: Organize and manage all your generations
            - **Search & Filter**: Find images by prompt or tags
            - **Rate & Tag**: Organize your best work
            - **Stats**: Track your creative journey
            
            *Powered by FLUX + Trade Buddy System*
            """
        )

    return demo


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FLUX Trade Buddy")
    parser.add_argument(
        "--name", type=str, default="flux-schnell", choices=list(configs.keys()), help="Model name"
    )
    parser.add_argument(
        "--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu", help="Device to use"
    )
    parser.add_argument("--offload", action="store_true", help="Offload model to CPU when not in use")
    parser.add_argument("--share", action="store_true", help="Create a public link to your demo")
    parser.add_argument("--track_usage", action="store_true", help="Track usage for licensing purposes")
    args = parser.parse_args()

    demo = create_demo(args.name, args.device, args.offload, args.track_usage)
    demo.launch(share=args.share)

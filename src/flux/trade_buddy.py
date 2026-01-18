"""
Trade Buddy - Advanced Image Generation Management and Comparison System
A powerful companion for FLUX image generation with trading, comparison, and iteration features.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image


class ImageGeneration:
    """Represents a single image generation with metadata."""
    
    def __init__(
        self,
        image_path: str,
        prompt: str,
        seed: int,
        model: str,
        width: int,
        height: int,
        steps: int,
        guidance: float,
        timestamp: Optional[str] = None,
        tags: Optional[List[str]] = None,
        rating: int = 0,
        notes: str = "",
    ):
        self.image_path = image_path
        self.prompt = prompt
        self.seed = seed
        self.model = model
        self.width = width
        self.height = height
        self.steps = steps
        self.guidance = guidance
        self.timestamp = timestamp or datetime.now().isoformat()
        self.tags = tags or []
        self.rating = rating
        self.notes = notes
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID from timestamp and seed."""
        return f"{self.timestamp}_{self.seed}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "image_path": self.image_path,
            "prompt": self.prompt,
            "seed": self.seed,
            "model": self.model,
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "guidance": self.guidance,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "rating": self.rating,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ImageGeneration":
        """Create from dictionary."""
        return cls(
            image_path=data["image_path"],
            prompt=data["prompt"],
            seed=data["seed"],
            model=data["model"],
            width=data["width"],
            height=data["height"],
            steps=data["steps"],
            guidance=data["guidance"],
            timestamp=data.get("timestamp"),
            tags=data.get("tags", []),
            rating=data.get("rating", 0),
            notes=data.get("notes", ""),
        )


class TradeBuddy:
    """
    Trade Buddy - Manage your image generation portfolio.
    
    Features:
    - Save and organize all generations
    - Compare multiple images side-by-side
    - Rate and tag images
    - Track prompt variations and their results
    - Export/import collections for sharing
    - Suggest variations based on successful generations
    """
    
    def __init__(self, gallery_path: str = "trade_buddy_gallery"):
        self.gallery_path = Path(gallery_path)
        self.gallery_path.mkdir(exist_ok=True)
        self.db_path = self.gallery_path / "gallery.json"
        self.generations: List[ImageGeneration] = []
        self.load_gallery()
    
    def load_gallery(self):
        """Load gallery from JSON database."""
        if self.db_path.exists():
            with open(self.db_path, "r") as f:
                data = json.load(f)
                self.generations = [ImageGeneration.from_dict(g) for g in data]
        else:
            self.generations = []
    
    def save_gallery(self):
        """Save gallery to JSON database."""
        with open(self.db_path, "w") as f:
            json.dump([g.to_dict() for g in self.generations], f, indent=2)
    
    def add_generation(
        self,
        image_path: str,
        prompt: str,
        seed: int,
        model: str,
        width: int,
        height: int,
        steps: int,
        guidance: float,
        tags: Optional[List[str]] = None,
    ) -> ImageGeneration:
        """Add a new generation to the gallery."""
        gen = ImageGeneration(
            image_path=image_path,
            prompt=prompt,
            seed=seed,
            model=model,
            width=width,
            height=height,
            steps=steps,
            guidance=guidance,
            tags=tags,
        )
        self.generations.append(gen)
        self.save_gallery()
        return gen
    
    def get_generation(self, gen_id: str) -> Optional[ImageGeneration]:
        """Get a generation by ID."""
        for gen in self.generations:
            if gen.id == gen_id:
                return gen
        return None
    
    def search_by_prompt(self, search_term: str) -> List[ImageGeneration]:
        """Search generations by prompt text."""
        return [g for g in self.generations if search_term.lower() in g.prompt.lower()]
    
    def search_by_tag(self, tag: str) -> List[ImageGeneration]:
        """Get all generations with a specific tag."""
        return [g for g in self.generations if tag in g.tags]
    
    def get_top_rated(self, limit: int = 10) -> List[ImageGeneration]:
        """Get top rated generations."""
        sorted_gens = sorted(self.generations, key=lambda g: g.rating, reverse=True)
        return sorted_gens[:limit]
    
    def get_recent(self, limit: int = 10) -> List[ImageGeneration]:
        """Get most recent generations."""
        sorted_gens = sorted(self.generations, key=lambda g: g.timestamp, reverse=True)
        return sorted_gens[:limit]
    
    def update_rating(self, gen_id: str, rating: int):
        """Update rating for a generation (1-5 stars)."""
        gen = self.get_generation(gen_id)
        if gen:
            gen.rating = max(0, min(5, rating))
            self.save_gallery()
    
    def add_tags(self, gen_id: str, tags: List[str]):
        """Add tags to a generation."""
        gen = self.get_generation(gen_id)
        if gen:
            gen.tags.extend([t for t in tags if t not in gen.tags])
            self.save_gallery()
    
    def add_notes(self, gen_id: str, notes: str):
        """Add notes to a generation."""
        gen = self.get_generation(gen_id)
        if gen:
            gen.notes = notes
            self.save_gallery()
    
    def get_prompt_variations(self, prompt: str, max_results: int = 5) -> List[ImageGeneration]:
        """Find generations with similar prompts."""
        # Simple similarity based on word overlap
        prompt_words = set(prompt.lower().split())
        
        def similarity(gen: ImageGeneration) -> float:
            gen_words = set(gen.prompt.lower().split())
            if not gen_words:
                return 0.0
            intersection = prompt_words & gen_words
            return len(intersection) / len(gen_words)
        
        similar = [(g, similarity(g)) for g in self.generations]
        similar.sort(key=lambda x: x[1], reverse=True)
        return [g for g, score in similar[:max_results] if score > 0.3]
    
    def suggest_variations(self, gen_id: str) -> Dict[str, any]:
        """Suggest parameter variations based on a generation."""
        gen = self.get_generation(gen_id)
        if not gen:
            return {}
        
        suggestions = {
            "seeds": [gen.seed + i for i in range(1, 6)],
            "steps": [max(1, gen.steps - 10), gen.steps, gen.steps + 10],
            "guidance": [
                max(1.0, gen.guidance - 1.0),
                gen.guidance,
                gen.guidance + 1.0,
            ],
            "sizes": [
                (gen.width // 2, gen.height // 2),
                (gen.width, gen.height),
                (gen.width * 2, gen.height * 2),
            ],
        }
        return suggestions
    
    def export_collection(self, tag: str, output_path: str):
        """Export a collection of images by tag."""
        gens = self.search_by_tag(tag)
        export_data = {
            "tag": tag,
            "count": len(gens),
            "exported_at": datetime.now().isoformat(),
            "generations": [g.to_dict() for g in gens],
        }
        
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
    
    def import_collection(self, import_path: str):
        """Import a collection from JSON."""
        with open(import_path, "r") as f:
            data = json.load(f)
            for gen_data in data.get("generations", []):
                gen = ImageGeneration.from_dict(gen_data)
                # Check if not already exists
                if not any(g.id == gen.id for g in self.generations):
                    self.generations.append(gen)
        self.save_gallery()
    
    def get_stats(self) -> Dict:
        """Get statistics about the gallery."""
        if not self.generations:
            return {
                "total": 0,
                "avg_rating": 0,
                "models_used": {},
                "total_images": 0,
            }
        
        models = {}
        for gen in self.generations:
            models[gen.model] = models.get(gen.model, 0) + 1
        
        rated = [g for g in self.generations if g.rating > 0]
        avg_rating = sum(g.rating for g in rated) / len(rated) if rated else 0
        
        all_tags = {}
        for gen in self.generations:
            for tag in gen.tags:
                all_tags[tag] = all_tags.get(tag, 0) + 1
        
        return {
            "total": len(self.generations),
            "avg_rating": round(avg_rating, 2),
            "models_used": models,
            "total_images": len(self.generations),
            "top_tags": sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10],
        }
    
    def create_comparison_grid(
        self,
        gen_ids: List[str],
        output_path: str,
        grid_cols: int = 2,
    ):
        """Create a comparison grid from multiple generations."""
        gens = [self.get_generation(gid) for gid in gen_ids if self.get_generation(gid)]
        
        if not gens:
            return None
        
        # Load images
        images = []
        for gen in gens:
            if os.path.exists(gen.image_path):
                images.append(Image.open(gen.image_path))
        
        if not images:
            return None
        
        # Calculate grid dimensions
        grid_rows = (len(images) + grid_cols - 1) // grid_cols
        
        # Get max dimensions for uniformity
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # Create grid
        grid_width = max_width * grid_cols
        grid_height = max_height * grid_rows
        grid_image = Image.new("RGB", (grid_width, grid_height), (0, 0, 0))
        
        # Paste images
        for idx, img in enumerate(images):
            row = idx // grid_cols
            col = idx % grid_cols
            x = col * max_width
            y = row * max_height
            grid_image.paste(img, (x, y))
        
        grid_image.save(output_path)
        return output_path


class PromptLibrary:
    """
    Manage a library of reusable prompts and prompt templates.
    """
    
    def __init__(self, library_path: str = "prompt_library.json"):
        self.library_path = Path(library_path)
        self.prompts: Dict[str, Dict] = {}
        self.load_library()
    
    def load_library(self):
        """Load prompt library from JSON."""
        if self.library_path.exists():
            with open(self.library_path, "r") as f:
                self.prompts = json.load(f)
        else:
            self.prompts = self._get_default_prompts()
            self.save_library()
    
    def save_library(self):
        """Save prompt library to JSON."""
        with open(self.library_path, "w") as f:
            json.dump(self.prompts, f, indent=2)
    
    def _get_default_prompts(self) -> Dict:
        """Get default starter prompts."""
        return {
            "nature": {
                "name": "Nature Scene",
                "template": "a photo of {subject} in {environment}, {lighting}, {style}",
                "examples": [
                    "a photo of a waterfall in a lush forest, golden hour lighting, cinematic",
                    "a photo of mountains in winter, dramatic sunset, photorealistic",
                ],
                "category": "photography",
            },
            "portrait": {
                "name": "Portrait",
                "template": "portrait of {subject}, {style}, {lighting}, {quality}",
                "examples": [
                    "portrait of a wise elder, oil painting style, rembrandt lighting, masterpiece",
                    "portrait of a cyberpunk character, neon lights, highly detailed",
                ],
                "category": "character",
            },
            "abstract": {
                "name": "Abstract Art",
                "template": "abstract {style} art with {colors} and {patterns}",
                "examples": [
                    "abstract geometric art with vibrant colors and flowing patterns",
                    "abstract expressionist art with bold colors and dynamic brushstrokes",
                ],
                "category": "art",
            },
        }
    
    def add_prompt(self, key: str, name: str, template: str, category: str = "custom", examples: Optional[List[str]] = None):
        """Add a new prompt to the library."""
        self.prompts[key] = {
            "name": name,
            "template": template,
            "category": category,
            "examples": examples or [],
        }
        self.save_library()
    
    def get_prompt(self, key: str) -> Optional[Dict]:
        """Get a prompt by key."""
        return self.prompts.get(key)
    
    def get_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all prompts in a category."""
        return {k: v for k, v in self.prompts.items() if v.get("category") == category}
    
    def fill_template(self, key: str, **kwargs) -> str:
        """Fill a prompt template with values."""
        prompt = self.get_prompt(key)
        if not prompt:
            return ""
        
        template = prompt["template"]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Missing parameter: {e}"
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return list(set(p.get("category", "uncategorized") for p in self.prompts.values()))

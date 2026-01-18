# 🎨 FLUX Console Theme & Trade Buddy - Installation & Usage

## 🚀 Quick Start

### 1. Installation

The Trade Buddy system is already integrated! Just ensure you have FLUX dependencies:

```bash
cd /home/runner/work/flux/flux
pip install -e ".[all]"
```

### 2. Launch Trade Buddy

**Full Trade Buddy Experience (Recommended):**
```bash
python demo_trade_buddy.py --name flux-schnell
```

**Classic Interfaces with Console Theme:**
```bash
# Gradio
python demo_gr.py --name flux-schnell

# Streamlit
streamlit run demo_st.py -- --device cuda

# Streamlit Fill
streamlit run demo_st_fill.py -- --device cuda
```

## 📦 What's Included

### 🎨 Console Theme System
- **Location**: `src/flux/theme.py`
- **Features**: 
  - Professional dark theme with cyan accents
  - Responsive design (mobile, tablet, desktop)
  - Consistent styling for Gradio and Streamlit
  - Custom CSS with smooth animations
  - Monospace fonts for technical aesthetic

### 🗂️ Trade Buddy Gallery
- **Location**: `src/flux/trade_buddy.py`
- **Features**:
  - Save all generations with metadata
  - Rate images (1-5 stars)
  - Tag and categorize
  - Search and filter
  - Statistics dashboard
  - Export/import collections
  - Comparison grids

### 🔗 Asset Catalog
- **Location**: `src/flux/assets.py`
- **Features**:
  - Complete catalog of FLUX example images
  - Quick links to documentation assets
  - Visual gallery browser
  - File metadata and sizes
  - Programmatic access

### 📚 Prompt Library
- **Location**: `src/flux/trade_buddy.py` (PromptLibrary class)
- **Features**:
  - Pre-built prompt templates
  - Organized by category
  - Example prompts
  - Template filling system

## 🎯 Features Comparison

| Feature | demo_trade_buddy.py | demo_gr.py | demo_st.py | demo_st_fill.py |
|---------|---------------------|------------|------------|-----------------|
| Console Theme | ✅ | ✅ | ✅ | ✅ |
| Image Generation | ✅ | ✅ | ✅ | ✅ |
| Gallery Management | ✅ | ❌ | ❌ | ❌ |
| Asset Catalog | ✅ | ❌ | ❌ | ❌ |
| Prompt Library | ✅ | ❌ | ❌ | ❌ |
| Statistics | ✅ | ❌ | ❌ | ❌ |
| Search & Filter | ✅ | ❌ | ❌ | ❌ |
| Inpainting/Outpainting | ❌ | ❌ | ❌ | ✅ |

## 📖 Documentation Files

1. **README.md** - Main FLUX documentation
2. **ASSETS_README.md** - Complete asset catalog with links
3. **TRADE_BUDDY_GUIDE.md** - Detailed Trade Buddy guide
4. **QUICKSTART.md** - This file

## 🎨 Theme Colors

The console theme uses these colors (customizable in `src/flux/theme.py`):

```python
CONSOLE_COLORS = {
    "primary": "#1a1a1a",      # Dark background
    "secondary": "#2d2d2d",    # Card backgrounds
    "accent": "#00d4ff",        # Cyan highlights
    "success": "#00ff88",       # Green success
    "warning": "#ffaa00",       # Orange warning
    "danger": "#ff4444",        # Red errors
    "text_primary": "#ffffff",  # White text
    "text_secondary": "#cccccc", # Gray text
}
```

## 🔗 Asset Links Reference

Quick access to example assets:

```python
from flux.assets import AssetLinks

# Example images
AssetLinks.GRID              # Main showcase grid
AssetLinks.DEV_GRID          # Dev model examples
AssetLinks.SCHNELL_GRID      # Schnell model examples
AssetLinks.KREA_GRID         # Krea model examples
AssetLinks.CUP               # Cup example
AssetLinks.CUP_MASK          # Cup mask
AssetLinks.ROBOT             # Robot image

# Documentation
AssetLinks.DOC_CANNY         # Canny edge detection
AssetLinks.DOC_DEPTH         # Depth conditioning
AssetLinks.DOC_INPAINTING    # Inpainting example
AssetLinks.DOC_KONTEXT       # Kontext example
AssetLinks.DOC_OUTPAINTING   # Outpainting example
AssetLinks.DOC_REDUX         # Redux example
```

## 💻 Code Examples

### Basic Trade Buddy Usage

```python
from flux.trade_buddy import TradeBuddy

# Initialize
buddy = TradeBuddy()

# Add a generation
gen = buddy.add_generation(
    image_path="output/image.jpg",
    prompt="a beautiful sunset",
    seed=12345,
    model="flux-schnell",
    width=1024,
    height=768,
    steps=4,
    guidance=3.5,
    tags=["sunset", "nature"]
)

# Search and filter
results = buddy.search_by_prompt("sunset")
tagged = buddy.search_by_tag("nature")
top = buddy.get_top_rated(10)

# Rate and organize
buddy.update_rating(gen.id, 5)
buddy.add_tags(gen.id, ["landscape", "sky"])
buddy.add_notes(gen.id, "Best sunset ever!")

# Get statistics
stats = buddy.get_stats()
print(f"Total images: {stats['total']}")
print(f"Average rating: {stats['avg_rating']}")
```

### Using Asset Catalog

```python
from flux.assets import AssetCatalog, AssetLinks

# Scan all assets
catalog = AssetCatalog()

# Get statistics
stats = catalog.get_stats()
print(f"Total assets: {stats['total_assets']}")
print(f"Total size: {stats['total_size_mb']} MB")

# Get assets by category
examples = catalog.get_assets_by_category("examples")
docs = catalog.get_assets_by_category("docs")

# Search
results = catalog.search_assets("grid")

# Use predefined links
grid_path = AssetLinks.GRID
cup_path = AssetLinks.CUP
```

### Using Prompt Library

```python
from flux.trade_buddy import PromptLibrary

library = PromptLibrary()

# Get categories
categories = library.get_categories()

# Get prompts by category
nature_prompts = library.get_by_category("nature")

# Fill a template
prompt = library.fill_template(
    "nature",
    subject="waterfall",
    environment="misty forest",
    lighting="golden hour",
    style="cinematic"
)
```

### Apply Theme to Custom Gradio App

```python
import gradio as gr
from flux.theme import get_gradio_theme, get_custom_css_for_gradio

theme = get_gradio_theme()
css = get_custom_css_for_gradio()

with gr.Blocks(theme=theme, css=css) as demo:
    gr.Markdown("# My FLUX App with Console Theme")
    # Your app here

demo.launch()
```

### Apply Theme to Custom Streamlit App

```python
import streamlit as st
from flux.theme import get_custom_css_for_streamlit

# Apply theme
st.markdown(get_custom_css_for_streamlit(), unsafe_allow_html=True)

st.title("🎨 My FLUX App")
st.markdown("*With Console Theme*")

# Your app here
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure proper installation
pip install -e ".[all]"

# Or install individually
pip install gradio streamlit torch pillow
```

### Theme Not Showing
- Clear browser cache
- Ensure latest gradio/streamlit versions
- Check console for CSS errors

### Assets Not Found
- Verify you're in the correct directory
- Check `assets/` folder exists
- Review ASSETS_README.md for paths

## 🎯 Tips for Best Results

1. **Start with Trade Buddy** - It's the most feature-complete
2. **Tag Consistently** - Develop a tagging system early
3. **Rate Images** - Helps find your best work later
4. **Use Prompt Library** - Build a collection of successful prompts
5. **Export Collections** - Backup your best work regularly
6. **Check Statistics** - Learn which settings work best

## 📚 Additional Resources

- **TRADE_BUDDY_GUIDE.md** - Complete guide with advanced features
- **ASSETS_README.md** - Full asset catalog
- **Main README.md** - FLUX setup and model information

## 🤝 Support

For issues or questions:
1. Check existing documentation
2. Review code comments
3. Open a GitHub issue
4. Contact repository maintainers

---

**🎉 Enjoy your enhanced FLUX experience with Trade Buddy!**

*Built with passion for the FLUX community* ❤️

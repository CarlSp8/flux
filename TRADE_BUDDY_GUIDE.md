# FLUX Trade Buddy - Complete Guide

## 🎨 What is Trade Buddy?

**Trade Buddy** is an advanced image generation management system built on top of FLUX. It transforms FLUX from a simple image generator into a professional creative studio with gallery management, asset organization, and a sleek console theme.

## ✨ Key Features

### 1. **Professional Console Theme**
- Dark theme with cyan accents for reduced eye strain
- Responsive design that works on desktop, tablet, and mobile
- Professional monospace fonts (JetBrains Mono)
- Smooth animations and hover effects
- Consistent styling across Gradio and Streamlit interfaces

### 2. **Image Gallery Management**
- Automatically saves all generations with metadata
- Rate images with 1-5 star system
- Tag and categorize your creations
- Search by prompt keywords
- Filter by tags
- Sort by date or rating
- View detailed statistics

### 3. **Asset Catalog System**
- Complete catalog of all FLUX example images
- Quick links to documentation assets
- Visual gallery browser
- File size information
- Direct file links for easy access

### 4. **Prompt Library**
- Pre-built prompt templates
- Organized by category (nature, portrait, abstract, etc.)
- Example prompts for inspiration
- Easy template filling system

### 5. **Advanced Generation Features**
- Save directly to gallery with custom tags
- Track generation statistics
- Compare multiple images
- Create comparison grids
- Suggest parameter variations

## 🚀 Getting Started

### Installation

No additional installation needed! The Trade Buddy system is integrated into the FLUX repository.

### Quick Start

#### Option 1: Trade Buddy Full Interface (Recommended)

```bash
python demo_trade_buddy.py --name flux-schnell
```

Features:
- Generation tab with prompt suggestions
- Gallery browser with search and filtering
- Statistics dashboard
- Asset catalog with all FLUX examples
- Console theme enabled

#### Option 2: Enhanced Classic Interface

The classic Gradio and Streamlit demos now include the console theme:

```bash
# Gradio with console theme
python demo_gr.py --name flux-schnell

# Streamlit with console theme
streamlit run demo_st.py -- --device cuda

# Streamlit Fill with console theme
streamlit run demo_st_fill.py -- --device cuda
```

## 📖 Usage Guide

### Generating Images

1. **Enter a prompt** - Describe what you want to generate
2. **Use prompt suggestions** - Select a category and click "Get Suggestions" for ideas
3. **Add tags** - Enter comma-separated tags (e.g., "landscape, nature, sunset")
4. **Configure parameters** - Adjust width, height, steps, guidance, seed
5. **Generate** - Click the "🚀 Generate Image" button
6. **Auto-save to gallery** - Images are automatically saved if checkbox is enabled

### Managing Your Gallery

#### Search and Filter
```
Search by prompt: Enter keywords from your prompts
Filter by tag: Enter a tag name to see all images with that tag
Sort: Choose "recent" or "top_rated"
```

#### Viewing Statistics
- Total images generated
- Average rating
- Models used breakdown
- Top tags
- Total storage used

### Using the Asset Catalog

The Asset Catalog provides quick access to all FLUX example images:

**Example Images:**
- Main Grid: `assets/grid.jpg`
- Dev Grid: `assets/dev_grid.jpg`
- Schnell Grid: `assets/schnell_grid.jpg`
- Krea Grid: `assets/flux-1-krea-dev-grid.png`
- Cup Example: `assets/cup.png`
- Cup Mask: `assets/cup_mask.png`
- Robot: `assets/robot.webp`

**Documentation Assets:**
- Canny Example: `assets/docs/canny.png`
- Depth Example: `assets/docs/depth.png`
- Inpainting Example: `assets/docs/inpainting.png`
- Kontext Example: `assets/docs/kontext.png`
- Outpainting Example: `assets/docs/outpainting.png`
- Redux Example: `assets/docs/redux.png`

See [ASSETS_README.md](ASSETS_README.md) for complete catalog.

## 🎯 Advanced Features

### Programmatic Usage

You can use Trade Buddy components in your own scripts:

```python
from flux.trade_buddy import TradeBuddy, PromptLibrary
from flux.assets import AssetCatalog, AssetLinks
from flux.theme import get_gradio_theme, get_streamlit_theme_config

# Initialize Trade Buddy
buddy = TradeBuddy()

# Add a generation
gen = buddy.add_generation(
    image_path="path/to/image.jpg",
    prompt="a beautiful landscape",
    seed=12345,
    model="flux-schnell",
    width=1024,
    height=768,
    steps=4,
    guidance=3.5,
    tags=["landscape", "nature"]
)

# Search images
results = buddy.search_by_prompt("landscape")
top_rated = buddy.get_top_rated(limit=10)

# Rate an image
buddy.update_rating(gen.id, rating=5)

# Use asset catalog
catalog = AssetCatalog()
all_assets = catalog.get_asset_links()
example_images = catalog.get_assets_by_category("examples")

# Access predefined assets
cup_image = AssetLinks.CUP
grid_image = AssetLinks.GRID

# Use prompt library
library = PromptLibrary()
nature_prompts = library.get_by_category("nature")
prompt = library.fill_template("nature", 
    subject="waterfall",
    environment="forest",
    lighting="golden hour",
    style="cinematic"
)
```

### Creating Comparison Grids

```python
from flux.trade_buddy import TradeBuddy

buddy = TradeBuddy()

# Get some generation IDs
recent = buddy.get_recent(limit=4)
gen_ids = [g.id for g in recent]

# Create comparison grid
buddy.create_comparison_grid(
    gen_ids=gen_ids,
    output_path="comparison.jpg",
    grid_cols=2
)
```

### Export/Import Collections

```python
# Export a collection by tag
buddy.export_collection(tag="landscapes", output_path="my_landscapes.json")

# Import into another instance
buddy2 = TradeBuddy()
buddy2.import_collection("my_landscapes.json")
```

## 🎨 Theme Customization

The console theme can be customized by modifying `src/flux/theme.py`:

```python
# Edit CONSOLE_COLORS dictionary
CONSOLE_COLORS = {
    "primary": "#1a1a1a",      # Dark background
    "secondary": "#2d2d2d",    # Slightly lighter
    "accent": "#00d4ff",        # Bright cyan - change this!
    "success": "#00ff88",       # Bright green
    # ... more colors
}
```

## 📁 File Structure

```
flux/
├── demo_trade_buddy.py          # Full Trade Buddy interface
├── demo_gr.py                   # Gradio demo with console theme
├── demo_st.py                   # Streamlit demo with console theme
├── demo_st_fill.py              # Streamlit fill demo with theme
├── ASSETS_README.md             # Complete asset catalog
├── TRADE_BUDDY_GUIDE.md         # This file
├── src/flux/
│   ├── theme.py                 # Theme configuration
│   ├── trade_buddy.py           # Gallery and library management
│   ├── assets.py                # Asset catalog system
│   └── ...
├── trade_buddy_gallery/         # Saved generations database
│   └── gallery.json
└── assets/                      # Example images
    ├── *.jpg, *.png, *.webp
    └── docs/
        └── *.png
```

## 🔧 Troubleshooting

### Gallery not saving
- Check that `save_to_gallery` checkbox is enabled
- Verify write permissions in the directory
- Check console for error messages

### Theme not loading
- Ensure you're using the latest versions of gradio/streamlit
- Try clearing browser cache
- Check import statements are correct

### Assets not displaying
- Verify asset files exist in `assets/` directory
- Check file permissions
- Ensure paths are correct in AssetLinks

## 💡 Tips & Best Practices

1. **Use Tags Consistently** - Develop a tagging system (e.g., "style:photorealistic", "subject:landscape")
2. **Rate as You Go** - Rate images immediately after generation
3. **Use Prompt Library** - Save successful prompts to the library
4. **Export Collections** - Regularly export your best work
5. **Check Statistics** - Use stats to track your most successful settings

## 🎯 Future Enhancements

Possible future additions:
- Image similarity search
- Automatic tag suggestions
- Batch generation with variations
- Collection sharing and collaboration
- Advanced comparison tools
- Prompt evolution tracking
- Style transfer between generations

## 📝 License

Trade Buddy is part of the FLUX repository and follows the same licensing as FLUX.

## 🤝 Contributing

To contribute improvements to Trade Buddy:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
- Check the main FLUX README.md
- Review ASSETS_README.md for asset questions
- Open an issue on GitHub

---

**Built with ❤️ for the FLUX community**

*Making AI image generation more organized, accessible, and beautiful.*

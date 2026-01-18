"""
Asset Manager for FLUX Trade Buddy
Centralized asset catalog with links, metadata, and management features.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class AssetCatalog:
    """
    Manages and catalogs all FLUX assets including:
    - Example images
    - Demo outputs
    - Documentation images
    - Reference images
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.assets = self._scan_assets()
    
    def _scan_assets(self) -> Dict[str, Dict]:
        """Scan and catalog all assets."""
        assets = {}
        
        # Define asset locations
        asset_dirs = {
            "examples": self.base_path / "assets",
            "docs": self.base_path / "assets" / "docs",
            "outputs": self.base_path / "output",
            "gallery": self.base_path / "trade_buddy_gallery",
        }
        
        for category, dir_path in asset_dirs.items():
            if dir_path.exists():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                        rel_path = file_path.relative_to(self.base_path)
                        asset_id = str(rel_path).replace(os.sep, "/")
                        
                        assets[asset_id] = {
                            "id": asset_id,
                            "name": file_path.name,
                            "path": str(file_path),
                            "relative_path": str(rel_path),
                            "category": category,
                            "size_bytes": file_path.stat().st_size,
                            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                            "extension": file_path.suffix,
                            "url": f"file://{file_path.absolute()}",
                            "web_url": f"/file={file_path.absolute()}",
                        }
        
        return assets
    
    def get_asset_links(self) -> Dict[str, str]:
        """Get all asset links as a dictionary."""
        return {asset_id: data["url"] for asset_id, data in self.assets.items()}
    
    def get_assets_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all assets in a specific category."""
        return {k: v for k, v in self.assets.items() if v["category"] == category}
    
    def get_asset(self, asset_id: str) -> Optional[Dict]:
        """Get a specific asset by ID."""
        return self.assets.get(asset_id)
    
    def search_assets(self, query: str) -> Dict[str, Dict]:
        """Search assets by name or path."""
        query_lower = query.lower()
        return {
            k: v for k, v in self.assets.items()
            if query_lower in k.lower() or query_lower in v["name"].lower()
        }
    
    def get_stats(self) -> Dict:
        """Get statistics about assets."""
        total_size = sum(asset["size_bytes"] for asset in self.assets.values())
        by_category = {}
        by_extension = {}
        
        for asset in self.assets.values():
            cat = asset["category"]
            ext = asset["extension"]
            
            by_category[cat] = by_category.get(cat, 0) + 1
            by_extension[ext] = by_extension.get(ext, 0) + 1
        
        return {
            "total_assets": len(self.assets),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_category": by_category,
            "by_extension": by_extension,
        }
    
    def export_catalog(self, output_path: str):
        """Export asset catalog to JSON."""
        with open(output_path, "w") as f:
            json.dump({
                "assets": self.assets,
                "stats": self.get_stats(),
            }, f, indent=2)
    
    def get_html_gallery(self, category: Optional[str] = None) -> str:
        """Generate HTML gallery view of assets."""
        assets_to_show = self.get_assets_by_category(category) if category else self.assets
        
        html = '''
        <style>
        .asset-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            padding: 15px;
            background: #1a1a1a;
        }
        .asset-card {
            background: #2d2d2d;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            color: #fff;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .asset-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
            border-color: #00d4ff;
        }
        .asset-img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        .asset-name {
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .asset-meta {
            font-size: 0.7em;
            color: #aaa;
        }
        .asset-category {
            display: inline-block;
            background: #00d4ff;
            color: #1a1a1a;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.75em;
            margin-top: 5px;
        }
        .asset-link {
            color: #00d4ff;
            text-decoration: none;
            font-size: 0.75em;
            display: block;
            margin-top: 5px;
        }
        .asset-link:hover {
            text-decoration: underline;
        }
        </style>
        <div class="asset-gallery">
        '''
        
        for asset_id, asset in list(assets_to_show.items())[:50]:  # Limit to 50 for performance
            html += f'''
            <div class="asset-card">
                <img src="{asset['web_url']}" class="asset-img" alt="{asset['name']}" onerror="this.style.display='none'">
                <div class="asset-name" title="{asset['name']}">{asset['name']}</div>
                <div class="asset-meta">
                    {asset['size_mb']} MB
                </div>
                <span class="asset-category">{asset['category']}</span>
                <a href="{asset['url']}" class="asset-link" target="_blank">🔗 Open</a>
            </div>
            '''
        
        html += '</div>'
        return html


class AssetLinks:
    """
    Quick access to commonly used asset links.
    """
    
    # Example images from assets/
    GRID = "assets/grid.jpg"
    DEV_GRID = "assets/dev_grid.jpg"
    SCHNELL_GRID = "assets/schnell_grid.jpg"
    KREA_GRID = "assets/flux-1-krea-dev-grid.png"
    CUP = "assets/cup.png"
    CUP_MASK = "assets/cup_mask.png"
    ROBOT = "assets/robot.webp"
    
    # Documentation images from assets/docs/
    DOC_CANNY = "assets/docs/canny.png"
    DOC_DEPTH = "assets/docs/depth.png"
    DOC_INPAINTING = "assets/docs/inpainting.png"
    DOC_KONTEXT = "assets/docs/kontext.png"
    DOC_OUTPAINTING = "assets/docs/outpainting.png"
    DOC_REDUX = "assets/docs/redux.png"
    
    @classmethod
    def get_all_links(cls) -> Dict[str, str]:
        """Get all predefined asset links."""
        return {
            "Example Images": {
                "Main Grid": cls.GRID,
                "Dev Grid": cls.DEV_GRID,
                "Schnell Grid": cls.SCHNELL_GRID,
                "Krea Grid": cls.KREA_GRID,
                "Cup Example": cls.CUP,
                "Cup Mask": cls.CUP_MASK,
                "Robot": cls.ROBOT,
            },
            "Documentation": {
                "Canny Example": cls.DOC_CANNY,
                "Depth Example": cls.DOC_DEPTH,
                "Inpainting Example": cls.DOC_INPAINTING,
                "Kontext Example": cls.DOC_KONTEXT,
                "Outpainting Example": cls.DOC_OUTPAINTING,
                "Redux Example": cls.DOC_REDUX,
            }
        }
    
    @classmethod
    def get_links_markdown(cls) -> str:
        """Get all links formatted as markdown."""
        md = "# FLUX Asset Links\n\n"
        
        for section, links in cls.get_all_links().items():
            md += f"## {section}\n\n"
            for name, path in links.items():
                md += f"- **{name}**: `{path}`\n"
            md += "\n"
        
        return md
    
    @classmethod
    def get_links_html(cls) -> str:
        """Get all links formatted as HTML."""
        html = '''
        <div style="background: #1a1a1a; color: #fff; padding: 20px; border-radius: 8px; font-family: 'JetBrains Mono', monospace;">
        <h2 style="color: #00d4ff; margin-bottom: 20px;">🔗 FLUX Asset Links</h2>
        '''
        
        for section, links in cls.get_all_links().items():
            html += f'<h3 style="color: #00ff88; margin-top: 20px; margin-bottom: 10px;">{section}</h3>'
            html += '<ul style="list-style: none; padding: 0;">'
            
            for name, path in links.items():
                full_path = os.path.abspath(path) if os.path.exists(path) else path
                html += f'''
                <li style="margin-bottom: 10px; padding: 10px; background: #2d2d2d; border-left: 3px solid #00d4ff; border-radius: 4px;">
                    <strong style="color: #00d4ff;">{name}</strong><br>
                    <code style="font-size: 0.85em; color: #ccc;">{path}</code><br>
                    <a href="file://{full_path}" style="color: #00ff88; text-decoration: none; font-size: 0.85em;" target="_blank">📂 Open File</a>
                </li>
                '''
            
            html += '</ul>'
        
        html += '</div>'
        return html
    
    @classmethod
    def get_links_json(cls) -> str:
        """Get all links as JSON string."""
        return json.dumps(cls.get_all_links(), indent=2)


def generate_asset_readme(output_path: str = "ASSETS_README.md"):
    """Generate a comprehensive README for all assets."""
    catalog = AssetCatalog()
    stats = catalog.get_stats()
    
    readme = f"""# FLUX Assets Catalog

This document catalogs all assets available in the FLUX repository.

## 📊 Statistics

- **Total Assets**: {stats['total_assets']}
- **Total Size**: {stats['total_size_mb']} MB
- **Categories**: {', '.join(stats['by_category'].keys())}
- **File Types**: {', '.join(stats['by_extension'].keys())}

## 📂 Asset Categories

"""
    
    for category, count in stats['by_category'].items():
        readme += f"### {category.upper()} ({count} files)\n\n"
        assets = catalog.get_assets_by_category(category)
        
        for asset_id, asset in list(assets.items())[:20]:  # Limit to 20 per category
            readme += f"- **{asset['name']}** ({asset['size_mb']} MB)\n"
            readme += f"  - Path: `{asset['relative_path']}`\n"
            readme += f"  - Link: `file://{asset['path']}`\n\n"
        
        if len(assets) > 20:
            readme += f"  ... and {len(assets) - 20} more files\n\n"
    
    readme += "\n## 🔗 Quick Links\n\n"
    readme += AssetLinks.get_links_markdown()
    
    readme += """
## 📝 Usage

### In Python:
```python
from flux.assets import AssetLinks, AssetCatalog

# Access predefined links
image_path = AssetLinks.GRID

# Scan all assets
catalog = AssetCatalog()
all_assets = catalog.get_asset_links()
```

### In Demos:
Assets are automatically available through the Trade Buddy interface.

---
*Generated by FLUX Trade Buddy Asset Manager*
"""
    
    with open(output_path, "w") as f:
        f.write(readme)
    
    return readme


if __name__ == "__main__":
    # Generate asset catalog
    catalog = AssetCatalog()
    
    print("=" * 60)
    print("FLUX ASSET CATALOG")
    print("=" * 60)
    
    stats = catalog.get_stats()
    print(f"\nTotal Assets: {stats['total_assets']}")
    print(f"Total Size: {stats['total_size_mb']} MB")
    print(f"\nBy Category:")
    for cat, count in stats['by_category'].items():
        print(f"  - {cat}: {count} files")
    
    print("\n" + "=" * 60)
    print("ASSET LINKS")
    print("=" * 60)
    print("\n" + AssetLinks.get_links_markdown())
    
    # Generate README
    print("\nGenerating ASSETS_README.md...")
    generate_asset_readme()
    print("✅ Done!")

# OpenWebUI Documentation - Complete Mirror

This directory contains a **complete offline mirror** of the OpenWebUI documentation with **full formatting intact**.

## 📊 Mirror Details

- **Source**: https://docs.openwebui.com/
- **Tool**: wget --mirror (complete site mirror)
- **Files**: 280+ files (28MB total)
- **Format**: Exact copy with all CSS, JS, images, and assets
- **Links**: All converted for offline viewing

## 🎨 What's Included

✅ **Complete CSS styling** - Looks identical to live site
✅ **JavaScript functionality** - Navigation, search, theme switching
✅ **All images and assets** - Screenshots, diagrams, logos
✅ **Responsive design** - Works on all screen sizes
✅ **Dark/light theme toggle** - Full theme support
✅ **Navigation sidebar** - Collapsible menu structure
✅ **Search functionality** - Built-in doc search
✅ **All internal links** - Converted to work offline

## 🚀 How to Use

1. **Open the main page**: `openwebui-docs/docs.openwebui.com/index.html`
2. **Navigate freely**: All links work offline
3. **Use search**: The search bar functions locally
4. **Switch themes**: Dark/light mode toggle works
5. **Browse sidebar**: Expand/collapse navigation sections

## 📁 Structure

```
openwebui-docs/
└── docs.openwebui.com/
    ├── index.html              # Home page
    ├── getting-started/        # Installation guides
    ├── features/              # Feature documentation
    ├── tutorials/             # How-to guides
    ├── troubleshooting/       # Problem solving
    ├── assets/                # CSS, JS, images
    │   ├── css/
    │   ├── js/
    │   └── images/
    └── sponsors/              # Sponsor banners
```

## 🔧 Technical Notes

- **Framework**: Docusaurus v3.5.2
- **Styling**: Custom CSS with theme support
- **Assets**: All external resources downloaded locally
- **Links**: Converted from absolute to relative paths
- **Compatibility**: Works in any modern web browser

## 📝 Update Instructions

To update this mirror in the future:

```bash
cd /home/stacy/AlphaOmega
rm -rf openwebui-docs/
mkdir -p openwebui-docs

wget --mirror \
     --convert-links \
     --adjust-extension \
     --page-requisites \
     --no-parent \
     --execute robots=off \
     --wait=1 \
     --random-wait \
     --no-check-certificate \
     --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
     -P openwebui-docs \
     https://docs.openwebui.com/
```

---

*This mirror was created using wget --mirror for complete offline documentation access.*</content>
<parameter name="filePath">/home/stacy/AlphaOmega/openwebui-docs/README.md
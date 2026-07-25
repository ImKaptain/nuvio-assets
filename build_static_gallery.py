import os
import json
import re
from PIL import Image

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ImKaptain/nuvio-assets/main"

def classify_asset_type(root_folder, file_path):
    """Strictly classifies an asset into 'covers', 'backdrops', 'logos', or 'ignore'."""
    lower_path = file_path.lower()
    lower_root = root_folder.lower()
    filename = lower_path.split('/')[-1]
    
    # User requested: Collection_Cards should not show in gallery
    if lower_root == 'collection_cards' or 'collection_cards' in lower_path:
        return 'ignore'
        
    if 'titlelogos' in lower_root or 'logo' in lower_path:
        return 'logos'
        
    # International Cinema cards have Outline, Hybrid, FilmStripFlag, FilmStripHybrid, Flag, Poster styles
    if lower_root == 'international cinema' or 'international cinema' in lower_path:
        if 'background' in lower_path or 'backdrop' in lower_path or 'wallpaper' in lower_path:
            return 'backdrops'
        return 'covers'
        
    # Regex check for T1, T2, T3, T4, T5 collage variations (e.g. T1_1080p, T2_4K, _T1_)
    is_t_backdrop = bool(re.search(r'(^|[\b_])t[1-9]([\b_.]|\d)', filename))
        
    # Strict backdrop, collage, banner, and variant keywords
    backdrop_keywords = [
        'opt0', 'opt1', 'opt2', 'opt3', 'option', 'variant', 'collage',
        'wallpaper', 'background', 'backdrop', 'prism', 'hero', 'banner', 'fanart'
    ]
    
    is_backdrop_keyword = any(k in lower_path for k in backdrop_keywords)
    
    if (lower_root.startswith('nuvio_backdrops_') or 
        lower_root == 'collections' or 
        lower_root == 'external_cache' or 
        'backdrop' in lower_root or 
        'background' in lower_root or 
        is_t_backdrop or 
        is_backdrop_keyword):
        return 'backdrops'
    else:
        return 'covers'

def get_image_dimensions(full_path):
    """Reads image dimensions and computes orientation & aspect ratio."""
    try:
        with Image.open(full_path) as img:
            w, h = img.size
            ratio = round(w / h, 3)
            if h > w * 1.1:
                orientation = 'portrait'
            elif w > h * 1.1:
                orientation = 'landscape'
            else:
                orientation = 'square'
            return w, h, ratio, orientation
    except Exception:
        return 1920, 1080, 1.778, 'landscape'

def scan_assets():
    """Scans all folders in nuvio-assets and organizes them strictly into clean asset types with orientation data."""
    assets = []
    ignore_dirs = {'.git', '.github', 'nuvio-share-hub', 'scratch', 'assets', 'Collection_Cards'}
    
    for root, dirs, files in os.walk(ASSET_DIR):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        rel_root = os.path.relpath(root, ASSET_DIR)
        if rel_root == '.':
            continue
            
        parts = rel_root.replace('\\', '/').split('/')
        category = parts[0]
        subfolder = parts[1] if len(parts) > 1 else ""
        is_gallery = "Gallery" in parts
        
        grouped = {}
        for f in files:
            if not (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.gif')):
                continue
                
            full_file_path = os.path.join(root, f)
            rel_file_path = os.path.join(rel_root, f).replace('\\', '/')
            raw_url = f"{GITHUB_RAW_BASE}/{rel_file_path.replace(' ', '%20')}"
            
            asset_type = classify_asset_type(category, rel_file_path)
            if asset_type == 'ignore':
                continue
                
            # Determine clean name
            clean_name = f
            for suffix in ['_Base_Dynamic.png', '_Hover_Dynamic.gif', '_Base.png', '_Hover.gif', '.png', '.jpg', '.gif']:
                if clean_name.endswith(suffix):
                    clean_name = clean_name[:-len(suffix)]
                    break
                    
            item_key = f"{rel_root}/{clean_name}"
            
            if item_key not in grouped:
                w, h, ratio, orientation = get_image_dimensions(full_file_path)
                grouped[item_key] = {
                    'id': f"{category}_{subfolder}_{clean_name}".replace(' ', '_'),
                    'title': clean_name.replace('_', ' '),
                    'type': asset_type,  # 'covers' | 'backdrops' | 'logos'
                    'category': category,
                    'subfolder': subfolder,
                    'is_gallery': is_gallery,
                    'is_dynamic': '_Dynamic' in f,
                    'base_url': None,
                    'hover_url': None,
                    'file_path': rel_file_path,
                    'width': w,
                    'height': h,
                    'aspect_ratio': ratio,
                    'orientation': orientation
                }
                
            if f.endswith(('Base.png', 'Base_Dynamic.png', '.png', '.jpg')):
                if not grouped[item_key]['base_url'] or '_Dynamic' in f:
                    grouped[item_key]['base_url'] = raw_url
            if f.endswith(('Hover.gif', 'Hover_Dynamic.gif', '.gif')):
                if not grouped[item_key]['hover_url'] or '_Dynamic' in f:
                    grouped[item_key]['hover_url'] = raw_url
                    
        for item in grouped.values():
            if item['base_url']:
                assets.append(item)
                
    # Sort ALL assets alphabetically by title for a diverse, rich mix
    assets.sort(key=lambda x: x['title'].lower())
    return assets

def generate_gallery_html(assets):
    manifest_json = json.dumps(assets, indent=2)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JUST GIVE ME THE F*CKING ASSETS • Nuvio Art Portfolio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-main: #ffffff;
      --bg-card: #f9fafb;
      --text-main: #000000;
      --text-muted: #6b7280;
      --border: #e5e7eb;
      --accent: #000000;
      --accent-purple: #8b5cf6;
      --radius: 10px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
    }}

    /* --- EDITORIAL HEADER BAR --- */
    header {{
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
    }}

    .header-top {{
      max-width: 1600px;
      margin: 0 auto;
      padding: 0.85rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1.5rem;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }}

    .brand-asterisk {{
      font-size: 2rem;
      font-weight: 900;
      line-height: 1;
      text-decoration: none;
      color: #000;
      transition: transform 0.3s ease;
    }}

    .brand-asterisk:hover {{
      transform: rotate(90deg);
    }}

    /* CATEGORIES DROPDOWN MENU */
    .dropdown-container {{
      position: relative;
    }}

    .cat-dropdown-btn {{
      background: transparent;
      border: none;
      font-family: 'Outfit', sans-serif;
      font-size: 0.88rem;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: #000;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.4rem 0.6rem;
      border-radius: 4px;
      transition: background 0.2s;
    }}

    .cat-dropdown-btn:hover {{
      background: #f3f4f6;
    }}

    .cat-menu {{
      position: absolute;
      top: 100%;
      left: 0;
      margin-top: 0.4rem;
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.12);
      width: 220px;
      display: none;
      flex-direction: column;
      padding: 0.4rem 0;
      z-index: 200;
    }}

    .cat-menu.open {{
      display: flex;
    }}

    .cat-item {{
      background: transparent;
      border: none;
      text-align: left;
      padding: 0.6rem 1rem;
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 700;
      color: #374151;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.15s ease;
    }}

    .cat-item:hover, .cat-item.active {{
      background: #000;
      color: #fff;
    }}

    .browse-all-btn {{
      background: #000000;
      color: #ffffff;
      border: none;
      font-family: 'Outfit', sans-serif;
      font-size: 0.82rem;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      padding: 0.5rem 1.1rem;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.2s ease;
    }}

    .browse-all-btn:hover {{
      background: #333333;
    }}

    .header-center {{
      flex: 1;
      max-width: 480px;
    }}

    .search-box {{
      position: relative;
      width: 100%;
    }}

    .search-box input {{
      width: 100%;
      background: #ffffff;
      border: 1px solid var(--border);
      color: #000;
      padding: 0.55rem 1rem 0.55rem 2.4rem;
      border-radius: 4px;
      font-size: 0.88rem;
      outline: none;
      transition: border-color 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: #000;
    }}

    .search-icon {{
      position: absolute;
      left: 0.85rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .stat-pill {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.8rem;
      font-weight: 800;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      border: 1px solid var(--border);
      padding: 0.4rem 0.8rem;
      border-radius: 4px;
    }}

    /* --- MASSIVE STATEMENT HERO --- */
    .hero-statement {{
      text-align: center;
      padding: 3.5rem 1.5rem 2rem;
      max-width: 1100px;
      margin: 0 auto;
    }}

    .hero-title {{
      font-family: 'Outfit', sans-serif;
      font-size: clamp(2.4rem, 6vw, 4.2rem);
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: -1.5px;
      line-height: 0.95;
      color: #000000;
      margin-bottom: 1.5rem;
    }}

    .sub-filter-bar {{
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 1rem;
    }}

    .sub-btn {{
      background: #ffffff;
      border: 1px solid var(--border);
      color: #374151;
      padding: 0.4rem 0.95rem;
      border-radius: 20px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .sub-btn:hover, .sub-btn.active {{
      background: #000000;
      color: #ffffff;
      border-color: #000000;
    }}

    /* --- MAIN CONTENT & GRID --- */
    main {{
      max-width: 1600px;
      margin: 1rem auto 3rem;
      padding: 0 2rem;
      flex-grow: 1;
      width: 100%;
    }}

    .section-label {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 800;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 1.2rem;
    }}

    /* EDITORIAL MASONRY GRID */
    .masonry-grid {{
      column-count: 4;
      column-gap: 1.25rem;
    }}

    @media (max-width: 1400px) {{
      .masonry-grid {{ column-count: 3; }}
    }}
    @media (max-width: 900px) {{
      .masonry-grid {{ column-count: 2; }}
    }}
    @media (max-width: 500px) {{
      .masonry-grid {{ column-count: 1; }}
    }}

    /* EDITORIAL CARD DESIGN */
    .photo-card {{
      break-inside: avoid;
      margin-bottom: 1.25rem;
      position: relative;
      background: #f9fafb;
      border-radius: var(--radius);
      overflow: hidden;
      cursor: pointer;
      border: 1px solid var(--border);
      transition: transform 0.25s ease, box-shadow 0.25s ease;
      width: 100%;
    }}

    .photo-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
      border-color: #000000;
    }}

    .photo-card img {{
      width: 100%;
      height: auto;
      display: block;
      transition: opacity 0.3s ease;
    }}

    /* HOVER OVERLAY (DUAL COPY BUTTONS & DETAILS) */
    .hover-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.82) 70%, rgba(0,0,0,0.92) 100%);
      opacity: 0;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 1rem;
      transition: opacity 0.25s ease;
      z-index: 20;
    }}

    .photo-card:hover .hover-overlay {{
      opacity: 1;
    }}

    .overlay-top {{
      display: flex;
      justify-content: flex-end;
    }}

    .overlay-tag {{
      background: rgba(255, 255, 255, 0.95);
      color: #000;
      font-family: 'Outfit', sans-serif;
      font-size: 0.72rem;
      font-weight: 800;
      padding: 0.25rem 0.6rem;
      border-radius: 4px;
      text-transform: uppercase;
    }}

    .dynamic-tag {{
      background: #10b981;
      color: #fff;
    }}

    .overlay-bottom {{
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}

    .card-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.05rem;
      font-weight: 800;
      color: #ffffff;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .card-sub {{
      font-size: 0.78rem;
      color: #d1d5db;
    }}

    .dual-copy-group {{
      display: flex;
      gap: 0.4rem;
    }}

    .copy-btn-sm {{
      flex: 1;
      background: #ffffff;
      color: #000000;
      border: none;
      padding: 0.45rem 0.6rem;
      border-radius: 4px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.75rem;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.3rem;
      transition: all 0.2s ease;
      white-space: nowrap;
    }}

    .copy-btn-sm:hover {{
      background: #000000;
      color: #ffffff;
    }}

    .copy-btn-sm.copied {{
      background: #10b981;
      color: #ffffff;
    }}

    /* --- LIGHTBOX DETAIL MODAL --- */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }}

    .modal-backdrop.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .modal-card {{
      background: #ffffff;
      border-radius: 12px;
      max-width: 1050px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      display: grid;
      grid-template-columns: 1fr 360px;
      position: relative;
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
    }}

    @media (max-width: 900px) {{
      .modal-card {{ grid-template-columns: 1fr; }}
    }}

    .modal-close {{
      position: absolute;
      top: 1rem;
      right: 1rem;
      width: 36px;
      height: 36px;
      background: #f3f4f6;
      border: 1px solid var(--border);
      color: #000;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.1rem;
      font-weight: 900;
      z-index: 20;
      transition: background 0.2s ease;
    }}

    .modal-close:hover {{
      background: #000;
      color: #fff;
    }}

    .modal-image-area {{
      background: #f9fafb;
      padding: 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      border-right: 1px solid var(--border);
    }}

    .modal-image-area img {{
      max-width: 100%;
      max-height: 65vh;
      object-fit: contain;
      border-radius: 6px;
    }}

    .view-toggle-bar {{
      margin-top: 1rem;
      display: flex;
      gap: 0.4rem;
      background: #e5e7eb;
      padding: 0.25rem;
      border-radius: 6px;
    }}

    .view-toggle-btn {{
      background: transparent;
      border: none;
      color: #4b5563;
      padding: 0.3rem 0.8rem;
      border-radius: 4px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.78rem;
      font-weight: 800;
      cursor: pointer;
    }}

    .view-toggle-btn.active {{
      background: #000000;
      color: #ffffff;
    }}

    .modal-info-area {{
      padding: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }}

    .modal-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.4rem;
      font-weight: 900;
      color: #000;
    }}

    .modal-meta-list {{
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .copy-section {{
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}

    .modal-copy-btn {{
      background: #000000;
      color: #ffffff;
      border: none;
      padding: 0.75rem 1rem;
      border-radius: 6px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: background 0.2s ease;
    }}

    .modal-copy-btn:hover {{
      background: #333333;
    }}

    .modal-copy-btn.copied {{
      background: #10b981;
      color: #ffffff;
    }}

    .related-section {{
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
    }}

    .related-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
    }}

    .related-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.6rem;
    }}

    .related-thumb {{
      aspect-ratio: 16/9;
      background: #f3f4f6;
      border-radius: 6px;
      overflow: hidden;
      cursor: pointer;
      border: 1px solid var(--border);
      transition: all 0.2s ease;
    }}

    .related-thumb:hover {{
      border-color: #000;
      transform: scale(1.04);
    }}

    .related-thumb img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    footer {{
      border-top: 1px solid var(--border);
      padding: 2.5rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
      margin-top: 3rem;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-top">
      <div class="header-left">
        <a href="#" class="brand-asterisk" title="Nuvio Art">✳</a>
        <div class="dropdown-container">
          <button class="cat-dropdown-btn" id="catDropdownBtn">
            CATEGORIES <span style="font-size:0.7rem">▼</span>
          </button>
          <div class="cat-menu" id="catMenu">
            <button class="cat-item active" data-type="covers">🎨 Covers <span id="badgeCovers">0</span></button>
            <button class="cat-item" data-type="backdrops">🖼️ Hero Backdrops <span id="badgeBackdrops">0</span></button>
            <button class="cat-item" data-type="logos">🏷️ Title Logos <span id="badgeLogos">0</span></button>
            <button class="cat-item" data-type="archive">📸 Gallery Archive <span id="badgeArchive">0</span></button>
          </div>
        </div>
        <button class="browse-all-btn" id="browseAllBtn">BROWSE ALL</button>
      </div>

      <div class="header-center">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" placeholder="Search covers & assets...">
        </div>
      </div>

      <div class="header-right">
        <span class="stat-pill" id="statPill">868 ASSETS</span>
      </div>
    </div>
  </header>

  <!-- MASSIVE STATEMENT HERO -->
  <section class="hero-statement">
    <h1 class="hero-title">JUST GIVE ME THE<br>F*CKING ASSETS</h1>
    
    <!-- SUB-FILTER PILLS FOR COVERS -->
    <div class="sub-filter-bar" id="subFilterBar">
      <button class="sub-btn active" data-sub="all">All Covers</button>
      <button class="sub-btn" data-sub="Genres">Genres</button>
      <button class="sub-btn" data-sub="Moods">Moods & Vibes</button>
      <button class="sub-btn" data-sub="Actors">Actors & Directors</button>
      <button class="sub-btn" data-sub="Streaming Services">Streaming & Networks</button>
      <button class="sub-btn" data-sub="International Cinema">International Cinema</button>
    </div>
  </section>

  <main>
    <div class="section-label" id="sectionLabel">LATEST COVERS (SHOWING 0)</div>
    <div class="masonry-grid" id="galleryGrid"></div>
  </main>

  <!-- LIGHTBOX DETAIL MODAL -->
  <div class="modal-backdrop" id="detailModal">
    <div class="modal-card">
      <button class="modal-close" id="modalClose">✕</button>
      <div class="modal-image-area">
        <img id="modalPreviewImg" src="" alt="Preview">
        <div class="view-toggle-bar">
          <button class="view-toggle-btn active" id="togglePngBtn">Base PNG</button>
          <button class="view-toggle-btn" id="toggleGifBtn">Focus GIF</button>
        </div>
      </div>
      <div class="modal-info-area">
        <div>
          <div class="modal-title" id="modalTitle">Title</div>
          <div class="modal-meta-list">
            <span id="modalMetaCategory">Category</span>
            <span id="modalMetaDimensions">Dimensions</span>
          </div>
        </div>

        <div class="copy-section">
          <button class="modal-copy-btn" id="modalCopyPngBtn">
            <span>📋 Copy Base PNG URL</span>
          </button>
          <button class="modal-copy-btn" id="modalCopyGifBtn">
            <span>✨ Copy Focus GIF URL</span>
          </button>
        </div>

        <div class="related-section" id="relatedSection">
          <div class="related-title">Card Variations & Style Options</div>
          <div class="related-grid" id="relatedGrid"></div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    <p>Nuvio Mega Collection • Official Asset Portfolio hosted on GitHub Pages</p>
  </footer>

  <script>
    const ASSETS = {manifest_json};

    let activeType = 'covers';  // 'covers' | 'backdrops' | 'logos' | 'archive'
    let activeSub = 'all';     // sub-filter for covers
    let activeModalItem = null;

    const grid = document.getElementById('galleryGrid');
    const searchInput = document.getElementById('searchInput');
    const sectionLabel = document.getElementById('sectionLabel');
    const catDropdownBtn = document.getElementById('catDropdownBtn');
    const catMenu = document.getElementById('catMenu');
    const browseAllBtn = document.getElementById('browseAllBtn');
    const catItems = document.querySelectorAll('.cat-item');
    const subBtns = document.querySelectorAll('.sub-btn');
    const subFilterBar = document.getElementById('subFilterBar');

    // Modal elements
    const detailModal = document.getElementById('detailModal');
    const modalClose = document.getElementById('modalClose');
    const modalPreviewImg = document.getElementById('modalPreviewImg');
    const modalTitle = document.getElementById('modalTitle');
    const modalMetaCategory = document.getElementById('modalMetaCategory');
    const modalMetaDimensions = document.getElementById('modalMetaDimensions');
    const modalCopyPngBtn = document.getElementById('modalCopyPngBtn');
    const modalCopyGifBtn = document.getElementById('modalCopyGifBtn');
    const togglePngBtn = document.getElementById('togglePngBtn');
    const toggleGifBtn = document.getElementById('toggleGifBtn');
    const relatedSection = document.getElementById('relatedSection');
    const relatedGrid = document.getElementById('relatedGrid');

    // Update Counts
    const coversCount = ASSETS.filter(a => a.type === 'covers' && !a.is_gallery).length;
    const backdropsCount = ASSETS.filter(a => a.type === 'backdrops' && !a.is_gallery).length;
    const logosCount = ASSETS.filter(a => a.type === 'logos').length;
    const archiveCount = ASSETS.filter(a => a.is_gallery).length;

    document.getElementById('badgeCovers').textContent = `(${{coversCount}})`;
    document.getElementById('badgeBackdrops').textContent = `(${{backdropsCount}})`;
    document.getElementById('badgeLogos').textContent = `(${{logosCount}})`;
    document.getElementById('badgeArchive').textContent = `(${{archiveCount}})`;
    document.getElementById('statPill').textContent = `${{ASSETS.length}} ASSETS`;

    // Category Dropdown Toggle
    catDropdownBtn.addEventListener('click', (e) => {{
      e.stopPropagation();
      catMenu.classList.toggle('open');
    }});

    document.addEventListener('click', () => catMenu.classList.remove('open'));

    // Browse All Reset
    browseAllBtn.addEventListener('click', () => {{
      activeType = 'covers';
      activeSub = 'all';
      searchInput.value = '';
      catItems.forEach(i => i.classList.remove('active'));
      document.querySelector('[data-type="covers"]').classList.add('active');
      subBtns.forEach(b => b.classList.remove('active'));
      document.querySelector('[data-sub="all"]').classList.add('active');
      subFilterBar.style.display = 'flex';
      renderGrid();
    }});

    function renderGrid() {{
      const query = searchInput.value.toLowerCase().trim();
      
      const filtered = ASSETS.filter(item => {{
        const matchesSearch = item.title.toLowerCase().includes(query) || 
                              item.category.toLowerCase().includes(query) || 
                              (item.subfolder && item.subfolder.toLowerCase().includes(query));
                              
        if (!matchesSearch) return false;

        // Archive Tab
        if (activeType === 'archive') return item.is_gallery;
        if (item.is_gallery) return false;

        // Backdrops Tab
        if (activeType === 'backdrops') return item.type === 'backdrops';
        
        // Logos Tab
        if (activeType === 'logos') return item.type === 'logos';
        
        // Covers Tab
        if (activeType === 'covers') {{
          if (item.type !== 'covers') return false;
          if (activeSub === 'all') return true;
          if (activeSub === 'Actors') return item.category === 'Actors' || item.category === 'Directors';
          if (activeSub === 'International Cinema') return item.category === 'International Cinema';
          if (activeSub === 'Streaming Services') {{
            const cat = item.category.toLowerCase();
            const sub = (item.subfolder || '').toLowerCase();
            const title = item.title.toLowerCase();
            if (['streaming services', 'general_cards', 'trending _ new', 'misc'].includes(cat)) return true;
            return ['streaming', 'network', 'bravo', 'channel 4', 'comedy central', 'disney', 'hgtv', 'mtv', 'pbs', 'syfy', 'tlc', 'tnt', 'mubi', 'cannes', 'academy', 'globes'].some(k => title.includes(k) || sub.includes(k));
          }}
          return item.category === activeSub;
        }}

        return true;
      }});

      // SORT ALPHABETICALLY BY TITLE
      filtered.sort((a, b) => a.title.localeCompare(b.title, undefined, {{ sensitivity: 'base' }}));

      let typeName = activeType.toUpperCase();
      if (activeType === 'covers' && activeSub !== 'all') typeName = activeSub.toUpperCase();
      sectionLabel.textContent = `LATEST ${{typeName}} (SHOWING ${{filtered.length}})`;
      grid.innerHTML = '';

      filtered.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'photo-card';

        const baseSrc = item.base_url;
        const hoverSrc = item.hover_url || item.base_url;

        let badgeText = item.category;
        if (item.is_dynamic) badgeText = '⚡ Dynamic';
        else if (item.is_gallery) badgeText = '📸 Archive';

        card.innerHTML = `
          <img src="${{baseSrc}}" alt="${{item.title}}" loading="lazy">
          <div class="hover-overlay">
            <div class="overlay-top">
              <span class="overlay-tag ${{item.is_dynamic ? 'dynamic-tag' : ''}}">${{badgeText}}</span>
            </div>
            <div class="overlay-bottom">
              <div>
                <div class="card-title">${{item.title}}</div>
                <div class="card-sub">${{item.category}} ${{item.subfolder ? '• ' + item.subfolder : ''}}</div>
              </div>
              <div class="dual-copy-group">
                <button class="copy-btn-sm copy-png-btn" data-url="${{baseSrc}}">
                  <span>📋 PNG</span>
                </button>
                ${{item.hover_url ? `<button class="copy-btn-sm copy-gif-btn" data-url="${{item.hover_url}}"><span>✨ GIF</span></button>` : ''}}
              </div>
            </div>
          </div>
        `;

        const img = card.querySelector('img');
        card.addEventListener('mouseenter', () => {{
          if (item.hover_url) img.src = hoverSrc;
        }});
        card.addEventListener('mouseleave', () => {{
          img.src = baseSrc;
        }});

        // Copy PNG button
        const copyPngBtn = card.querySelector('.copy-png-btn');
        if (copyPngBtn) {{
          copyPngBtn.addEventListener('click', (e) => {{
            e.stopPropagation();
            navigator.clipboard.writeText(baseSrc);
            copyPngBtn.classList.add('copied');
            copyPngBtn.querySelector('span').textContent = '✓ Copied!';
            setTimeout(() => {{
              copyPngBtn.classList.remove('copied');
              copyPngBtn.querySelector('span').textContent = '📋 PNG';
            }}, 2000);
          }});
        }}

        // Copy GIF button
        const copyGifBtn = card.querySelector('.copy-gif-btn');
        if (copyGifBtn) {{
          copyGifBtn.addEventListener('click', (e) => {{
            e.stopPropagation();
            navigator.clipboard.writeText(item.hover_url);
            copyGifBtn.classList.add('copied');
            copyGifBtn.querySelector('span').textContent = '✓ Copied!';
            setTimeout(() => {{
              copyGifBtn.classList.remove('copied');
              copyGifBtn.querySelector('span').textContent = '✨ GIF';
            }}, 2000);
          }});
        }}

        // Open Detail Modal on Card Click
        card.addEventListener('click', () => {{
          openModal(item);
        }});

        grid.appendChild(card);
      }});
    }}

    function openModal(item) {{
      activeModalItem = item;
      modalTitle.textContent = item.title;
      modalMetaCategory.textContent = `Category: ${{item.category}} ${{item.subfolder ? '• ' + item.subfolder : ''}}`;
      modalMetaDimensions.textContent = `Dimensions: ${{item.width}} x ${{item.height}} (${{item.orientation}})`;
      modalPreviewImg.src = item.base_url;

      togglePngBtn.classList.add('active');
      toggleGifBtn.classList.remove('active');

      if (item.hover_url) {{
        toggleGifBtn.style.display = 'inline-block';
        modalCopyGifBtn.style.display = 'flex';
      }} else {{
        toggleGifBtn.style.display = 'none';
        modalCopyGifBtn.style.display = 'none';
      }}

      // Populate Related Variations
      relatedGrid.innerHTML = '';
      const rawFolder = (item.subfolder || item.title).toLowerCase();
      const targetCat = item.category.toLowerCase();
      const cleanCountry = rawFolder.replace('filmstripflag', '').replace('filmstriphybrid', '').replace('flag', '').replace('hybrid', '').replace('outline', '').replace('poster', '').trim();

      const related = ASSETS.filter(a => {{
        if (a.id === item.id) return false;
        if (a.category.toLowerCase() !== targetCat) return false;
        if (a.type !== item.type) return false;
        const aFolder = (a.subfolder || a.title).toLowerCase();
        return aFolder.includes(cleanCountry) || a.file_path.toLowerCase().includes('/' + cleanCountry + '/');
      }}).slice(0, 8);

      if (related.length === 0) {{
        relatedSection.style.display = 'none';
      }} else {{
        relatedSection.style.display = 'flex';
        related.forEach(rel => {{
          const thumb = document.createElement('div');
          thumb.className = 'related-thumb';
          thumb.title = rel.title;
          thumb.innerHTML = `<img src="${{rel.base_url}}" alt="${{rel.title}}">`;
          thumb.addEventListener('click', () => openModal(rel));
          relatedGrid.appendChild(thumb);
        }});
      }}

      detailModal.classList.add('open');
    }}

    modalClose.addEventListener('click', () => detailModal.classList.remove('open'));
    detailModal.addEventListener('click', (e) => {{
      if (e.target === detailModal) detailModal.classList.remove('open');
    }});

    togglePngBtn.addEventListener('click', () => {{
      if (activeModalItem) {{
        modalPreviewImg.src = activeModalItem.base_url;
        togglePngBtn.classList.add('active');
        toggleGifBtn.classList.remove('active');
      }}
    }});

    toggleGifBtn.addEventListener('click', () => {{
      if (activeModalItem && activeModalItem.hover_url) {{
        modalPreviewImg.src = activeModalItem.hover_url;
        toggleGifBtn.classList.add('active');
        togglePngBtn.classList.remove('active');
      }}
    }});

    modalCopyPngBtn.addEventListener('click', () => {{
      if (activeModalItem) {{
        navigator.clipboard.writeText(activeModalItem.base_url);
        modalCopyPngBtn.classList.add('copied');
        modalCopyPngBtn.querySelector('span').textContent = '✓ Copied Base PNG!';
        setTimeout(() => {{
          modalCopyPngBtn.classList.remove('copied');
          modalCopyPngBtn.querySelector('span').textContent = '📋 Copy Base PNG URL';
        }}, 2000);
      }}
    }});

    modalCopyGifBtn.addEventListener('click', () => {{
      if (activeModalItem && activeModalItem.hover_url) {{
        navigator.clipboard.writeText(activeModalItem.hover_url);
        modalCopyGifBtn.classList.add('copied');
        modalCopyGifBtn.querySelector('span').textContent = '✓ Copied Focus GIF!';
        setTimeout(() => {{
          modalCopyGifBtn.classList.remove('copied');
          modalCopyGifBtn.querySelector('span').textContent = '✨ Copy Focus GIF URL';
        }}, 2000);
      }}
    }});

    catItems.forEach(item => {{
      item.addEventListener('click', () => {{
        catItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        activeType = item.dataset.type;
        catMenu.classList.remove('open');

        if (activeType === 'covers') {{
          subFilterBar.style.display = 'flex';
        }} else {{
          subFilterBar.style.display = 'none';
        }}
        renderGrid();
      }});
    }});

    subBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        subBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeSub = btn.dataset.sub;
        renderGrid();
      }});
    }});

    searchInput.addEventListener('input', renderGrid);

    renderGrid();
  </script>
</body>
</html>
"""
    return html

def main():
    print("Scanning nuvio-assets directory...")
    assets = scan_assets()
    print(f"Scanned {len(assets)} unique asset sets.")
    
    html = generate_gallery_html(assets)
    out_file = os.path.join(ASSET_DIR, 'index.html')
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Successfully generated clean Bold Editorial Recipe-Inspired Portfolio HTML at: {out_file}")

if __name__ == '__main__':
    main()

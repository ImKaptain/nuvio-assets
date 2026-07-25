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
  <title>Kaptain's Mega Collection of Assets • Official Portfolio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #09090b;
      --bg-header: rgba(9, 9, 11, 0.92);
      --bg-card: #121218;
      --accent: #ffffff;
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --border: rgba(255, 255, 255, 0.1);
      --radius: 12px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
    }}

    /* --- SLEEK HEADER BAR --- */
    header {{
      background: var(--bg-header);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
    }}

    .header-top {{
      max-width: 1600px;
      margin: 0 auto;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1.5rem;
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      text-decoration: none;
      color: var(--text-main);
    }}

    .brand-badge {{
      width: 36px;
      height: 36px;
      background: #ffffff;
      color: #000000;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-family: 'Outfit', sans-serif;
      font-size: 1.1rem;
    }}

    .brand-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.15rem;
      font-weight: 800;
      letter-spacing: -0.3px;
      color: #ffffff;
    }}

    /* HEADER PRIMARY TABS */
    .primary-nav {{
      display: flex;
      gap: 0.4rem;
    }}

    .nav-tab {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      font-family: 'Outfit', sans-serif;
      font-size: 0.88rem;
      font-weight: 700;
      padding: 0.5rem 1rem;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s ease;
    }}

    .nav-tab:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.06);
    }}

    .nav-tab.active {{
      color: #000000;
      background: #ffffff;
      border-color: #ffffff;
    }}

    .nav-badge {{
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-muted);
      font-size: 0.72rem;
      padding: 0.15rem 0.45rem;
      border-radius: 10px;
      font-weight: 600;
    }}

    .nav-tab.active .nav-badge {{
      background: #000000;
      color: #ffffff;
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .search-box {{
      position: relative;
      width: 280px;
    }}

    .search-box input {{
      width: 100%;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.5rem 1rem 0.5rem 2.4rem;
      border-radius: 20px;
      font-size: 0.85rem;
      outline: none;
      transition: border-color 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: #ffffff;
    }}

    .search-icon {{
      position: absolute;
      left: 0.85rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    /* --- BOLD STATEMENT HERO SECTION (3-ROW CENTER ALIGNED) --- */
    .hero-section {{
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
      line-height: 1.02;
      color: #ffffff;
      margin-bottom: 1.2rem;
      text-align: center;
    }}

    .hero-subtitle {{
      color: var(--text-muted);
      font-size: 0.98rem;
      max-width: 600px;
      margin: 0 auto 1.8rem;
      line-height: 1.5;
    }}

    .sub-filter-bar {{
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .sub-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.4rem 1rem;
      border-radius: 20px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .sub-btn:hover {{
      background: rgba(255, 255, 255, 0.12);
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.25);
    }}

    .sub-btn.active {{
      background: #ffffff;
      color: #000000;
      border-color: #ffffff;
    }}

    /* --- MAIN GALLERY GRID --- */
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

    /* ZERO-CLIPPING MASONRY COLUMN GRID */
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

    /* PHOTO CARD */
    .photo-card {{
      break-inside: avoid;
      margin-bottom: 1.25rem;
      position: relative;
      background: var(--bg-card);
      border-radius: var(--radius);
      cursor: pointer;
      border: 1px solid var(--border);
      transition: transform 0.25s ease, border-color 0.25s ease;
      width: 100%;
    }}

    .photo-card:hover {{
      transform: translateY(-4px);
      border-color: rgba(255, 255, 255, 0.3);
      z-index: 10;
    }}

    .photo-card img {{
      width: 100%;
      height: auto;
      display: block;
      border-radius: var(--radius);
      transition: opacity 0.3s ease;
    }}

    /* HOVER OVERLAY (DUAL COPY BUTTONS & DETAILS) */
    .hover-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.85) 70%, rgba(0,0,0,0.95) 100%);
      border-radius: var(--radius);
      opacity: 0;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 1rem;
      transition: opacity 0.2s ease;
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
      background: rgba(0, 0, 0, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #ffffff;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
    }}

    .dynamic-tag {{
      background: #10b981;
      color: #ffffff;
      border: none;
    }}

    .overlay-bottom {{
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}

    .card-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.05rem;
      font-weight: 700;
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
      background: rgba(255, 255, 255, 0.15);
      color: #ffffff;
      border: 1px solid rgba(255, 255, 255, 0.25);
      padding: 0.45rem 0.6rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.3rem;
      transition: all 0.2s ease;
      white-space: nowrap;
    }}

    .copy-btn-sm:hover {{
      background: #ffffff;
      color: #000000;
      border-color: #ffffff;
    }}

    .copy-btn-sm.copied {{
      background: #10b981;
      border-color: #10b981;
      color: #ffffff;
    }}

    /* --- LIGHTBOX DETAIL MODAL --- */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.88);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
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
      background: #111116;
      border: 1px solid var(--border);
      border-radius: 16px;
      max-width: 1100px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      display: grid;
      grid-template-columns: 1fr 380px;
      position: relative;
      box-shadow: 0 25px 60px rgba(0,0,0,0.9);
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
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #ffffff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.2rem;
      z-index: 20;
      transition: all 0.2s ease;
    }}

    .modal-close:hover {{
      background: rgba(255, 255, 255, 0.2);
    }}

    .modal-image-area {{
      background: #000000;
      padding: 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
    }}

    .modal-image-area img {{
      max-width: 100%;
      max-height: 65vh;
      object-fit: contain;
      border-radius: 8px;
    }}

    .view-toggle-bar {{
      margin-top: 1rem;
      display: flex;
      gap: 0.5rem;
      background: rgba(255, 255, 255, 0.08);
      padding: 0.3rem;
      border-radius: 8px;
    }}

    .view-toggle-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.3rem 0.8rem;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
    }}

    .view-toggle-btn.active {{
      background: #ffffff;
      color: #000000;
    }}

    .modal-info-area {{
      padding: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      border-left: 1px solid var(--border);
    }}

    .modal-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.4rem;
      font-weight: 800;
      color: #ffffff;
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
      background: #ffffff;
      color: #000000;
      border: none;
      padding: 0.75rem 1rem;
      border-radius: 8px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
    }}

    .modal-copy-btn:hover {{
      background: #e5e7eb;
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
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-muted);
    }}

    .related-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.6rem;
    }}

    .related-thumb {{
      aspect-ratio: 16/9;
      background: #000000;
      border-radius: 6px;
      overflow: hidden;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s ease;
    }}

    .related-thumb:hover {{
      border-color: #ffffff;
      transform: scale(1.05);
    }}

    .related-thumb img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    footer {{
      border-top: 1px solid var(--border);
      padding: 2.5rem 1.5rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
      margin-top: 3rem;
    }}

    footer p {{
      max-width: 600px;
      margin: 0 auto;
      line-height: 1.5;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-top">
      <a href="#" class="brand-group">
        <div class="brand-badge">K</div>
        <span class="brand-title">Kaptain's Mega Collection</span>
      </a>

      <!-- PRIMARY NAV TABS -->
      <nav class="primary-nav" id="primaryNav">
        <button class="nav-tab active" data-type="covers">
          🎨 Covers <span class="nav-badge" id="badgeCovers">0</span>
        </button>
        <button class="nav-tab" data-type="backdrops">
          🖼️ Hero Backdrops <span class="nav-badge" id="badgeBackdrops">0</span>
        </button>
        <button class="nav-tab" data-type="logos">
          🏷️ Title Logos <span class="nav-badge" id="badgeLogos">0</span>
        </button>
        <button class="nav-tab" data-type="archive">
          📸 Gallery Archive <span class="nav-badge" id="badgeArchive">0</span>
        </button>
      </nav>

      <div class="header-right">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" placeholder="Search covers & assets...">
        </div>
      </div>
    </div>
  </header>

  <!-- STATEMENT HERO SECTION (3 ROWS CENTER ALIGNED) -->
  <section class="hero-section">
    <h1 class="hero-title">
      Kaptain's<br>
      Mega Collection<br>
      of Assets
    </h1>
    <p class="hero-subtitle">Official portfolio for Nuvio covers, dynamic daily artwork, hero backdrops, and title logos.</p>
    
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
    <p>Kaptain's Mega Collection • Official Nuvio Asset Portfolio hosted on GitHub Pages</p>
  </footer>

  <script>
    const ASSETS = {manifest_json};

    let activeType = 'covers';  // 'covers' | 'backdrops' | 'logos' | 'archive'
    let activeSub = 'all';     // sub-filter for covers
    let activeModalItem = null;

    const grid = document.getElementById('galleryGrid');
    const searchInput = document.getElementById('searchInput');
    const sectionLabel = document.getElementById('sectionLabel');
    const navTabs = document.querySelectorAll('.nav-tab');
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

    document.getElementById('badgeCovers').textContent = coversCount;
    document.getElementById('badgeBackdrops').textContent = backdropsCount;
    document.getElementById('badgeLogos').textContent = logosCount;
    document.getElementById('badgeArchive').textContent = archiveCount;

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

    navTabs.forEach(tab => {{
      tab.addEventListener('click', () => {{
        navTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        activeType = tab.dataset.type;

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
        
    print(f"Successfully generated clean 3-Row Center-Aligned Header Portfolio HTML at: {out_file}")

if __name__ == '__main__':
    main()

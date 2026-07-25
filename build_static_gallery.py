import os
import json

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ImKaptain/nuvio-assets/main"

def classify_asset_type(root_folder, file_path):
    """Strictly classifies an asset into 'covers', 'backdrops', or 'logos'."""
    lower_path = file_path.lower()
    lower_root = root_folder.lower()
    
    if 'titlelogos' in lower_root or 'logo' in lower_path:
        return 'logos'
    elif (lower_root.startswith('nuvio_backdrops_') or 
          'backdrop' in lower_path or 
          'backdrop' in lower_root or 
          'prism' in lower_path or 
          'wallpaper' in lower_path or 
          'hero' in lower_path):
        return 'backdrops'
    else:
        return 'covers'

def scan_assets():
    """Scans all folders in nuvio-assets and organizes them strictly into clean asset types."""
    assets = []
    ignore_dirs = {'.git', '.github', 'nuvio-share-hub', 'scratch', 'assets'}
    
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
                
            rel_file_path = os.path.join(rel_root, f).replace('\\', '/')
            raw_url = f"{GITHUB_RAW_BASE}/{rel_file_path.replace(' ', '%20')}"
            
            # Determine clean name
            clean_name = f
            for suffix in ['_Base_Dynamic.png', '_Hover_Dynamic.gif', '_Base.png', '_Hover.gif', '.png', '.jpg', '.gif']:
                if clean_name.endswith(suffix):
                    clean_name = clean_name[:-len(suffix)]
                    break
                    
            item_key = f"{rel_root}/{clean_name}"
            asset_type = classify_asset_type(category, rel_file_path)
            
            if item_key not in grouped:
                grouped[item_key] = {
                    'title': clean_name.replace('_', ' '),
                    'type': asset_type,  # 'covers' | 'backdrops' | 'logos'
                    'category': category,
                    'subfolder': subfolder,
                    'is_gallery': is_gallery,
                    'is_dynamic': '_Dynamic' in f,
                    'base_url': None,
                    'hover_url': None,
                    'file_path': rel_file_path
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
                
    return assets

def generate_gallery_html(assets):
    manifest_json = json.dumps(assets, indent=2)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nuvio Art Portfolio • Official Gallery</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070709;
      --bg-header: rgba(10, 10, 14, 0.85);
      --accent: #8b5cf6;
      --accent-glow: rgba(139, 92, 246, 0.4);
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --border: rgba(255, 255, 255, 0.08);
      --radius: 12px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
    }}

    /* --- MINIMAL HEADER & NAVIGATION --- */
    header {{
      background: var(--bg-header);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
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

    .brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: var(--text-main);
    }}

    .brand-logo {{
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, #8b5cf6, #ec4899);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-family: 'Outfit', sans-serif;
      font-size: 1rem;
      box-shadow: 0 4px 15px var(--accent-glow);
    }}

    .brand-text {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.5px;
    }}

    .search-box {{
      position: relative;
      width: 320px;
    }}

    .search-box input {{
      width: 100%;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.55rem 1rem 0.55rem 2.4rem;
      border-radius: 20px;
      font-size: 0.88rem;
      outline: none;
      transition: all 0.25s ease;
    }}

    .search-box input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 16px var(--accent-glow);
    }}

    .search-icon {{
      position: absolute;
      left: 0.85rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    /* --- PRIMARY NAVIGATION TABS --- */
    .primary-nav {{
      max-width: 1600px;
      margin: 0 auto;
      padding: 0 2rem;
      display: flex;
      gap: 0.5rem;
    }}

    .nav-tab {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-family: 'Outfit', sans-serif;
      font-size: 0.95rem;
      font-weight: 600;
      padding: 0.75rem 1.2rem;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
    }}

    .nav-tab:hover {{
      color: var(--text-main);
    }}

    .nav-tab.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
    }}

    .nav-badge {{
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-muted);
      font-size: 0.72rem;
      padding: 0.15rem 0.5rem;
      border-radius: 12px;
      font-weight: 500;
    }}

    .nav-tab.active .nav-badge {{
      background: rgba(139, 92, 246, 0.2);
      color: var(--accent);
    }}

    /* --- SECONDARY SUB-FILTERS (For Covers tab) --- */
    .sub-filter-bar {{
      max-width: 1600px;
      margin: 0.75rem auto 0;
      padding: 0 2rem 0.75rem;
      display: flex;
      gap: 0.5rem;
      overflow-x: auto;
      scrollbar-width: none;
      border-top: 1px solid rgba(255, 255, 255, 0.04);
      padding-top: 0.75rem;
    }}

    .sub-btn {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.35rem 0.85rem;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}

    .sub-btn:hover, .sub-btn.active {{
      background: rgba(139, 92, 246, 0.15);
      color: #fff;
      border-color: rgba(139, 92, 246, 0.4);
    }}

    /* --- MAIN GALLERY GRID --- */
    main {{
      max-width: 1600px;
      margin: 1.5rem auto;
      padding: 0 2rem;
      flex-grow: 1;
      width: 100%;
    }}

    .status-summary {{
      margin-bottom: 1.2rem;
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    /* CLEAN UNCLUTTERED TUMBLR / PHOTOGRAPHER GRID */
    .gallery-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1.25rem;
    }}

    /* ZERO-CLUTTER PHOTO CARD */
    .photo-card {{
      position: relative;
      aspect-ratio: 16/9;
      background: #050508;
      border-radius: var(--radius);
      overflow: hidden;
      cursor: pointer;
      border: 1px solid var(--border);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
    }}

    .photo-card:hover {{
      transform: scale(1.02);
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.8);
      z-index: 10;
    }}

    .photo-card img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: opacity 0.3s ease;
    }}

    /* HOVER OVERLAY (ALL TEXT & BUTTONS ARE HIDDEN UNTIL HOVER) */
    .hover-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.85) 70%, rgba(0,0,0,0.95) 100%);
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
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #fff;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
    }}

    .dynamic-tag {{
      background: linear-gradient(135deg, #10b981, #059669);
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
      color: #fff;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .card-sub {{
      font-size: 0.78rem;
      color: #d1d5db;
    }}

    .copy-btn {{
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 0.55rem 0.9rem;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      transition: background 0.2s ease, transform 0.15s ease;
      box-shadow: 0 4px 12px var(--accent-glow);
    }}

    .copy-btn:hover {{
      background: #7c3aed;
      transform: translateY(-1px);
    }}

    .copy-btn.copied {{
      background: #10b981;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }}

    footer {{
      border-top: 1px solid var(--border);
      padding: 2rem;
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
      <a href="#" class="brand">
        <div class="brand-logo">N</div>
        <span class="brand-text">NUVIO ART</span>
      </a>
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Search covers...">
      </div>
    </div>

    <!-- PRIMARY NAV TABS -->
    <div class="primary-nav" id="primaryNav">
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
    </div>

    <!-- SECONDARY SUB-FILTERS (Only visible on Covers tab) -->
    <div class="sub-filter-bar" id="subFilterBar">
      <button class="sub-btn active" data-sub="all">All Covers</button>
      <button class="sub-btn" data-sub="Genres">Genres</button>
      <button class="sub-btn" data-sub="Moods">Moods & Vibes</button>
      <button class="sub-btn" data-sub="Actors">Actors & Directors</button>
      <button class="sub-btn" data-sub="Streaming Services">Streaming & Networks</button>
      <button class="sub-btn" data-sub="Collection_Cards">Collection Cards</button>
    </div>
  </header>

  <main>
    <div class="status-summary" id="statsSummary">Loading gallery...</div>
    <div class="gallery-grid" id="galleryGrid"></div>
  </main>

  <footer>
    <p>Nuvio Mega Collection • Official Asset Portfolio hosted on GitHub Pages</p>
  </footer>

  <script>
    const ASSETS = {manifest_json};

    let activeType = 'covers';  // 'covers' | 'backdrops' | 'logos' | 'archive'
    let activeSub = 'all';     // sub-filter for covers

    const grid = document.getElementById('galleryGrid');
    const searchInput = document.getElementById('searchInput');
    const statsSummary = document.getElementById('statsSummary');
    const navTabs = document.querySelectorAll('.nav-tab');
    const subBtns = document.querySelectorAll('.sub-btn');
    const subFilterBar = document.getElementById('subFilterBar');

    // Update Counts (STRICT CLASSIFICATION)
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
        if (item.is_gallery) return false; // Strictly hide gallery items from normal tabs

        // Backdrops Tab (STRICT)
        if (activeType === 'backdrops') return item.type === 'backdrops';
        
        // Logos Tab (STRICT)
        if (activeType === 'logos') return item.type === 'logos';
        
        // Covers Tab (STRICT: MUST BE TYPE 'COVERS')
        if (activeType === 'covers') {{
          if (item.type !== 'covers') return false; // Zero backdrops allowed here!
          if (activeSub === 'all') return true;
          if (activeSub === 'Actors') return item.category === 'Actors' || item.category === 'Directors';
          if (activeSub === 'Streaming Services') return item.category === 'Streaming Services' || item.category === 'Networks';
          return item.category === activeSub;
        }}

        return true;
      }});

      statsSummary.textContent = `Showing ${{filtered.length}} items`;
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
              <button class="copy-btn" data-url="${{baseSrc}}">
                <span>📋 Copy Raw URL</span>
              </button>
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

        const copyBtn = card.querySelector('.copy-btn');
        copyBtn.addEventListener('click', (e) => {{
          e.stopPropagation();
          navigator.clipboard.writeText(baseSrc);
          copyBtn.classList.add('copied');
          copyBtn.querySelector('span').textContent = '✓ Copied!';
          setTimeout(() => {{
            copyBtn.classList.remove('copied');
            copyBtn.querySelector('span').textContent = '📋 Copy Raw URL';
          }}, 2000);
        }});

        grid.appendChild(card);
      }});
    }}

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
        
    print(f"Successfully generated clean zero-clutter Photographer Portfolio HTML at: {out_file}")

if __name__ == '__main__':
    main()

import os
import json

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ImKaptain/nuvio-assets/main"

def classify_asset_type(root_folder, file_path):
    """Classifies an asset into 'covers', 'backdrops', or 'logos'."""
    lower_path = file_path.lower()
    lower_root = root_folder.lower()
    
    if 'titlelogos' in lower_root or 'logo' in lower_path:
        return 'logos'
    elif lower_root.startswith('nuvio_backdrops_') or 'backdrop' in lower_path:
        return 'backdrops'
    else:
        return 'covers'

def scan_assets():
    """Scans all folders in nuvio-assets and organizes them into clean categories."""
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
  <title>Nuvio Art Portfolio • Official Asset Gallery</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070709;
      --bg-card: #111116;
      --bg-header: rgba(11, 11, 15, 0.85);
      --accent: #8b5cf6;
      --accent-hover: #7c3aed;
      --accent-glow: rgba(139, 92, 246, 0.35);
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --border: rgba(255, 255, 255, 0.08);
      --border-hover: rgba(139, 92, 246, 0.4);
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

    /* --- TOP HEADER & NAVIGATION --- */
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
      max-width: 1500px;
      margin: 0 auto;
      padding: 1.2rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1.5rem;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 0.8rem;
      text-decoration: none;
      color: var(--text-main);
    }}

    .brand-logo {{
      width: 34px;
      height: 34px;
      background: linear-gradient(135deg, #8b5cf6, #ec4899);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-family: 'Outfit', sans-serif;
      font-size: 1.1rem;
      box-shadow: 0 4px 15px var(--accent-glow);
    }}

    .brand-text {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.3rem;
      font-weight: 800;
      letter-spacing: -0.5px;
    }}

    .brand-tag {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--accent);
      background: rgba(139, 92, 246, 0.12);
      border: 1px solid rgba(139, 92, 246, 0.3);
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      margin-left: 0.4rem;
    }}

    .search-box {{
      position: relative;
      width: 360px;
    }}

    .search-box input {{
      width: 100%;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.65rem 1rem 0.65rem 2.6rem;
      border-radius: 20px;
      font-size: 0.9rem;
      outline: none;
      transition: all 0.25s ease;
    }}

    .search-box input:focus {{
      background: rgba(255, 255, 255, 0.07);
      border-color: var(--accent);
      box-shadow: 0 0 16px var(--accent-glow);
    }}

    .search-icon {{
      position: absolute;
      left: 0.9rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 0.9rem;
    }}

    /* --- PRIMARY TABS (Covers, Backdrops, Logos, Archive) --- */
    .primary-nav {{
      max-width: 1500px;
      margin: 0 auto;
      padding: 0 2rem;
      display: flex;
      gap: 0.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }}

    .nav-tab {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-family: 'Outfit', sans-serif;
      font-size: 0.95rem;
      font-weight: 600;
      padding: 0.8rem 1.4rem;
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
      font-size: 0.75rem;
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
      max-width: 1500px;
      margin: 1rem auto 0;
      padding: 0 2rem;
      display: flex;
      gap: 0.5rem;
      overflow-x: auto;
      scrollbar-width: none;
    }}

    .sub-btn {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.4rem 0.9rem;
      border-radius: 20px;
      font-size: 0.82rem;
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

    /* --- MAIN CONTENT & PORTFOLIO GRID --- */
    main {{
      max-width: 1500px;
      margin: 2rem auto;
      padding: 0 2rem;
      flex-grow: 1;
      width: 100%;
    }}

    .status-bar {{
      margin-bottom: 1.5rem;
      color: var(--text-muted);
      font-size: 0.88rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    /* TUMBLR / PHOTOGRAPHER PORTFOLIO GRID */
    .portfolio-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.8rem;
    }}

    .portfolio-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease, box-shadow 0.3s ease;
    }}

    .portfolio-card:hover {{
      transform: translateY(-6px);
      border-color: var(--border-hover);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7);
    }}

    .media-frame {{
      position: relative;
      width: 100%;
      aspect-ratio: 16/9;
      background: #000;
      overflow: hidden;
    }}

    .media-frame img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.5s ease, opacity 0.3s ease;
    }}

    .portfolio-card:hover .media-frame img {{
      transform: scale(1.03);
    }}

    .tag-overlay {{
      position: absolute;
      top: 0.7rem;
      right: 0.7rem;
      display: flex;
      gap: 0.4rem;
      z-index: 10;
    }}

    .tag-pill {{
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.2rem 0.6rem;
      border-radius: 6px;
      letter-spacing: 0.3px;
    }}

    .dynamic-pill {{
      background: linear-gradient(135deg, #10b981, #059669);
      border: none;
    }}

    .card-footer {{
      padding: 1.1rem;
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
      background: linear-gradient(180deg, rgba(17, 17, 22, 0.6) 0%, rgba(17, 17, 22, 1) 100%);
      flex-grow: 1;
      justify-content: space-between;
    }}

    .card-info {{
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }}

    .card-title-text {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.05rem;
      font-weight: 700;
      color: #fff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .card-subtext {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}

    .copy-raw-btn {{
      background: rgba(139, 92, 246, 0.12);
      color: #a78bfa;
      border: 1px solid rgba(139, 92, 246, 0.3);
      padding: 0.6rem 1rem;
      border-radius: 8px;
      font-size: 0.83rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
    }}

    .copy-raw-btn:hover {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
      box-shadow: 0 4px 12px var(--accent-glow);
    }}

    .copy-raw-btn.copied {{
      background: #10b981;
      color: #fff;
      border-color: #10b981;
    }}

    footer {{
      border-top: 1px solid var(--border);
      padding: 2.5rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
      margin-top: 4rem;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-top">
      <a href="#" class="brand">
        <div class="brand-logo">N</div>
        <span class="brand-text">NUVIO ART</span>
        <span class="brand-tag">PORTFOLIO</span>
      </a>
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Search covers, backdrops, actors, moods...">
      </div>
    </div>

    <!-- PRIMARY TABS -->
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

    <!-- SECONDARY SUB-FILTERS (Shown for Covers) -->
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
    <div class="status-bar">
      <span id="statsSummary">Loading artwork portfolio...</span>
    </div>
    <div class="portfolio-grid" id="portfolioGrid"></div>
  </main>

  <footer>
    <p>Nuvio Mega Collection • Official Asset Portfolio hosted on GitHub Pages</p>
  </footer>

  <script>
    const ASSETS = {manifest_json};

    let activeType = 'covers';  // 'covers' | 'backdrops' | 'logos' | 'archive'
    let activeSub = 'all';     // sub-filter for covers

    const grid = document.getElementById('portfolioGrid');
    const searchInput = document.getElementById('searchInput');
    const statsSummary = document.getElementById('statsSummary');
    const navTabs = document.querySelectorAll('.nav-tab');
    const subBtns = document.querySelectorAll('.sub-btn');
    const subFilterBar = document.getElementById('subFilterBar');

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

        if (activeType === 'archive') return item.is_gallery;
        if (item.is_gallery) return false; // Hide gallery from normal tabs

        if (activeType === 'backdrops') return item.type === 'backdrops';
        if (activeType === 'logos') return item.type === 'logos';
        
        // Covers tab
        if (activeType === 'covers') {{
          if (item.type !== 'covers') return false;
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
        card.className = 'portfolio-card';

        const baseSrc = item.base_url;
        const hoverSrc = item.hover_url || item.base_url;

        let badgeText = item.category;
        if (item.is_dynamic) badgeText = '⚡ Dynamic';
        else if (item.is_gallery) badgeText = '📸 Archive';

        card.innerHTML = `
          <div class="media-frame">
            <img src="${{baseSrc}}" alt="${{item.title}}" loading="lazy">
            <div class="tag-overlay">
              <span class="tag-pill ${{item.is_dynamic ? 'dynamic-pill' : ''}}">${{badgeText}}</span>
            </div>
          </div>
          <div class="card-footer">
            <div class="card-info">
              <div class="card-title-text">${{item.title}}</div>
              <div class="card-subtext">${{item.category}} ${{item.subfolder ? '• ' + item.subfolder : ''}}</div>
            </div>
            <button class="copy-raw-btn" data-url="${{baseSrc}}">
              <span>📋 Copy Raw URL</span>
            </button>
          </div>
        `;

        const img = card.querySelector('img');
        card.addEventListener('mouseenter', () => {{
          if (item.hover_url) img.src = hoverSrc;
        }});
        card.addEventListener('mouseleave', () => {{
          img.src = baseSrc;
        }});

        const copyBtn = card.querySelector('.copy-raw-btn');
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
        
    print(f"Successfully generated clean Tumblr-style Portfolio HTML at: {out_file}")

if __name__ == '__main__':
    main()

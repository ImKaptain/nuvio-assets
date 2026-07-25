import os
import json
import re

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ImKaptain/nuvio-assets/main"

def scan_assets():
    """Scans all folders in nuvio-assets to build structured items list."""
    assets = []
    
    ignore_dirs = {'.git', '.github', 'nuvio-share-hub', 'scratch', 'assets'}
    
    for root, dirs, files in os.walk(ASSET_DIR):
        # Filter out ignored dirs
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
            
            # Determine item key (strip _Base, _Hover, _Dynamic)
            clean_name = f
            for suffix in ['_Base_Dynamic.png', '_Hover_Dynamic.gif', '_Base.png', '_Hover.gif', '.png', '.jpg', '.gif']:
                if clean_name.endswith(suffix):
                    clean_name = clean_name[:-len(suffix)]
                    break
                    
            item_key = f"{rel_root}/{clean_name}"
            if item_key not in grouped:
                grouped[item_key] = {
                    'title': clean_name.replace('_', ' '),
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
  <title>Nuvio Art Gallery & Asset Portfolio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #0a0a0c;
      --bg-card: #121218;
      --bg-card-hover: #1a1a24;
      --accent: #6366f1;
      --accent-glow: rgba(99, 102, 241, 0.4);
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --border: rgba(255, 255, 255, 0.08);
      --radius: 12px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: 'Outfit', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    header {{
      background: linear-gradient(180deg, rgba(18, 18, 24, 0.9) 0%, rgba(10, 10, 12, 0.8) 100%);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 1.25rem 2rem;
    }}

    .header-container {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }}

    .logo-group {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #6366f1, #a855f7);
      color: #fff;
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      font-size: 0.85rem;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      letter-spacing: 1px;
    }}

    h1 {{
      font-size: 1.4rem;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}

    .search-box {{
      position: relative;
      flex-grow: 1;
      max-width: 450px;
    }}

    .search-box input {{
      width: 100%;
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.65rem 1rem 0.65rem 2.5rem;
      border-radius: 20px;
      font-size: 0.95rem;
      outline: none;
      transition: all 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 12px var(--accent-glow);
    }}

    .search-icon {{
      position: absolute;
      left: 0.85rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
    }}

    .categories-bar {{
      max-width: 1400px;
      margin: 1rem auto 0;
      padding: 0 2rem;
      display: flex;
      gap: 0.5rem;
      overflow-x: auto;
      scrollbar-width: none;
    }}

    .cat-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.4rem 1rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}

    .cat-btn:hover, .cat-btn.active {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
      box-shadow: 0 0 10px var(--accent-glow);
    }}

    main {{
      max-width: 1400px;
      margin: 2rem auto;
      padding: 0 2rem;
      flex-grow: 1;
      width: 100%;
    }}

    .stats-summary {{
      margin-bottom: 1.5rem;
      color: var(--text-muted);
      font-size: 0.9rem;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.5rem;
    }}

    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
      position: relative;
    }}

    .card:hover {{
      transform: translateY(-4px);
      border-color: rgba(99, 102, 241, 0.5);
      box-shadow: 0 12px 30px rgba(0,0,0,0.6);
    }}

    .media-container {{
      position: relative;
      aspect-ratio: 16/9;
      background: #050508;
      overflow: hidden;
    }}

    .media-container img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.3s ease;
    }}

    .badge-tag {{
      position: absolute;
      top: 0.6rem;
      right: 0.6rem;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,0.15);
      color: #fff;
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
    }}

    .dynamic-tag {{
      background: linear-gradient(135deg, #10b981, #059669);
      border: none;
    }}

    .card-body {{
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      flex-grow: 1;
      justify-content: space-between;
    }}

    .card-title {{
      font-size: 1rem;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .card-meta {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}

    .copy-btn {{
      background: rgba(99, 102, 241, 0.15);
      color: #a5b4fc;
      border: 1px solid rgba(99, 102, 241, 0.3);
      padding: 0.5rem 0.8rem;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      transition: all 0.2s;
    }}

    .copy-btn:hover {{
      background: var(--accent);
      color: #fff;
    }}

    .copy-btn.copied {{
      background: #10b981;
      color: #fff;
      border-color: #10b981;
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
    <div class="header-container">
      <div class="logo-group">
        <span class="logo-badge">NUVIO ART</span>
        <h1>Asset Portfolio & Gallery</h1>
      </div>
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Search movies, genres, actors, mood cards...">
      </div>
    </div>
    <div class="categories-bar" id="categoriesBar">
      <button class="cat-btn active" data-cat="all">All Assets</button>
      <button class="cat-btn" data-cat="Genres">Genres</button>
      <button class="cat-btn" data-cat="Moods">Moods & Vibes</button>
      <button class="cat-btn" data-cat="Actors">Actors</button>
      <button class="cat-btn" data-cat="Directors">Directors</button>
      <button class="cat-btn" data-cat="Streaming Services">Streaming Services</button>
      <button class="cat-btn" data-cat="TitleLogos">Title Logos</button>
      <button class="cat-btn" data-cat="gallery">Gallery Archive</button>
    </div>
  </header>

  <main>
    <div class="stats-summary" id="statsSummary">Showing assets...</div>
    <div class="grid" id="assetGrid"></div>
  </main>

  <footer>
    <p>Nuvio Mega Collection • Hosted on GitHub Pages</p>
  </footer>

  <script>
    const ASSETS = {manifest_json};
    let currentCat = 'all';

    const grid = document.getElementById('assetGrid');
    const searchInput = document.getElementById('searchInput');
    const statsSummary = document.getElementById('statsSummary');
    const catBtns = document.querySelectorAll('.cat-btn');

    function renderGrid() {{
      const query = searchInput.value.toLowerCase().trim();
      
      const filtered = ASSETS.filter(item => {{
        const matchesSearch = item.title.toLowerCase().includes(query) || 
                              item.category.toLowerCase().includes(query) || 
                              (item.subfolder && item.subfolder.toLowerCase().includes(query));
                              
        if (currentCat === 'all') return matchesSearch;
        if (currentCat === 'gallery') return matchesSearch && item.is_gallery;
        return matchesSearch && item.category === currentCat && !item.is_gallery;
      }});

      statsSummary.textContent = `Showing ${{filtered.length}} of ${{ASSETS.length}} hosted assets`;
      grid.innerHTML = '';

      filtered.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'card';

        const hoverSrc = item.hover_url || item.base_url;
        const baseSrc = item.base_url;

        let badgeHtml = `<span class="badge-tag">${{item.category}}</span>`;
        if (item.is_dynamic) {{
          badgeHtml = `<span class="badge-tag dynamic-tag">⚡ Dynamic</span>`;
        }} else if (item.is_gallery) {{
          badgeHtml = `<span class="badge-tag">📸 Gallery Archive</span>`;
        }}

        card.innerHTML = `
          <div class="media-container">
            <img src="${{baseSrc}}" alt="${{item.title}}" data-base="${{baseSrc}}" data-hover="${{hoverSrc}}" loading="lazy">
            ${{badgeHtml}}
          </div>
          <div class="card-body">
            <div>
              <div class="card-title">${{item.title}}</div>
              <div class="card-meta">${{item.category}} ${{item.subfolder ? '• ' + item.subfolder : ''}}</div>
            </div>
            <button class="copy-btn" data-url="${{baseSrc}}">
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

        const copyBtn = card.querySelector('.copy-btn');
        copyBtn.addEventListener('click', (e) => {{
          e.stopPropagation();
          navigator.clipboard.writeText(item.base_url);
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

    catBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        catBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCat = btn.dataset.cat;
        renderGrid();
      }});
    }});

    searchInput.addEventListener('input', renderGrid);

    // Initial render
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
        
    print(f"Successfully generated static gallery HTML at: {out_file}")

if __name__ == '__main__':
    main()

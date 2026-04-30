const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const axios = require('axios');
const sharp = require('sharp');

// --- CONFIGURATION ---
const GITHUB_USERNAME = 'ImKaptain'; // e.g., 'timwa'
const REPO_NAME = 'nuvio-assets';             // e.g., 'nuvio-assets'
const INPUT_FILE = 'nuvio_config.json';
const OUTPUT_FILE = 'optimized_config.json';
const ASSETS_DIR = path.join(__dirname, 'assets', 'images');

// Keys to search for and their respective optimization rules
// Note: 'focusGifUrl' is intentionally removed so it gets completely ignored!
const IMAGE_KEYS = [
  'coverImageUrl',
  'heroBackdropUrl',
  'titleLogoUrl',
  'backdropImageUrl'
];

// Ensure the local assets/images directory exists
if (!fs.existsSync(ASSETS_DIR)) {
  fs.mkdirSync(ASSETS_DIR, { recursive: true });
}

// Helper: Generates a short 8-character MD5 hash of the original URL
function generateShortHash(url) {
  return crypto.createHash('md5').update(url).digest('hex').slice(0, 8);
}

// Helper: Downloads an image as a Buffer
async function downloadImage(url) {
  try {
    const response = await axios({
      url,
      method: 'GET',
      responseType: 'arraybuffer',
      timeout: 15000,
    });
    return Buffer.from(response.data);
  } catch (error) {
    console.error(`[ERROR] Failed to download ${url}:`, error.message);
    return null;
  }
}

// Recursive function to traverse the JSON and process matching keys
async function processJSON(obj) {
  if (Array.isArray(obj)) {
    for (let i = 0; i < obj.length; i++) {
      await processJSON(obj[i]);
    }
  } 
  else if (obj !== null && typeof obj === 'object') {
    for (const key of Object.keys(obj)) {
      const value = obj[key];
      
      if (IMAGE_KEYS.includes(key) && typeof value === 'string' && value.match(/^https?:\/\//)) {
        
        // Skip logic: case-insensitive check to ensure lowercase URLs are still skipped
        if (value.toLowerCase().includes(GITHUB_USERNAME.toLowerCase())) {
          console.log(`[SKIPPING] Already optimized URL: ${value}`);
          continue;
        }

        const hash = generateShortHash(value);
        const fileName = `${hash}.webp`; // Reverted to .webp for TV compatibility
        const filePath = path.join(ASSETS_DIR, fileName);
        
        // Utilizing the new GitHub Pages CDN - forced lowercase to prevent 404 errors!
        const newUrl = `https://${GITHUB_USERNAME.toLowerCase()}.github.io/${REPO_NAME}/assets/images/${fileName}`;
        
        if (!fs.existsSync(filePath)) {
          console.log(`[PROCESSING] ${key}: ${value}`);
          const imageBuffer = await downloadImage(value);
          
          // Only proceed if the buffer actually has data
          if (imageBuffer && imageBuffer.length > 0) {
            try {
              // 1. Initialize sharp with animation support
              let pipeline = sharp(imageBuffer, { animated: true });
              
              // 2. Apply Resizing Logic
              if (key === 'coverImageUrl' || key === 'titleLogoUrl') {
                // High-quality UI thumbnails
                pipeline = pipeline.resize({ width: 500, withoutEnlargement: true });
              } 
              else if (key === 'heroBackdropUrl' || key === 'backdropImageUrl') {
                // Cinematic backdrops
                pipeline = pipeline.resize({ width: 1280, withoutEnlargement: true });
              }
              
              // 3. Convert to WebP (Hardware decoder friendly)
              await pipeline.webp({ animated: true }).toFile(filePath);
                
              console.log(`[SAVED] ${fileName} (${key})`);

              // SUCCESS: Only update the JSON if the file was actually saved
              obj[key] = newUrl;

            } catch (err) {
              console.error(`[SHARP ERROR] Failed to process ${value}:`, err.message);
              // Clean up the ghost file if sharp crashed mid-write
              if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath); 
              }
            }
          } else {
            console.log(`[DOWNLOAD FAILED] Skipping URL rewrite for: ${value}`);
          }
        } else {
          // Check if the cached file is actually a ghost file (0 bytes)
          const stats = fs.statSync(filePath);
          if (stats.size === 0) {
            console.log(`[GHOST FILE DETECTED] Deleting empty file: ${fileName}`);
            fs.unlinkSync(filePath);
            // We do not update the URL so you can try running it again later
          } else {
            console.log(`[CACHED] ${fileName}`);
            // File exists and is healthy, safe to update JSON
            obj[key] = newUrl; 
          }
        }
      } else {
        await processJSON(value);
      }
    }
  }
}

async function main() {
  try {
    if (!fs.existsSync(INPUT_FILE)) {
      console.error(`[FATAL] Input file not found: ${INPUT_FILE}`);
      return;
    }
    console.log(`Loading ${INPUT_FILE}...`);
    const rawData = fs.readFileSync(INPUT_FILE, 'utf-8');
    const config = JSON.parse(rawData);
    
    console.log('Optimizing images (WebP + Resizing + Ghost Hunting)...');
    await processJSON(config);
    
    console.log(`Writing output to ${OUTPUT_FILE}...`);
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(config, null, 2), 'utf-8');
    
    console.log('Done! All assets are now resized WebPs and linked via GitHub Pages.');
  } catch (error) {
    console.error('[FATAL] An unexpected error occurred:', error);
  }
}

main();
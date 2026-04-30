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
        
        if (value.includes(GITHUB_USERNAME)) {
          console.log(`[SKIPPING] Already optimized URL: ${value}`);
          continue;
        }
        const hash = generateShortHash(value);
        const fileName = `${hash}.avif`; // Switched to .avif
        const filePath = path.join(ASSETS_DIR, fileName);
        
        const newUrl = `https://cdn.jsdelivr.net/gh/${GITHUB_USERNAME}/${REPO_NAME}@main/assets/images/${fileName}`;
        if (!fs.existsSync(filePath)) {
          console.log(`[PROCESSING] ${key}: ${value}`);
          const imageBuffer = await downloadImage(value);
          
          if (imageBuffer) {
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
              // focusGifUrl is ignored by the if/else and remains original size
              // 3. Convert to AVIF (Superior compression)
              // quality: 50 in AVIF is roughly equivalent to 80 in WebP but much smaller
              await pipeline.avif({ quality: 50 }).toFile(filePath);
                
              console.log(`[SAVED] ${fileName} (${key})`);
            } catch (err) {
              console.error(`[SHARP ERROR] Failed to process ${value}:`, err.message);
            }
          }
        } else {
          console.log(`[CACHED] ${fileName}`);
        }
        obj[key] = newUrl;
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
    console.log('Optimizing images (AVIF + Resizing)...');
    await processJSON(config);
    console.log(`Writing output to ${OUTPUT_FILE}...`);
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(config, null, 2), 'utf-8');
    
    console.log('Done! All assets are now resized AVIFs.');
  } catch (error) {
    console.error('[FATAL] An unexpected error occurred:', error);
  }
}
main();
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

// The specific keys we want to look for
const IMAGE_KEYS = [
  'coverImageUrl',
  'heroBackdropUrl',
  'titleLogoUrl',
  'focusGifUrl',
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
      responseType: 'arraybuffer', // Required to handle binary data
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
  // If it's an array, iterate and recursively process each item
  if (Array.isArray(obj)) {
    for (let i = 0; i < obj.length; i++) {
      await processJSON(obj[i]);
    }
  } 
  // If it's an object, check its keys
  else if (obj !== null && typeof obj === 'object') {
    for (const key of Object.keys(obj)) {
      const value = obj[key];
      // If we found a matching key and the value is an HTTP/HTTPS URL
      if (IMAGE_KEYS.includes(key) && typeof value === 'string' && value.match(/^https?:\/\//)) {
        
        // Skip if the URL already points to our GitHub CDN
        if (value.includes(GITHUB_USERNAME)) {
          console.log(`[SKIPPING] Already optimized URL: ${value}`);
          continue;
        }
        const hash = generateShortHash(value);
        const fileName = `${hash}.webp`;
        const filePath = path.join(ASSETS_DIR, fileName);
        
        // Construct the new jsDelivr URL
        const newUrl = `https://cdn.jsdelivr.net/gh/${GITHUB_USERNAME}/${REPO_NAME}/assets/images/${fileName}`;
        // Only process and download if we haven't already saved this image locally
        if (!fs.existsSync(filePath)) {
          console.log(`[DOWNLOADING] ${value}`);
          const imageBuffer = await downloadImage(value);
          
          if (imageBuffer) {
            try {
              // ALWAYS pass { animated: true } to preserve animated GIFs
              // Sharp will handle standard static images normally
              await sharp(imageBuffer, { animated: true })
                .webp({ quality: 80 })
                .toFile(filePath);
                
              console.log(`[SAVED] ${fileName}`);
            } catch (err) {
              console.error(`[SHARP ERROR] Failed to process ${value}:`, err.message);
            }
          }
        } else {
          console.log(`[CACHED] File already exists locally: ${fileName}`);
        }
        // Update the JSON object in memory with the new CDN URL
        obj[key] = newUrl;
      } else {
        // If it's not a matching key, continue digging deeper
        await processJSON(value);
      }
    }
  }
}
// Main execution function
async function main() {
  try {
    if (!fs.existsSync(INPUT_FILE)) {
      console.error(`[FATAL] Input file not found: ${INPUT_FILE}`);
      return;
    }
    console.log(`Loading ${INPUT_FILE}...`);
    const rawData = fs.readFileSync(INPUT_FILE, 'utf-8');
    const config = JSON.parse(rawData);
    console.log('Scanning JSON for image URLs...');
    await processJSON(config);
    console.log(`Writing optimized JSON to ${OUTPUT_FILE}...`);
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(config, null, 2), 'utf-8');
    
    console.log('Success! All images processed and URLs updated.');
  } catch (error) {
    console.error('[FATAL] An unexpected error occurred:', error);
  }
}
main();

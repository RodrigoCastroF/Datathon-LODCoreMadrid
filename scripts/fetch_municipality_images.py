# scripts/fetch_municipality_images.py
"""
Fetch municipality images from Comunidad de Madrid plaza thumbnails.

Usage:
    python scripts/fetch_municipality_images.py --limit 10
"""

import argparse
import json
import re
import time
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from io import BytesIO

import pandas as pd
import requests
from PIL import Image
from tqdm import tqdm
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def slugify(text: str) -> str:
    """Convert municipality name to filename slug."""
    text = text.lower()
    text = re.sub(r'[áàäâ]', 'a', text)
    text = re.sub(r'[éèëê]', 'e', text)
    text = re.sub(r'[íìïî]', 'i', text)
    text = re.sub(r'[óòöô]', 'o', text)
    text = re.sub(r'[úùüû]', 'u', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def fetch_all_plaza_images() -> Dict[str, str]:
    """Fetch all plaza images from Comunidad de Madrid site once."""
    try:
        url = "https://www.comunidad.madrid/actividades/2024/plaza-plaza"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all images in lugares directory
        images = soup.find_all('img', src=re.compile(r'/img/lugares/'))
        
        plaza_images = {}
        for img in images:
            alt_text = img.get('alt', '')
            img_url = img.get('src', '')
            
            if img_url and '/img/lugares/' in img_url:
                # Extract municipality name from alt text (format: "Municipality - Plaza...")
                match = re.match(r'^([^-]+)', alt_text)
                if match:
                    muni_name = match.group(1).strip()
                    
                    # Clean URL
                    img_url = img_url.split('?')[0].split('&')[0]
                    img_url = img_url.replace('/styles/block_teaser_image_horizontal/public', '')
                    
                    if not img_url.startswith('http'):
                        img_url = f"https://www.comunidad.madrid{img_url}"
                    
                    plaza_images[muni_name] = img_url
        
        return plaza_images
        
    except Exception as e:
        print(f"❌ Error fetching plaza images: {e}")
        return {}


def match_municipality(muni: str, plaza_images: Dict[str, str]) -> Optional[str]:
    """Match municipality name to plaza image."""
    # Try exact match first
    if muni in plaza_images:
        return plaza_images[muni]
    
    # Try case-insensitive match
    for plaza_muni, url in plaza_images.items():
        if plaza_muni.lower() == muni.lower():
            return url
    
    # Try fuzzy match (contains)
    muni_lower = muni.lower()
    for plaza_muni, url in plaza_images.items():
        if muni_lower in plaza_muni.lower() or plaza_muni.lower() in muni_lower:
            return url
    
    return None


def download_image(url: str, output_path: Path) -> bool:
    """Download and save image."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGB")
        
        max_size = (800, 600)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        img.save(output_path, "JPEG", quality=95, optimize=True)
        return True
        
    except Exception:
        return False


def fetch_all_images(csv_path: str, output_dir: Path, limit: Optional[int] = None) -> Dict[str, str]:
    """Fetch images for all municipalities."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    municipalities = df["Nombre"].unique().tolist()
    
    print(f"📊 Total municipalities in CSV: {len(municipalities)}")
    
    if limit:
        municipalities = municipalities[:limit]
    
    # Fetch all plaza images once
    print("🔍 Fetching plaza images from Comunidad de Madrid...")
    plaza_images = fetch_all_plaza_images()
    print(f"✅ Found {len(plaza_images)} plaza images on site\n")
    
    manifest = {}
    not_found = []
    
    print(f"🖼️  Matching and downloading {len(municipalities)} municipalities...")
    print(f"📁 Output: {output_dir}\n")
    
    for muni in tqdm(municipalities, desc="Downloading"):
        slug = slugify(muni)
        output_path = output_dir / f"{slug}.jpg"
        
        if output_path.exists():
            manifest[slug] = "cached"
            continue
        
        img_url = match_municipality(muni, plaza_images)
        
        if img_url:
            success = download_image(img_url, output_path)
            manifest[slug] = "success" if success else "failed"
        else:
            manifest[slug] = "not_found"
            not_found.append(muni)
        
        time.sleep(0.5)
    
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Report missing municipalities
    if not_found:
        print(f"\n⚠️  Missing municipalities ({len(not_found)}):")
        for muni in not_found:
            print(f"  - {muni}")
    
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Test with N municipalities")
    parser.add_argument("--csv", default="data/merged_dataset.csv")
    parser.add_argument("--output", default="assets/municipalities")
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / args.csv
    output_dir = script_dir / args.output
    
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        return
    
    manifest = fetch_all_images(str(csv_path), output_dir, args.limit)
    
    print("\n" + "="*60)
    print("📊 Summary:")
    print(f"  ✅ Success: {sum(1 for v in manifest.values() if v == 'success')}")
    print(f"  💾 Cached: {sum(1 for v in manifest.values() if v == 'cached')}")
    print(f"  ❌ Failed: {sum(1 for v in manifest.values() if v == 'failed')}")
    print(f"  🔍 Not found: {sum(1 for v in manifest.values() if v == 'not_found')}")
    print("="*60)


if __name__ == "__main__":
    main()

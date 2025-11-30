#!/usr/bin/env python3
import os, zipfile, shutil
from pathlib import Path

# Config
TMPDIR = Path("data/_dual_tmp")
OUTDIR = Path("data/opensubs_raw/by_lang")
LANGS = ["tr", "en", "de", "fr", "it", "es", "nl", "pl", "el", "ru"]

def main():
    # Ensure output directories exist
    for lang in LANGS:
        (OUTDIR / lang).mkdir(parents=True, exist_ok=True)

    # Get list of all zip files
    all_zips = list(TMPDIR.glob("*.zip"))
    print(f"Found {len(all_zips)} zip files. Scanning for target languages...")

    for lang in LANGS:
        print(f"\n--- Looking for: {lang} ---")
        found = False
        target_file_suffix = f".{lang}"  # e.g., ".tr"
        
        # We prefer v2018 over v2016 if available, so let's sort zips to put 2018 first
        sorted_zips = sorted(all_zips, key=lambda x: "2018" in x.name, reverse=True)

        for zip_path in sorted_zips:
            try:
                if not zipfile.is_zipfile(zip_path):
                    continue

                with zipfile.ZipFile(zip_path, "r") as zf:
                    # Look for a file inside that ends with .tr (or .en, etc)
                    candidates = [n for n in zf.namelist() if n.endswith(target_file_suffix)]
                    
                    if candidates:
                        # We found the file!
                        source_filename = candidates[0]
                        dest_path = OUTDIR / lang / f"{lang}.txt"
                        
                        print(f"  Found {source_filename} in {zip_path.name}")
                        print(f"  -> Extracting to {dest_path}...")
                        
                        with zf.open(source_filename) as source, open(dest_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        
                        found = True
                        break  # Stop looking for this language, move to next
            except Exception as e:
                print(f"  [Warn] Skipping bad zip {zip_path.name}: {e}")
        
        if not found:
            print(f"  [FAIL] Could not find any file ending in {target_file_suffix} inside the zips.")

    print("\n\nDone! Check your 'data/opensubs_raw/by_lang' folder.")

if __name__ == "__main__":
    main()

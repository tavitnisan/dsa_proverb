#!/usr/bin/env python3
import os, sys, csv, gzip, shutil, zipfile
from pathlib import Path
from datetime import datetime, timezone
import urllib.request, urllib.error
import ssl
import time

# Try to use certifi for SSL certificates. 
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    print("Warning: 'certifi' not found. Disabling SSL verification.")
    SSL_CONTEXT = ssl._create_unverified_context()

# Languages to download
LANGS = ["tr", "en", "de", "fr", "it", "es", "nl", "pl", "el", "ru"]

# We focus on v2018 as it is the most stable release on these mirrors
VERSIONS = ["v2018", "v2016"]

PRIMARY_BASE = "https://object.pouta.csc.fi/OPUS-OpenSubtitles"
FALLBACK_BASE = "https://opus.nlpl.eu/download.php?f=OPUS-OpenSubtitles"

OUTDIR = Path("data/opensubs_raw/by_lang")
TMPDIR = Path("data/_dual_tmp")
SUMMARY = Path("data/corpus_summary.csv")
LOG = TMPDIR / "download.log"

for d in (OUTDIR, TMPDIR):
    d.mkdir(parents=True, exist_ok=True)

def log(msg):
    # Print with a timestamp so we know when things happen
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

def try_url(url, dest):
    """Attempts to download a URL with a progress bar."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=60) as r:
            # Get file size if available
            file_size = r.getheader('Content-Length')
            file_size = int(file_size) if file_size else None
            
            with open(dest, "wb") as f:
                downloaded = 0
                block_sz = 8192 * 4
                while True:
                    buffer = r.read(block_sz)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    f.write(buffer)
                    
                    # Visual Progress Bar
                    if file_size:
                        percent = downloaded * 100 / file_size
                        mb_dl = downloaded / (1024 * 1024)
                        mb_tot = file_size / (1024 * 1024)
                        sys.stdout.write(f"\r    Downloading: {percent:.1f}% ({mb_dl:.1f}/{mb_tot:.1f} MB)")
                    else:
                        mb_dl = downloaded / (1024 * 1024)
                        sys.stdout.write(f"\r    Downloading: {mb_dl:.1f} MB (Unknown Total)")
                    sys.stdout.flush()
        
        print() # Move to next line after done
        return True, 200
    except urllib.error.HTTPError as e:
        sys.stdout.write("\r") # clear line
        return False, e.code
    except Exception as e:
        sys.stdout.write("\r") # clear line
        log(f"    Error {e} for {url}")
        return False, None

def get_moses_config(lang):
    if lang == "en":
        return "de-en", 1
    
    pair = sorted([lang, "en"])
    pair_str = f"{pair[0]}-{pair[1]}"
    target_col = pair.index(lang)
    return pair_str, target_col

def extract_from_moses_zip(zip_path, out_txt, target_col):
    kept = 0
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = [m for m in zf.namelist() if m.endswith(".txt")]
            if not members:
                return 0
            
            print(f"    Extracting text from zip...", flush=True)
            with zf.open(members[0], "r") as fin, open(out_txt, "w", encoding="utf-8") as fout:
                for raw in fin:
                    try:
                        line = raw.decode("utf-8", errors="ignore").strip()
                        parts = line.split(" ||| ")
                        if len(parts) >= 2:
                            text = parts[target_col].strip()
                            if text:
                                fout.write(text + "\n")
                                kept += 1
                    except Exception:
                        continue
    except Exception as e:
        log(f"    Zip extraction error: {e}")
        return 0
    return kept

def count(path):
    lines = toks = 0
    if not path.exists(): return 0, 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for ln in f:
            lines += 1
            toks += len(ln.split())
    return lines, toks

def main():
    rows = []
    
    for lang in LANGS:
        outdir = OUTDIR / lang
        outdir.mkdir(parents=True, exist_ok=True)
        out_txt = outdir / f"{lang}.txt"
        
        if out_txt.exists() and out_txt.stat().st_size > 100000:
            print(f"Skipping {lang}, already exists.")
            continue

        ok = False
        used_version = ""
        used_mode = ""

        # STRATEGY 1: Try Moses Pair
        pair_str, target_col = get_moses_config(lang)
        
        for ver in VERSIONS:
            rel = f"/{ver}/moses/{pair_str}.txt.zip"
            urls = [
                f"{PRIMARY_BASE}{rel}",
                f"{FALLBACK_BASE}{rel}"
            ]
            
            for url in urls:
                tmp_zip = TMPDIR / f"{pair_str}.{ver}.zip"
                log(f"Trying MOSES {url} (extract col {target_col})")
                
                success, code = try_url(url, tmp_zip)
                if success:
                    kept = extract_from_moses_zip(tmp_zip, out_txt, target_col)
                    if kept > 1000:
                        ok = True
                        used_version = ver
                        used_mode = f"moses({pair_str})"
                        tmp_zip.unlink() 
                        break
                    else:
                        log("    Extraction resulted in empty or small file.")
            if ok: break

        # STRATEGY 2: Mono (Fallback)
        if not ok and lang != "en":
            for ver in VERSIONS:
                rel = f"/{ver}/mono/OpenSubtitles.raw.{lang}.gz"
                urls = [
                    f"{PRIMARY_BASE}{rel}",
                    f"{FALLBACK_BASE}{rel}"
                ]
                for url in urls:
                    tmp_gz = TMPDIR / f"{lang}.{ver}.gz"
                    log(f"Trying MONO {url}")
                    success, code = try_url(url, tmp_gz)
                    if success:
                        try:
                            print(f"    Unzipping...", flush=True)
                            with gzip.open(tmp_gz, "rb") as f_in, open(out_txt, "wb") as f_out:
                                shutil.copyfileobj(f_in, f_out)
                            if out_txt.stat().st_size > 1000:
                                ok = True
                                used_version = ver
                                used_mode = "mono"
                                break
                        except Exception as e:
                            log(f"    Gunzip failed: {e}")
                if ok: break

        # REPORTING
        if ok:
            lines, toks = count(out_txt)
            log(f"[OK] {lang}: {lines} lines ({used_mode} @ {used_version})")
            rows.append({
                "language": lang,
                "lines": lines,
                "tokens_approx": toks,
                "corpus": "OpenSubtitles",
                "release_used": used_version,
                "pair_used": used_mode,
                "downloaded_at": datetime.now(timezone.utc).isoformat()
            })
        else:
            log(f"[FAIL] {lang} - Could not find valid data on any mirror.")
            rows.append({
                "language": lang,
                "lines": 0,
                "tokens_approx": 0,
                "corpus": "OpenSubtitles",
                "release_used": "FAILED",
                "pair_used": "FAILED",
                "downloaded_at": datetime.now(timezone.utc).isoformat()
            })

    # Write Summary
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["language", "lines", "tokens_approx", "corpus", "release_used", "pair_used", "downloaded_at"])
        w.writeheader()
        w.writerows(rows)
    
    print("\n------------------------------------------------")
    print(f"Done. Summary written to: {SUMMARY}")
    print(f"Log file at: {LOG}")

if __name__=="__main__":
    main()

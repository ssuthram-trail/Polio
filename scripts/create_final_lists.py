import time
import requests
import urllib.parse
import csv

BASE_URL = "https://rest.genenames.org"
HEADERS = {"Accept": "application/json"}

def resolve_symbol(old_symbol):
    query = f'symbol:"{old_symbol}" OR prev_symbol:"{old_symbol}" OR alias_symbol:"{old_symbol}"'
    encoded_query = urllib.parse.quote(query)
    url = f"{BASE_URL}/search/{encoded_query}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        docs = response.json().get("response", {}).get("docs", [])
        if docs: return docs[0].get("symbol")
    except Exception: pass
    return None

def main():
    # 1. Load HGNC base list (526)
    hgnc_current = set()
    with open('human_proteases_detailed_20260320_110919.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['symbol']: hgnc_current.add(row['symbol'].strip().upper())
            
    # 2. Load the exact overlap (251)
    overlap = set()
    with open('proteases_overlap.txt', 'r', encoding='utf-8') as f:
        overlap = set(line.strip().upper() for line in f if line.strip())
        
    print("Fetching resolutions for the paper-only variants...")
    master_combined = set(overlap)
    unmapped = []
    
    # 3. Resolve the 287 paper-only genes
    with open('proteases_paper_only.txt', 'r', encoding='utf-8') as f:
        paper_genes = [line.strip().upper() for line in f if line.strip()]
        
    for i, old_sym in enumerate(paper_genes):
        if (i+1) % 50 == 0: print(f"Resolved {i+1}/{len(paper_genes)}...")
        current_sym = resolve_symbol(old_sym)
        
        if current_sym:
            # If it already existed in HGNC base list OR is entirely new, we add it to our master list
            master_combined.add(current_sym.upper())
        else:
            unmapped.append(old_sym)
        time.sleep(0.05)
        
    # Write master combined list (251 overlap + 44 remapped overlap + 188 newly discovered = 483 genes)
    with open('master_combined_proteases.txt', 'w') as f:
        for p in sorted(master_combined):
            f.write(p + "\n")
            
    # Write unmapped genes
    with open('unmapped_paper_proteases.txt', 'w') as f:
        for p in sorted(unmapped):
            f.write(p + "\n")
            
    print(f"\nCreated 'master_combined_proteases.txt' with {len(master_combined)} verified HGNC gene symbols.")
    print(f"Created 'unmapped_paper_proteases.txt' with {len(unmapped)} unresolved historical symbols.")

if __name__ == '__main__':
    main()

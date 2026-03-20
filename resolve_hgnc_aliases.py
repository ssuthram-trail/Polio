import time
import requests
import urllib.parse

BASE_URL = "https://rest.genenames.org"
HEADERS = {"Accept": "application/json"}

def resolve_symbol(old_symbol):
    """
    Search HGNC for a symbol, including its previous symbols and aliases.
    Returns the current approved symbol if found, else None.
    """
    # Enclose the symbol in double quotes for an exact match within the search fields
    query = f'symbol:"{old_symbol}" OR prev_symbol:"{old_symbol}" OR alias_symbol:"{old_symbol}"'
    encoded_query = urllib.parse.quote(query)
    
    url = f"{BASE_URL}/search/{encoded_query}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        docs = data.get("response", {}).get("docs", [])
        if docs:
            # Sort by score or status if multiple, but returning the first hit's approved symbol is usually right
            # We want the 'symbol' from the highest scoring document
            return docs[0].get("symbol")
            
    except Exception as e:
        print(f"Error querying {old_symbol}: {e}")
        
    return None

def main():
    # Load 2026 HGNC list to compare against
    hgnc_current = set()
    with open('human_proteases_detailed_20260320_110919.csv', 'r', encoding='utf-8') as f:
        # Skip header
        next(f)
        for line in f:
            parts = line.split(',')
            if len(parts) > 1:
                hgnc_current.add(parts[1].strip().upper())
                
    resolved_count = 0
    now_in_hgnc_query = 0
    new_approved_symbols = []
    unresolved = []
    
    print("Resolving old symbols from Puente 2003 against HGNC... please wait.")
    
    with open('proteases_paper_only.txt', 'r', encoding='utf-8') as f:
        paper_genes = [line.strip().upper() for line in f if line.strip()]
        
    for i, old_sym in enumerate(paper_genes):
        if (i+1) % 50 == 0:
            print(f"Processed {i+1}/{len(paper_genes)} symbols...")
            
        current_sym = resolve_symbol(old_sym)
        
        if current_sym:
            resolved_count += 1
            if current_sym.upper() in hgnc_current:
                now_in_hgnc_query += 1
            else:
                new_approved_symbols.append((old_sym, current_sym))
        else:
            unresolved.append(old_sym)
            
        # tiny sleep to be polite to HGNC API
        time.sleep(0.05)
        
    print(f"\n--- Resolution Results ---")
    print(f"Total old symbols checked: {len(paper_genes)}")
    print(f"Successfully resolved to a current HGNC symbol: {resolved_count}")
    print(f"Of those resolved, {now_in_hgnc_query} ALREADY existed in our HGNC peptide/protease query under their new name!")
    print(f"Newly discovered functional proteases missed by our keyword search: {len(new_approved_symbols)}")
    print(f"Could not map to any HGNC symbol: {len(unresolved)}")
    
    # Save the newly discovered but missed genes
    if new_approved_symbols:
        with open('missed_but_approved_proteases.txt', 'w') as f:
            for old, current in new_approved_symbols:
                f.write(f"{old} -> {current}\n")
        print("\nSaved the newly discovered (but unqueried) approved genes to 'missed_but_approved_proteases.txt'")

if __name__ == '__main__':
    main()

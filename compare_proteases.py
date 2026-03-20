import csv

def compare_lists(hgnc_csv, paper_txt):
    # Load HGNC genes
    hgnc_genes = set()
    with open(hgnc_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['symbol']:
                hgnc_genes.add(row['symbol'].strip().upper())
                
    # Load paper genes
    paper_genes = set()
    with open(paper_txt, 'r', encoding='utf-8') as f:
        for line in f:
            symbol = line.strip().upper()
            if symbol:
                paper_genes.add(symbol)
                
    # Comparisons
    overlap = hgnc_genes.intersection(paper_genes)
    hgnc_only = hgnc_genes - paper_genes
    paper_only = paper_genes - hgnc_genes
    
    print(f"Total in HGNC list: {len(hgnc_genes)}")
    print(f"Total in Puente 2003 list: {len(paper_genes)}")
    print(f"Overlap (in both): {len(overlap)}")
    print(f"Only in HGNC: {len(hgnc_only)}")
    print(f"Only in Puente 2003: {len(paper_only)}")
    
    # Save the overlap to a file
    with open('proteases_overlap.txt', 'w') as f:
        for p in sorted(overlap):
            f.write(p + "\n")
            
    with open('proteases_hgnc_only.txt', 'w') as f:
        for p in sorted(hgnc_only):
            f.write(p + "\n")
            
    with open('proteases_paper_only.txt', 'w') as f:
        for p in sorted(paper_only):
            f.write(p + "\n")
            
    print("\nDetailed lists saved to: proteases_overlap.txt, proteases_hgnc_only.txt, and proteases_paper_only.txt")

if __name__ == '__main__':
    compare_lists('human_proteases_detailed_20260320_110919.csv', 'human_proteases_puente2003.txt')

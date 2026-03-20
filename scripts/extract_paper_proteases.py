import os
import re

def parse_txt_files(pdf_dir):
    human_proteases = []
    
    # Regex to match lines starting with MEROPS code: e.g. A01.001, C01.002, Ax1.xxx, S01.123np
    line_pattern = re.compile(r'^([ACMSTU][0-9A-Za-z]{2}\.[x0-9]{3}[a-z]*)\s+(.*?)$')
    
    # Look for locus link pattern to anchor the human gene
    # e.g., " BACE 23621 11q23 "
    # gene name could be "#CYMP", "PGA3/4/5", etc.
    # We can match: string of caps/nums/symbols followed by space, number, space, and locus (e.g. 11q23)
    # Actually, some genes are missing from human, so they're blank, but the locus might be blank too.
    # "Ax1.xxxnp seminal vesicle antigen    Sva 20939 6B2"
    # "A01.010 cathepsin E CTSE 1510 (1q31) Ctse 13034 1E4 y 82"
    # "A01.006 chymosin #CYMP 1542 1p13 Cymp 229697 3F3 y"
    
    for filename in sorted(os.listdir(pdf_dir)):
        if filename.endswith(".txt"):
            filepath = os.path.join(pdf_dir, filename)
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    m = line_pattern.match(line)
                    if m:
                        rest = m.group(2)
                        # Let's try to extract the human gene symbol.
                        # It is the token before a number (LocusLink ID) which is before a Locus (like 11p15 or (1q31) or 1p36 or unknown)
                        # We can use regex: \s([A-Z0-9/#\-]+)\s+(\d+)\s+(\(?[0-9XY]{1,2}[pq].*?\)?)
                        # Some genes don't have human locus link?
                        # Let's try matching:
                        match_gene = re.search(r'\s([A-Z0-9#/\-]+)\s+(\d+)\s+(\(?[0-9XY]{1,2}[pq][a-zA-Z0-9]*\)?|(mitochondria)|(unknown)|(Un))', rest)
                        if match_gene:
                            human_gene = match_gene.group(1).lstrip('#')
                            human_proteases.append(human_gene)
                        else:
                            # Let's print out lines that didn't match so we can improve regex
                            # print("No match:", line)
                            pass
                            
    # Remove duplicates
    human_proteases = list(dict.fromkeys(human_proteases))
    print(f"Extracted {len(human_proteases)} human proteases.")
    
    with open(os.path.join(pdf_dir, "human_proteases_paper.txt"), "w") as f:
        for p in human_proteases:
            f.write(p + "\n")
            
parse_txt_files("/Users/silpasuthram/Documents/Projects/Polio/paper_supps")

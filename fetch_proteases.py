import requests
import json
import csv
import urllib.parse
from datetime import datetime

# Base URL for the HGNC REST API
BASE_URL = "https://rest.genenames.org"

# Headers required by the API
HEADERS = {
    "Accept": "application/json"
}

def query_hgnc_search(query_term):
    """
    Query the HGNC 'search' endpoint to get matching HGNC IDs based on a query term.
    """
    # URL encode the query term
    encoded_query = urllib.parse.quote(query_term)
    
    url = f"{BASE_URL}/search/{encoded_query}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        # Extract the list of documents (genes)
        docs = data.get("response", {}).get("docs", [])
        
        results = []
        for doc in docs:
            # We mostly care about ID, Symbol, and Score from the search endpoint
            results.append({
                "hgnc_id": doc.get("hgnc_id"),
                "symbol": doc.get("symbol"),
                "score": doc.get("score")
            })
            
        print(f"Found {len(results)} genes for query: '{query_term}'")
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying HGNC: {e}")
        return []

def fetch_gene_details(hgnc_id):
    """
    Fetch full details for a specific gene using its HGNC ID.
    (Note: This is slower so we only use it if we need extra fields not in search)
    """
    url = f"{BASE_URL}/fetch/hgnc_id/{hgnc_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        docs = data.get("response", {}).get("docs", [])
        if docs:
            return docs[0]
        return None
        
    except requests.exceptions.RequestException as e:
        print("Error fetching details for {hgnc_id}: {e}")
        return None

def fetch_all_human_proteases():
    """
    Fetches a comprehensive list of human proteases/peptidases.
    Uses multiple queries to catch different terminology.
    """
    print("Starting fetch of human proteases from HGNC...")
    all_genes = {} # Use dict to deduplicate by hgnc_id
    
    # We will search for both "protease" and "peptidase" in the approved gene names,
    # ensuring they have the status "Approved".
    # HGNC's Solr-based search allows for wildcards and boolean operators.
    
    queries = [
        # Search for generic names
        'name:*protease* AND status:Approved',
        'name:*peptidase* AND status:Approved',
        
        # Search for specific known protease families in the name
        'name:*trypsin* AND status:Approved',
        'name:*cathepsin* AND status:Approved',
        'name:*caspase* AND status:Approved',
        'name:*kallikrein* AND status:Approved',
        'name:*metalloproteinase* AND status:Approved',
        'name:*calpain* AND status:Approved',
        'name:*secretase* AND status:Approved',
    ]
    
    for query in queries:
        print(f"\nRunning query: {query}")
        results = query_hgnc_search(query)
        
        for gene in results:
            gene_id = gene['hgnc_id']
            if gene_id not in all_genes:
                all_genes[gene_id] = gene
                
    
    print(f"\nTotal unique proteases/peptidases found: {len(all_genes)}")
    return list(all_genes.values())

def save_to_csv(genes, filename=None):
    """
    Saves the list of genes to a CSV file.
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"human_proteases_hgnc_{timestamp}.csv"
        
    if not genes:
        print("No genes to save. Exiting.")
        return
        
    fieldnames = ["hgnc_id", "symbol", "query_score"]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for gene in genes:
                writer.writerow({
                    "hgnc_id": gene.get("hgnc_id", ""),
                    "symbol": gene.get("symbol", ""),
                    "query_score": gene.get("score", "")
                })
        print(f"\nSuccessfully saved {len(genes)} genes to {filename}")
        
    except IOError as e:
        print(f"Error saving to file: {e}")

if __name__ == "__main__":
    proteases = fetch_all_human_proteases()
    
    if proteases:
        # Ask if they want to fetch full details
        fetch_details = input(f"Do you want to fetch full details (name, location, entrez_id, ensembl_id) for all {len(proteases)} genes? This will make {len(proteases)} separate API calls and take a few minutes. (y/n): ")
        
        if fetch_details.lower().startswith('y'):
            print("Fetching detailed information... Please wait.")
            detailed_genes = []
            
            for i, gene in enumerate(proteases):
                if (i+1) % 50 == 0:
                    print(f"Processed {i+1}/{len(proteases)} genes...")
                    
                details = fetch_gene_details(gene['hgnc_id'])
                if details:
                    detailed_genes.append(details)
                else:
                    # Keep basic info if fetch fails
                    detailed_genes.append(gene)
                    
            # Save detailed CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"human_proteases_detailed_{timestamp}.csv"
            
            # Use a broader set of fieldnames for detailed results
            fieldnames = ["hgnc_id", "symbol", "name", "locus_type", "location", "entrez_id", "ensembl_gene_id", "uniprot_ids", "gene_group"]
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for gene in detailed_genes:
                    # Convert lists to strings for CSV
                    if isinstance(gene.get("uniprot_ids"), list):
                        gene["uniprot_ids"] = "|".join(gene["uniprot_ids"])
                    if isinstance(gene.get("gene_group"), list):
                        gene["gene_group"] = "|".join(gene["gene_group"])
                        
                    writer.writerow(gene)
                    
            print(f"\nSuccessfully saved {len(detailed_genes)} detailed genes to {filename}")
            
        else:
            save_to_csv(proteases)

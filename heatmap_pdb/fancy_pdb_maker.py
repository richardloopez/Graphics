import csv
from Bio.PDB import PDBParser, PDBIO
import argparse

# Extract the info from the .csv
def extract_interactions_from_csv(csv_file):
    interactions = {}
    with open(csv_file, 'r', newline='') as file: 
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            residue_number = int(row['R2'])
            interaction = float(row['TOTAL_AV'])
            interactions[residue_number] = interaction
        return interactions

def gap_protein_residues(interactions, protein_gap):
    gap = int(protein_gap)
    return {res_num + gap: val for res_num, val in interactions.items()}

def map_interactions_to_pdb(input_pdb, output_pdb, interactions_dict):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('protein', input_pdb)
    
    found_count = 0
 
    for model in structure:
        for chain in model:
            for residue in chain:
                res_num = residue.id[1]
                
                if res_num in interactions_dict:
                    value = interactions_dict[res_num] * -1 # Multiply by -1 to invert the values, so that higher interactions have higher B-factors
                    found_count += 1
                    for atom in residue:
                        atom.set_bfactor(value)
                else:
                    for atom in residue:
                        print(f"Residue {res_num} not found in interactions, setting B-factor to 0.0")
                        atom.set_bfactor(0.0)

    io = PDBIO()
    io.set_structure(structure)
    io.save(output_pdb)
    print(f"Found {found_count} residues with interactions.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map CSV interactions to PDB structure")
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("protein_gap", help="Protein gap (it may not begin in resid 1, it may begin in resid 10, etc.)")
    parser.add_argument("input_pdb", help="Path to input PDB file")
    parser.add_argument("output_pdb", help="Path to output PDB file")
    args = parser.parse_args()

    interactions = extract_interactions_from_csv(args.input_csv)
    interactions_gapped = gap_protein_residues(interactions, args.protein_gap)
    map_interactions_to_pdb(args.input_pdb, args.output_pdb, interactions_gapped)
    print(f"Processed: {args.input_csv} -> {args.output_pdb}")
import nbformat
import glob
import os

def normalize_notebooks():
    """Normalize notebook files to add missing ID fields"""
    notebook_files = glob.glob('CSS/*.ipynb')
    
    for notebook_path in notebook_files:
        print(f"Normalizing {os.path.basename(notebook_path)}...")
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Normalize the notebook to add missing IDs
        nbformat.validate(nb)
        
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
    print(f"Normalized {len(notebook_files)} notebook files.")

if __name__ == "__main__":
    normalize_notebooks()
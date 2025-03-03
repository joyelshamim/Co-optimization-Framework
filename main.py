import os
import sys
import glob
import subprocess
import tempfile
import time
import shutil

# Create the required folder structure if it doesn't exist
os.makedirs('CSS', exist_ok=True)

def list_available_models():
    """Display available model notebooks in the CSS folder"""
    if not os.path.exists('CSS'):
        print("CSS folder not found. Please ensure your folder structure is correct.")
        return {}

    notebook_files = glob.glob('CSS/*.ipynb')
    
    if not notebook_files:
        print("No model files found in the CSS folder.")
        return {}
    
    # Create a dictionary mapping numbers to file paths
    models = {}
    print("\nAvailable optimization models:")
    print("----------------------------------")
    for i, filepath in enumerate(sorted(notebook_files), 1):
        filename = os.path.basename(filepath)
        # Format filename for display
        display_name = filename.replace('.ipynb', '').replace('_', ' ')
        
        models[i] = {
            'path': filepath,
            'name': display_name
        }
        print(f"{i}. {display_name}")
    print("----------------------------------")
    
    return models

def modify_notebook_imports(notebook_path):
    """Modify the notebook to add proper import paths for config.py"""
    import nbformat
    
    try:
        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Create a new cell to add at the beginning to fix imports
        import_fix_cell = {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'source': '# Added by run script to fix imports\n'
                      'import sys\n'
                      'import os\n'
                      'sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))\n'
                      'print("Import paths have been set up to find config.py in the root directory.")\n',
            'outputs': []
        }
        
        # Add the import fix cell at the beginning
        nb.cells.insert(0, import_fix_cell)
        
        # Write the modified notebook to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.ipynb')
        os.close(fd)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        return temp_path
        
    except Exception as e:
        print(f"Error modifying notebook: {e}")
        return notebook_path

def run_notebook_with_subprocess(notebook_path, output_file=None):
    """Run a notebook using nbconvert via subprocess"""
    try:
        # Modify the notebook to fix imports
        modified_notebook_path = modify_notebook_imports(notebook_path)
        
        # Create a temporary file for output if none provided
        if output_file is None:
            fd, output_file = tempfile.mkstemp(suffix='.ipynb')
            os.close(fd)
        
        print(f"Running model from: {os.path.basename(notebook_path)}")
        print("This may take a minute...\n")
        
        # Run the notebook using nbconvert
        cmd = [
            sys.executable, 
            '-m', 'nbconvert', 
            '--to', 'notebook', 
            '--execute',
            '--output', output_file,
            modified_notebook_path
        ]
        
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait for the process to complete with a timeout
        try:
            stdout, stderr = process.communicate(timeout=600)  # 10 minute timeout
            if process.returncode != 0:
                stderr_text = stderr.decode('utf-8', errors='replace')
                print(f"Error executing notebook: {stderr_text}")
                return None
            print("\nModel execution completed successfully!")
            return output_file
        except subprocess.TimeoutExpired:
            process.kill()
            print("Execution timed out (10 minutes)")
            return None
            
    except Exception as e:
        print(f"Error executing notebook: {str(e)}")
        return None

def extract_results_from_file(output_file):
    """Extract optimization results from the output file"""
    try:
        if output_file is None or not os.path.exists(output_file):
            return "No results to display."
        
        # Read the file as a notebook
        import nbformat
        with open(output_file, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        results = []
        in_results_section = False
        
        for cell in nb.cells:
            if cell.cell_type == 'code' and cell.outputs:
                for output in cell.outputs:
                    if 'text' in output and '===== SIMULATION RESULTS =====' in str(output.get('text', '')):
                        in_results_section = True
                        results.append(output.get('text', ''))
                    elif 'text' in output and in_results_section:
                        results.append(output.get('text', ''))
        
        if results:
            return ''.join(results)
        else:
            # Try to find any output that might contain optimization results
            for cell in nb.cells:
                if cell.cell_type == 'code' and cell.outputs:
                    for output in cell.outputs:
                        if 'text' in output and any(term in str(output.get('text', '')) for term in 
                                                 ['SIMULATION RESULTS', 'System-wide Summary', 'Vehicle Routing Summary']):
                            results.append(output.get('text', ''))
            
            if results:
                return ''.join(results)
            else:
                return "No optimization results found in the output."
    
    except Exception as e:
        print(f"Error extracting results: {str(e)}")
        return "Error extracting results from the output file."

# Removed save_results_to_file and save_visualizations functions as they're no longer needed

def run_model(choice, models):
    """Run the selected model and display results"""
    if not models or choice not in models:
        print(f"Invalid selection: {choice}. Please select a valid number.")
        return
    
    selected = models[choice]
    print(f"Running optimization model: {selected['name']}\n")
    
    # Check if the notebook exists in CSS folder
    if not os.path.exists(selected['path']):
        print(f"Error: Model not found at {selected['path']}.")
        print("Make sure all model notebooks are in the CSS folder.")
        return
    
    # Make sure Result folder exists
    os.makedirs('Result', exist_ok=True)
    
    # Execute the notebook
    output_file = run_notebook_with_subprocess(selected['path'])
    
    # Extract and display results
    if output_file:
        results = extract_results_from_file(output_file)
        print("\n=== OPTIMIZATION RESULTS ===")
        print(results)
        
        # Clean up temporary files
        try:
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # Clean up the modified notebook file if it exists and is different from the original
            modified_notebook_path = modified_notebook_path if 'modified_notebook_path' in locals() else None
            if modified_notebook_path and os.path.exists(modified_notebook_path) and modified_notebook_path != notebook_path:
                os.remove(modified_notebook_path)
        except Exception as e:
            print(f"Warning: Failed to clean up temporary files: {str(e)}")

def list_results():
    """List any result files"""
    print("Result viewing functionality has been removed as requested.")
    print("Results are only displayed during model execution.")

def setup_environment():
    """Set up the environment for running models"""
    # Make sure the config.py file is accessible from the CSS folder
    root_config_path = os.path.join(os.getcwd(), 'config.py')
    css_config_path = os.path.join(os.getcwd(), 'CSS', 'config.py')
    
    if os.path.exists(root_config_path) and not os.path.exists(css_config_path):
        print("Setting up environment: Making config.py accessible to models...")
        
        try:
            # For Windows, create a copy of the file (symlinks require admin privileges)
            if os.name == 'nt':
                import shutil
                shutil.copy2(root_config_path, css_config_path)
                print("Created a copy of config.py in the CSS folder")
            else:
                # For Unix-like systems, create a symbolic link
                os.symlink(os.path.abspath(root_config_path), css_config_path)
                print("Created a symbolic link to config.py in the CSS folder")
        except Exception as e:
            print(f"Warning: Failed to set up config.py access: {str(e)}")
            print("Models may fail to run if they cannot import the config module.")
    
    # Make sure Dataset folder is directly accessible from the CSS folder if needed
    if not os.path.exists('CSS/Dataset') and os.path.exists('Dataset'):
        print("Setting up Dataset folder access for models...")
        try:
            # For Windows, create a directory junction (symlinks require admin privileges)
            if os.name == 'nt':
                import subprocess
                subprocess.run(['mklink', '/J', 'CSS\\Dataset', os.path.abspath('Dataset')], shell=True)
                print("Created a directory junction to Dataset folder in the CSS folder")
            else:
                # For Unix-like systems, create a symbolic link
                os.symlink(os.path.abspath('Dataset'), 'CSS/Dataset')
                print("Created a symbolic link to Dataset folder in the CSS folder")
        except Exception as e:
            print(f"Warning: Failed to set up Dataset folder access: {str(e)}")
            print("Models may fail to run if they cannot find the Dataset folder.")


def main():
    print("=" * 60)
    print("MOBILE ENERGY STORAGE OPTIMIZATION TOOL")
    print("=" * 60)
    print("\nThis tool allows you to run different optimization models for Mobile Energy Storage Systems (MESS).")
    
    # Set up the environment
    setup_environment()
    
    # List available models
    models = list_available_models()
    
    if not models:
        print("No optimization models found. Please add notebook files to the CSS folder.")
        return
    
    while True:
        print("\nSelect an option:")
        print("1. Run a specific optimization model")
        print("2. List generated results")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            selection = input("\nEnter the number of the model to run: ")
            try:
                selection = int(selection)
                run_model(selection, models)
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '2':
            list_results()
        
        elif choice == '3':
            print("Exiting the program.")
            break
        
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()

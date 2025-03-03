import os

def get_project_root() -> str:
    """
    Return the absolute path to the project root directory.
    This function intelligently detects if it's being called from the CSS subfolder
    and adjusts the path accordingly.
    """
    file_path = os.path.abspath(__file__)
    
    # Check if this file is in the CSS folder
    if os.path.basename(os.path.dirname(file_path)) == 'CSS':
        # If in CSS folder, go up one level to the project root
        return os.path.dirname(os.path.dirname(file_path))
    else:
        # If in project root, return current directory
        return os.path.dirname(file_path)

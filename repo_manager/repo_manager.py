import os
import logging
import requests
import shutil
from urllib.parse import urlparse
from git import Repo, exc  # Requires: pip install gitpython

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepoManager:
    """
    A tool to handle git repository operations for a Windows Desktop Application.
    """

    def __init__(self, default_save_path=None):
        """
        Initialize the manager.
        
        Args:
            default_save_path (str): Default local folder to save cloned repos. 
                                     Defaults to './downloaded_repos' if None.
        """
        if default_save_path:
            self.default_save_path = default_save_path
        else:
            self.default_save_path = os.path.join(os.getcwd(), "downloaded_repos")
            
        if not os.path.exists(self.default_save_path):
            os.makedirs(self.default_save_path)

    def _get_repo_name_from_url(self, url):
        """Extracts the repository name from the URL."""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return path_parts[-1].replace('.git', '')
        return "unknown_repo"

    def clone_repo(self, repo_url, local_path=None):
        """
        Clones a remote repository to the local machine.
        
        Args:
            repo_url (str): The HTTP/HTTPS URL of the git repository.
            local_path (str, optional): The specific folder where the user wants to clone.
                                        If None, uses self.default_save_path + repo name.
        
        Returns:
            str: The full path to the cloned repository.
        """
        repo_name = self._get_repo_name_from_url(repo_url)
        
        # Determine the final destination directory
        if local_path:
            # If user provided a specific folder (e.g., via a Folder Picker dialog)
            destination = os.path.join(local_path, repo_name)
        else:
            destination = os.path.join(self.default_save_path, repo_name)

        if os.path.exists(destination):
            logger.warning(f"Directory {destination} already exists.")
            # Option: Raise error, or maybe pull changes? 
            # For this example, we raise an error to let the UI handle it (e.g., "Overwrite?").
            raise FileExistsError(f" The folder '{repo_name}' already exists in that location.")

        try:
            logger.info(f"Cloning {repo_url} into {destination}...")
            # This runs the actual git clone operation
            Repo.clone_from(repo_url, destination)
            logger.info("Clone successful.")
            return destination
            
        except exc.GitCommandError as e:
            logger.error(f"Git clone failed: {e}")
            raise Exception(f"Git Error: Verify the URL is correct and Git is installed. Details: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def download_zip_fallback(self, repo_url, save_path=None):
        """
        Fallback: Downloads the repository as a ZIP if git clone fails or isn't desired.
        """
        repo_name = self._get_repo_name_from_url(repo_url)
        
        # Use provided path or default
        target_dir = save_path if save_path else self.default_save_path
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        local_filename = os.path.join(target_dir, f"{repo_name}.zip")
        
        # Construct ZIP URL (GitHub specific)
        clean_url = repo_url.rstrip('.git')
        zip_url = f"{clean_url}/archive/refs/heads/main.zip"

        try:
            logger.info(f"Attempting ZIP download from {zip_url}...")
            response = requests.get(zip_url, stream=True)
            
            if response.status_code == 404:
                zip_url = f"{clean_url}/archive/refs/heads/master.zip"
                response = requests.get(zip_url, stream=True)

            response.raise_for_status()

            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"ZIP Download complete: {local_filename}")
            return local_filename

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download zip: {e}")
            raise Exception("Failed to download ZIP archive.")

# Example Usage Block (Backend Logic with Demo UI)
if __name__ == "__main__":
    # We import tkinter here only for demonstration purposes.
    # In your real app, your UI framework (PyQt, Kivy, etc.) would handle the input.
    import tkinter as tk
    from tkinter import filedialog

    # Simulate a button click event in your Windows App
    manager = RepoManager()
    
    # This URL would come from your text input field
    test_url = "https://github.com/GitScopes/GitScope"
    
    print("Opening folder selection dialog...")
    
    # Initialize Tkinter root (hide the main window)
    root = tk.Tk()
    root.withdraw()

    # Open the folder selection dialog
    user_selected_path = filedialog.askdirectory(title="Select Target Folder for Clone")

    if user_selected_path:
        try:
            print(f"User clicked Clone for: {test_url}")
            print(f"Selected destination: {user_selected_path}")
            
            cloned_path = manager.clone_repo(test_url, user_selected_path)
            
            print(f"Success! Repository cloned to: {cloned_path}")
            # Here you would show a "Success" message box in your UI
            
        except FileExistsError as e:
            print(f"UI Message: {e}")
        except Exception as e:
            print(f"UI Error Alert: {e}")
    else:
        print("Operation cancelled: No folder selected.")
import json
import os
import tempfile

CACHE_FILE = "user_data_cache.json"

def load_cache():
    """Loads cache data from file. Deletes the file if corrupted."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            # Handle the corruption error
            print(f"ERROR: Corrupted cache file detected at {CACHE_FILE}. Deleting file and returning empty cache. Details: {e}")
            os.remove(CACHE_FILE)
            # Proceed to return an empty cache
            
    return {}

def save_cache(data):
    """Saves cache data to file atomically to prevent corruption."""
    # 1. Create a temporary file in the same directory
    # Using delete=False ensures the file stays until we move it
    temp_file_path = None
    
    # Get the directory of the final cache file
    cache_dir = os.path.dirname(CACHE_FILE) or '.'

    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=cache_dir) as tmp_file:
            json.dump(data, tmp_file, indent=4)
        
        temp_file_path = tmp_file.name
        
        # 2. If the write was successful, rename (atomically moves/overwrites) the temp file
        os.replace(temp_file_path, CACHE_FILE)

    except Exception as e:
        print(f"Error during atomic cache save: {e}")
        # Clean up the temporary file if it was created but the save failed
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        # You might want to re-raise the exception or handle it gracefully
        raise
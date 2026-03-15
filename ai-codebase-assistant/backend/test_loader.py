import os
from code_loader import load_codebase

def run_test():
    # Path to the data directory relative to this script
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    print(f"--- Testing load_codebase on: {os.path.abspath(data_dir)} ---")
    
    try:
        files = load_codebase(data_dir)
        print(f"Files found: {len(files)}")
        
        if files:
            first_file = files[0]
            print(f"\nFirst file: {first_file['file_name']}")
            print(f"Path: {first_file['file_path']}")
            print("-" * 20)
            # Preview first 200 characters of content
            preview = first_file['code_content'][:200]
            print(preview + ("..." if len(first_file['code_content']) > 200 else ""))
            print("-" * 20)
        else:
            print("No supported code files found in the data directory.")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    run_test()

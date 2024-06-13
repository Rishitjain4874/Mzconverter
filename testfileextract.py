import os
import shutil

def find_and_copy_files(root_dir, new_dir):
    # Create the new directory if it doesn't exist
    os.makedirs(new_dir, exist_ok=True)

    # Initialize a counter for naming the new files
    file_counter = 17

    # Walk through the directory structure
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'Ultra_Format':
                # Construct the full file path
                file_path = os.path.join(dirpath, filename)
                
                # Construct the new file name and path
                new_file_name = f'test{file_counter}.udlf'
                new_file_path = os.path.join(new_dir, new_file_name)
                
                # Copy the file to the new directory with the new name
                shutil.copy(file_path, new_file_path)
                
                # Increment the counter
                file_counter += 1

    print(f"Copied {file_counter - 1} files to {new_dir}")

# Define the root directory to search and the new directory to store renamed files
root_directory = 'Configuration'
new_directory = 'UDLF files'

# Call the function
find_and_copy_files(root_directory, new_directory)

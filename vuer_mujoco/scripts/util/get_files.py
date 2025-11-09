import os


def get_all_files_in_directory(directory):
    """
    Recursively retrieves all files in a given directory with their full paths.

    :param directory: Path to the directory to search
    :return: List of full file paths
    """
    file_paths = []  # List to store the file paths

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Construct the full file path
            full_path = os.path.join(root, file)
            file_paths.append(full_path)

    return file_paths


# Example usage
if __name__ == "__main__":
    directory_to_search = "./"  # Replace with the directory path
    all_files = get_all_files_in_directory(directory_to_search)

    print("\nList of Files:")
    for file_path in all_files:
        print(file_path)

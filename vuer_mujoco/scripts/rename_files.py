import os
import glob

# Define the directory containing the robocasa_scenes files
directory = "robocasa_scenes/"
# Pattern for matching files
pattern = os.path.join(directory, "layout*-style*.xml")

# Find all the files matching the pattern
files = glob.glob(pattern)

for file_path in files:
    # Extract the file name from the full path
    file_name = os.path.basename(file_path)

    # Parse the layout and style parts of the file name
    if "layout" in file_name and "style" in file_name:
        try:
            layout_part, style_part = file_name.split(".")[0].split("-")
            layout_number = int(layout_part.replace("layout", ""))
            style_number = int(style_part.replace("style", ""))

            # Generate the new file name with zero-padded numbers
            new_file_name = f"layout{layout_number:04d}-style{style_number:04d}.xml"

            # Get the full path for the new file name
            new_file_path = os.path.join(directory, new_file_name)

            # Rename the file
            os.rename(file_path, new_file_path)
            print(f"Renamed: {file_path} -> {new_file_path}")
        except ValueError:
            print(f"Skipping invalid file name format: {file_name}")
    else:
        print(f"Skipping: {file_name}")
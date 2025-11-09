import os
import trimesh

# Define the input and output folder paths
input_folder = 'assets_stl'
output_folder = 'assets'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.stl'):  # Check if the file is an STL
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + '.obj'  # Change extension to .obj
        output_path = os.path.join(output_folder, output_filename)

        # Load the STL file
        mesh = trimesh.load(input_path)

        if mesh.is_empty:
            print(f"Failed to load {filename}")
            continue

        # Export the mesh as an OBJ file
        mesh.export(output_path)
        print(f"Converted {filename} to {output_filename}")

print("Conversion complete!")
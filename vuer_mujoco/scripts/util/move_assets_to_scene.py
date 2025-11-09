import os
import shutil

from tqdm import tqdm


def move_assets_to_scene(asset_paths, scene_root):
    """
    Moves asset files to a new root folder while preserving the folder structure.

    Args:
    asset_paths (list): List of asset file paths to be moved.
    scene_root (str): Path to the new root folder (e.g., 'scene_0001').

    """
    if not os.path.exists(scene_root):
        os.makedirs(scene_root)

    it = tqdm(asset_paths, desc="Moving assets", unit="asset")

    for asset_path in it:
        # Get the directory structure relative to the current working directory
        if not os.path.isabs(asset_path):
            asset_path = os.path.abspath(asset_path)

        relative_path = os.path.relpath(asset_path)

        # Create the new destination path under scene_root
        destination_path = os.path.join(scene_root, relative_path)
        destination_dir = os.path.dirname(destination_path)

        # Ensure the destination directory exists
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # Copy the file to the new location
        shutil.copy2(asset_path, destination_path)
        it.write(f"{asset_path} -> {destination_path}")


if __name__ == "__main__":
    # Example list of asset file paths (these can be absolute or relative paths)
    asset_files = [
        "assets/textures/wood.jpg",
        "assets/models/chair.obj",
        "assets/models/table.obj",
    ]

    # Root folder to relocate the assets
    new_scene_root = "scene_0001"

    # Move the assets
    move_assets_to_scene(asset_files, new_scene_root + "/scene.mjcf.xml")

import os
import shutil


def move_to(asset_paths: list, scene_root: str) -> list:
    """
    Moves a scene file and associated assets to a new root folder while preserving their structure.

    Args:
        asset_paths (list): List of asset file paths to be moved. Paths can be absolute or relative.
        scene_file (str): Path to the scene file to be moved. Can be absolute or relative.
        scene_root (str): Path to the new root folder (e.g., 'scene_0001'). Will be created if it doesn't exist.

    Returns:
        list: List of all files moved to their new locations.
    """
    os.makedirs(scene_root, exist_ok=True)

    # Rename the scene file to 'mjcf.xml' in the destination
    # scene_destination = os.path.join(scene_root, "scene.mjcf.xml")
    # shutil.copy2(scene_file_abs, scene_destination)
    # print(f"Moved and renamed: {scene_file_abs} -> {scene_destination}")

    moved_files = []

    # Move each asset
    for asset_path in asset_paths:
        if not os.path.isabs(asset_path):
            asset_path = os.path.abspath(asset_path)

        relative_path = os.path.relpath(asset_path)

        # Create the new destination path under scene_root
        destination_path = os.path.join(scene_root, relative_path)
        destination_dir = os.path.dirname(destination_path)

        # Ensure the destination directory exists
        os.makedirs(destination_dir, exist_ok=True)

        shutil.copy2(asset_path, destination_path)
        print(f"Moved: {asset_path} -> {destination_path}")

        moved_files.append(destination_path)

    return moved_files

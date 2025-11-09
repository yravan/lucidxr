import yaml
from params_proto import ParamsProto
from termcolor import colored

from vuer_mujoco.scripts.move_files import move_to
from vuer_mujoco.schemas.utils.collect_asset_paths import collect_asset_paths
from vuer_mujoco.scripts.util.prune_unused_assets import remove_unused_mesh
from vuer_mujoco.scripts.util.s3_file_upload_utils import upload_to_s3, upload_files_to_s3
from vuer_mujoco.scripts.util.working_directory_context_manager import WorkDir


class Args(ParamsProto):
    """parse mujoco scene, and upload to s3 as a standalone folder."""

    wd = "."  # "../../assets"

    scene_name = "layout0001-style0001"
    entrypoint_name = "scene.vuer.yml"

    # Path to the scene file
    source_scene = "robocasa_scenes_staging/{scene_name}.xml"

    # S3 target parths
    s3_bucket = "vuer-hub-production"
    s3_prefix = "robocasa-scenes/{scene_name}"
    s3_entrypoint = "{s3_prefix}/{entrypoint_name}"

    # Destination folder for the scene and assets
    local_prefix = "outputs/{scene_name}"
    clean_mjcf = "scene.mjcf.xml"
    local_asset_list = "scene_files.txt"

    def __post_init__(self, _deps=None):
        for k, v in self.__dict__.items():
            value = v.format(**self.__dict__)
            setattr(self, k, value)

            print(f"{colored(k, 'cyan')}:\t{colored(value, 'yellow')}")


def main():
    args = Args()

    # Clean the MJCF scene file by removing unused mesh elements, and
    # save to a new location
    remove_unused_mesh(args.source_scene, to=args.local_prefix + "/" + args.clean_mjcf)

    with WorkDir(args.local_prefix):
        # Dynamically extract the asset file paths from the MJCF scene file
        # DANGER: this ignores the <compiler meshdir="..."> attribute.
        source_list = collect_asset_paths(args.clean_mjcf)

    # Move the scene file (as 'mjcf.xml') and associated assets
    staged_list = move_to(source_list, args.local_prefix)

    with WorkDir(args.local_prefix):
        s3_list = upload_files_to_s3(
            [args.clean_mjcf, *source_list],
            args.s3_bucket,
            args.s3_prefix,
        )

        # Write the S3 file list to scene_files.txt
        with open(args.local_asset_list, "w") as f:
            f.write("\n".join(s3_list))

        # Save the scene data in YAML format
        scene_data = {
            "tag": "Scene",
            "children": [
                {
                    "tag": "MuJoCo",
                    "src": s3_list[0],
                    "assets": s3_list,
                }
            ],
        }

        with open(args.entrypoint_name, "w") as f:
            yaml.dump(scene_data, f)  # noqa: F821

        s3_list = upload_to_s3(args.entrypoint_name, args.s3_bucket, args.s3_entrypoint)


if __name__ == "__main__":
    main()

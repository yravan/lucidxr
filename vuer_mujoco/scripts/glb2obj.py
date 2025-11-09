from pathlib import Path

import trimesh
from trimesh.visual.material import SimpleMaterial


def convert_glb_to_obj(glb_file, obj_file, scale_factor=1.0):
    """Converts a GLB file to an OBJ file with optional scaling."""

    path = Path(obj_file)
    path.parent.mkdir(exist_ok=True, parents=True)
    print("created path:", path.parent)
    fname = path.name.split(".")[0]

    # Load the GLB file
    scene = trimesh.load(glb_file)

    def to_simple_patched(self):
        print("hey =>", self)

        def carried():
            new_mat = SimpleMaterial(image=self.baseColorTexture, diffuse=self.baseColorFactor)
            new_mat.name = self.name
            print(self.name)
            return new_mat

        return carried

    # If the scene is a single mesh, export it directly
    if isinstance(scene, trimesh.Trimesh):
        scene.export(obj_file)
    else:
        # If the scene contains multiple meshes, export each one
        for ind, mesh in enumerate(scene.geometry.values()):
            if mesh.is_empty:  # Skip empty mesh
                continue
            
            if scale_factor != 1.0:
                mesh.apply_scale(scale_factor)

            mesh.visual.material.to_simple = to_simple_patched(mesh.visual.material)
            mesh.visual.material.name = f"{fname}_{ind}"

            path = path.parent / f"{fname}_{ind}.obj"
            mesh.export(path, include_texture=True, mtl_name=f"{fname}_{ind}.mtl")


def main(**kwargs):
    from params_proto import ParamsProto, Proto, Flag

    class Args(ParamsProto, cli=False):
        # Usage example
        source = Proto("path/to/your/file.glb", help="Path to the GLB file")
        to = Proto("path/to/output/file.obj", help="Output path to save the OBJ file")
        scale = Proto(1.0, help="Scale factor to apply to the mesh")
        center = Flag(help="Center the mesh at the origin")

    Args._update(**kwargs)
    convert_glb_to_obj(Args.source, Args.to, scale_factor=Args.scale)


if __name__ == "__main__":
    main(
        source="/Users/yajvanravan/fortyfive/lucidxr/assets/sketchfab/process/pans/frying_pan.glb",
        to="../../assets/sketchfab/outputs/pans/frying_pan_1.obj",
        scale=0.001,
    )


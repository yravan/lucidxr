#!/usr/bin/env python
"""
OBJ Scaler - A simple command-line tool to scale OBJ 3D model files.

This script takes an OBJ file as input and scales it by the specified factor(s).

Usage:
  # Uniform scaling (same factor for all dimensions)
  python scale_obj.py input.obj --scale 0.5

  # Non-uniform scaling (different factors for x, y, z dimensions)
  python scale_obj.py input.obj --scale 0.1,0.2,0.3

  # Specify output file (default is input_scaled.obj)
  python scale_obj.py input.obj --scale 0.5 --output output.obj

  # Scale without preserving the model's center point
  python scale_obj.py input.obj --scale 0.5 --no-preserve-origin

  # Recenter the model to world origin (0,0,0) after scaling
  python scale_obj.py input.obj --scale 0.5 --recenter

  # Recenter the model on the XY plane only (preserving Z height)
  python scale_obj.py input.obj --scale 0.5 --recenter-xy

  # Recenter the model on the XZ plane only (preserving Y height)
  python scale_obj.py input.obj --scale 0.5 --recenter-xz

  # Enable verbose output
  python scale_obj.py input.obj --scale 0.5 --verbose

  # Multiple options together
  python scale_obj.py input.obj --scale 0.1,0.2,0.3 --output custom.obj --verbose --recenter

When --preserve-origin is enabled (default), the model maintains its center
position during scaling, expanding or contracting around its center point.
When disabled with --no-preserve-origin, scaling occurs relative to the
origin (0,0,0), which may change the model's position.

The --recenter option will move the object to be centered at world origin (0,0,0)
after scaling, regardless of the --preserve-origin setting.

The --recenter-xy option will center the object on the XY plane (setting X and Y
coordinates to 0) while preserving its Z height.

The --recenter-xz option will center the object on the XZ plane (setting X and Z
coordinates to 0) while preserving its Y height.
"""

import os
import sys
import numpy as np
from typing import Union, Tuple

from params_proto import ParamsProto, Proto, Flag


class ObjScalerParams(ParamsProto, cli_parse=True):
    """Parameters for scaling OBJ files.

    The parameters control how the OBJ file is scaled:
    - input_file: The path to the OBJ file to be scaled
    - scale: Either a single value for uniform scaling or three comma-separated values for X,Y,Z scaling
    - output: Where to save the scaled model (defaults to adding '_scaled' suffix to the input file)
    - no_preserve_origin: When False (default), scaling is done relative to the model's center point,
      preserving the average position of all vertices. This means the model expands/contracts
      around its center. When True, scaling is done relative to the world origin (0,0,0),
      which may shift the model's position as it scales.
    - recenter_xy: When True, center the object on the XY plane (setting X and Y coordinates to 0)
      while preserving its Z height after scaling
    - recenter_xz: When True, center the object on the XZ plane (setting X and Z coordinates to 0)
      while preserving its Y height after scaling
    - verbose: Provides detailed output during the scaling process
    """

    # Positional argument (handled separately)
    file = Proto(None, help="Path to the input OBJ file")

    output = Proto(None, help="Output file path (default: <input>_scaled.obj)")

    # Options
    scale = Proto(help="Scale factor(s). Use a single value for uniform scaling or comma-separated values (x,y,z) for non-uniform scaling")
    world_origin = Flag(help="Do not preserve the origin during scaling")
    recenter_xy = Flag(help="Center the object on the XY plane (setting X and Y coordinates to 0) while preserving Z height")
    recenter_xz = Flag(help="Center the object on the XZ plane (setting X and Z coordinates to 0) while preserving Y height")
    verbose = Flag(help="Enable verbose output")


def cli_entry_point():
    """Entry point for the console script defined in pyproject.toml."""
    main()


def parse_scale(scale_str: str) -> Union[float, Tuple[float, float, float]]:
    """Parse the scale parameter from string to either a single float or a tuple of three floats."""
    if scale_str is None:
        print("Error: Scale factor is required")
        sys.exit(1)

    if "," in scale_str:
        try:
            values = [float(x.strip()) for x in scale_str.split(",")]
            if len(values) == 3:
                return tuple(values)
            else:
                print(f"Error: Expected 3 values for x,y,z scaling, got {len(values)}")
                sys.exit(1)
        except ValueError as e:
            print(f"Error parsing scale values: {e}")
            sys.exit(1)
    else:
        try:
            return float(scale_str)
        except ValueError:
            print(f"Error: '{scale_str}' is not a valid scale factor")
            sys.exit(1)


def scale_obj(
    input_file: str,
    output_file: str,
    scale_factor: Union[float, Tuple[float, float, float]],
    preserve_origin: bool = True,
    recenter_xy: bool = False,
    recenter_xz: bool = False,
    verbose: bool = False,
) -> None:
    """
    Scale vertices in an OBJ file by given factor(s).

    Args:
        input_file: Path to input OBJ file
        output_file: Path to output OBJ file
        scale_factor: Either a single value for uniform scaling or tuple of (x,y,z) for non-uniform scaling
        preserve_origin: Whether to preserve the center point during scaling
        recenter_xy: Whether to center the object on the XY plane while preserving Z height
        recenter_xz: Whether to center the object on the XZ plane while preserving Y height
        verbose: Whether to print verbose information
    """
    if verbose:
        if isinstance(scale_factor, tuple):
            print(f"Scaling {input_file} by factors x:{scale_factor[0]}, y:{scale_factor[1]}, z:{scale_factor[2]}")
        else:
            print(f"Scaling {input_file} uniformly by factor {scale_factor}")

    # Initialize vertices list
    vertices = []
    other_lines = []

    # Read the input file
    try:
        with open(input_file, "r") as f:
            for line in f:
                if line.startswith("v "):  # Vertex line
                    vertices.append(line)
                else:
                    other_lines.append(line)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Process vertices
    new_vertices = []
    vertices_coords = []

    for v in vertices:
        parts = v.split()
        if len(parts) >= 4:  # Must have at least "v x y z"
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            vertices_coords.append((x, y, z))

    # Calculate center if preserving origin
    if preserve_origin and vertices_coords:
        center = np.mean(vertices_coords, axis=0)
    else:
        center = np.zeros(3)

    # Apply scaling to vertices
    for v in vertices:
        parts = v.split()
        if len(parts) >= 4:
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])

            # Apply scaling
            if isinstance(scale_factor, tuple):
                # Non-uniform scaling
                if preserve_origin:
                    x = center[0] + (x - center[0]) * scale_factor[0]
                    y = center[1] + (y - center[1]) * scale_factor[1]
                    z = center[2] + (z - center[2]) * scale_factor[2]
                else:
                    x *= scale_factor[0]
                    y *= scale_factor[1]
                    z *= scale_factor[2]
            else:
                # Uniform scaling
                if preserve_origin:
                    x = center[0] + (x - center[0]) * scale_factor
                    y = center[1] + (y - center[1]) * scale_factor
                    z = center[2] + (z - center[2]) * scale_factor
                else:
                    x *= scale_factor
                    y *= scale_factor
                    z *= scale_factor

            # Reconstruct the vertex line
            parts[1:4] = [str(x), str(y), str(z)]
            new_vertices.append(" ".join(parts) + "\n")
        else:
            new_vertices.append(v)  # Keep the line as is if it doesn't have enough components

    # Apply recentering if requested
    if (recenter_xy or recenter_xz) and new_vertices:
        # Extract coordinates from new vertices
        scaled_vertices = []
        for v in new_vertices:
            parts = v.split()
            if len(parts) >= 4:  # Must have at least "v x y z"
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                scaled_vertices.append((x, y, z))

        if scaled_vertices:
            # Calculate the new center after scaling
            new_center = np.mean(scaled_vertices, axis=0)

            # Apply recentering
            recentered_vertices = []
            for v in new_vertices:
                parts = v.split()
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])

                    # Recenter according to flags
                    if recenter_xy:
                        x -= new_center[0]
                        y -= new_center[1]
                    if recenter_xz:
                        x -= new_center[0]
                        z -= new_center[2]

                    parts[1:4] = [str(x), str(y), str(z)]
                    recentered_vertices.append(" ".join(parts) + "\n")
                else:
                    recentered_vertices.append(v)

            new_vertices = recentered_vertices

            if verbose:
                if recenter_xy:
                    print(f"Recentered object on XY plane by shifting X:{new_center[0]}, Y:{new_center[1]}")
                if recenter_xz:
                    print(f"Recentered object on XZ plane by shifting X:{new_center[0]}, Z:{new_center[2]}")

    # Write the output file
    try:
        with open(output_file, "w") as f:
            # Write vertices first
            for v in new_vertices:
                f.write(v)

            # Write all other lines
            for line in other_lines:
                f.write(line)

        if verbose:
            print(f"Scaled OBJ saved to {output_file}")

    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)


def main():
    """Main function to handle command-line arguments and execute scaling."""
    # Parse args with params_proto
    args = ObjScalerParams()

    # Handle positional argument (input file)
    # params_proto doesn't handle positional args directly, so we need to do this manually
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        args.file = sys.argv[1]

    if args.file is None:
        print("Error: Input file is required")
        print("Usage: scale-obj input.obj --scale 0.5")
        sys.exit(1)

    # Determine output file if not specified
    if args.output is None:
        base, ext = os.path.splitext(args.file)
        args.output = f"{base}_scaled{ext}"

    # Parse scale parameter
    scale_factor = parse_scale(args.scale)

    # Perform scaling
    scale_obj(
        args.file,
        args.output,
        scale_factor,
        preserve_origin=not args.world_origin,
        recenter_xy=args.recenter_xy,
        recenter_xz=args.recenter_xz,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()

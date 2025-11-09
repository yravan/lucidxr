from lxml import etree


def remove_unused_mesh(file_path, to=None):
    import os

    print("current work dir:", os.getcwd())
    print("file:", os.path.abspath(file_path))

    try:
        print(f"Reading file: {file_path}")

        # Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Remove <body> elements with name including 'eef_target' or 'robot'
        for body in root.findall(".//body"):
            body_name = body.attrib.get("name", "")
            if "eef_target" in body_name or "robot" in body_name:  # Check if the name matches the criteria
                print(f"\rRemoving unused body element: <body name='{body_name}'/>", end="", flush=True)
                parent = body.getparent()
                if parent is not None:
                    parent.remove(body)

        # Remove all <sensor> elements
        for sensor in root.findall(".//sensor"):
            print("\rRemoving sensor element: <sensor/>", end="", flush=True)
            parent = sensor.getparent()
            if parent is not None:
                parent.remove(sensor)

        # Remove all <actuator> elements
        for actuator in root.findall(".//actuator"):
            print("\rRemoving actuator element: <actuator/>", end="", flush=True)
            parent = actuator.getparent()
            if parent is not None:
                parent.remove(actuator)

        # Gather all used <mesh> elements
        used_mesh_names = {mesh.attrib.get("mesh", "") for mesh in root.findall(".//geom")}

        # Identify and remove unused <mesh> elements
        for mesh in root.findall(".//mesh"):
            mesh_name = mesh.attrib.get("name", "")
            if mesh_name not in used_mesh_names:  # Check if the mesh is unused
                print(f"\rRemoving unused mesh element: <mesh name='{mesh_name}'/>", end="", flush=True)
                parent = mesh.getparent()
                if parent is not None:
                    parent.remove(mesh)

        used_material_names = {mesh.attrib.get("material", "") for mesh in root.findall(".//geom")}

        for material in root.findall(".//material"):
            material_name = material.attrib.get("name", "")
            if material_name not in used_material_names:
                print(f"\rRemoving unused material element: <material name='{material_name}'/>", end="", flush=True)
                parent = material.getparent()
                if parent is not None:
                    parent.remove(material)

        used_texture_names = {texture.attrib.get("texture", "") for texture in root.findall(".//material")}
        for texture in root.findall(".//texture"):
            texture_name = texture.attrib.get("name", "")
            if texture_name not in used_texture_names:
                print(f"\rRemoving unused texture element: <texture name='{texture_name}'/>", end="", flush=True)
                parent = texture.getparent()
                if parent is not None:
                    parent.remove(texture)

        save_location = to or file_path
        if os.path.dirname(save_location) != "":
            os.makedirs(os.path.dirname(save_location), exist_ok=True)

        # Save changes back to the XML file
        tree.write(save_location, encoding="utf-8", xml_declaration=True, pretty_print=True)
        print(f"Updated XML file saved successfully: {save_location}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except OSError as e:
        print(f"OS error occurred: {e}")
    except etree.XMLSyntaxError as e:
        print(f"XML parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Provide the correct path
    file_path = "Stack.xml"
    remove_unused_mesh(file_path)

import json
import sys
from xml.dom import minidom
from xml.etree import ElementTree


X_HEX_SPACING = 15000000
Z_HEX_SPACING = 17320000
Z_HALF_SPACING = 8660000


def build_galaxy_file(name, prefix, clusters, connections):
    root = ElementTree.Element("macros")
    macro = ElementTree.SubElement(root, "macro")
    macro.set("name", f"{prefix}_{name}_macro")
    macro.set("class", "galaxy")

    _add_component_ref_element(macro, "standardgalaxy")

    connections = ElementTree.SubElement(macro, "connections")
    for cluster in input_json["clusters"]:
        _add_cluster(connections, prefix, cluster["id"], cluster["x"], cluster["z"])

    return root


def _add_component_ref_element(parent, value):
    component = ElementTree.SubElement(parent, "component")
    component.set("ref", value)


def _add_cluster(connections, prefix, cluster_id, cluster_x, cluster_z):
    x_position, y_position = _calculate_absolute_position(cluster_x, cluster_z)
    connection = ElementTree.SubElement(connections, "connection")
    connection.set("name", f"{prefix}_cluster{cluster_id:02}_connection")
    connection.set("ref", "clusters")
    offset = ElementTree.SubElement(connection, "offset")
    position = ElementTree.SubElement(offset, "position")
    position.set("x", str(x_position))
    position.set("y", "0")
    position.set("z", str(y_position))
    sub_macro = ElementTree.SubElement(connection, "macro")
    sub_macro.set("ref", f"{prefix}_cluster{cluster_id:02}_macro")
    sub_macro.set("connection", "galaxy")


def _calculate_absolute_position(x_coord, z_coord):
    x_absolute = x_coord * X_HEX_SPACING
    z_absolute = z_coord * Z_HEX_SPACING
    if x_coord % 2 != 0:
        z_absolute += Z_HALF_SPACING

    return (x_absolute, z_absolute)


def _add_connection():
    pass


if __name__ == "__main__":
    input_json = None
    with open(sys.argv[1]) as input_file:
        input_json = json.load(input_file)

    name = input_json["name"]
    prefix = input_json["prefix"]

    galaxy_root = build_galaxy_file(
        name, prefix, input_json["clusters"], input_json["connections"]
    )

    doc = minidom.parseString(ElementTree.tostring(galaxy_root))
    with open("galaxy.xml", "wb") as galaxy_file:
        galaxy_file.write(doc.toprettyxml(encoding="utf-8"))

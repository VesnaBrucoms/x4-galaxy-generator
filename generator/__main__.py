import json
import sys
from xml.dom import minidom
from xml.etree import ElementTree

from generator.maps.cluster import Cluster


X_HEX_SPACING = 15000000
Z_HEX_SPACING = 17320000
Z_HALF_SPACING = 8660000
CLUSTERS = []
CONNECTIONS = {}


def build_galaxy_file(name, prefix):
    root = ElementTree.Element("macros")
    macro = ElementTree.SubElement(root, "macro")
    macro.set("name", f"{prefix}_{name}_macro")
    macro.set("class", "galaxy")

    _add_component_ref_element(macro, "standardgalaxy")

    connections = ElementTree.SubElement(macro, "connections")
    for cluster in CLUSTERS:
        _add_cluster(connections, cluster)
        _collect_connections(cluster)
    _add_connection(connections, CLUSTERS)

    return root


def _add_component_ref_element(parent, value):
    component = ElementTree.SubElement(parent, "component")
    component.set("ref", value)


def _add_cluster(connections, cluster):
    x_position, y_position = _calculate_absolute_position(cluster.x, cluster.z)
    connection = ElementTree.SubElement(connections, "connection")
    connection.set("name", cluster.connection_ref)
    connection.set("ref", "clusters")
    offset = ElementTree.SubElement(connection, "offset")
    position = ElementTree.SubElement(offset, "position")
    position.set("x", str(x_position))
    position.set("y", "0")
    position.set("z", str(y_position))
    sub_macro = ElementTree.SubElement(connection, "macro")
    sub_macro.set("ref", cluster.macro_ref)
    sub_macro.set("connection", "galaxy")


def _collect_connections(cluster):
    cluster_gates = cluster.get_cluster_connections()
    for name, values in cluster_gates.items():
        for source in CONNECTIONS.keys():
            if source == values["destination"]:
                break
        else:
            sector_ref = values.pop("sector")
            zone_ref = values.pop("zone")
            path = f"../{cluster.connection_ref}/{sector_ref}/{zone_ref}/{name}"
            values["path"] = path
            CONNECTIONS[name] = values


def _calculate_absolute_position(x_coord, z_coord):
    x_absolute = x_coord * X_HEX_SPACING
    z_absolute = z_coord * Z_HEX_SPACING
    if x_coord % 2 != 0:
        z_absolute += Z_HALF_SPACING

    return (x_absolute, z_absolute)


def _add_connection(connections_element, clusters):
    for conn_name, conn_values in CONNECTIONS.items():
        destinaiton_sig = conn_name.split("_")[-1]
        dest_cluster_id = int(destinaiton_sig[1:4])
        dest_sector_id = int(destinaiton_sig[5:8])
        dest_cluster = None
        for cluster in CLUSTERS:
            if cluster.id == dest_cluster_id:
                dest_cluster = cluster
        if not dest_cluster:
            continue
        dest_sector = dest_cluster[dest_sector_id]
        destination = conn_values["destination"]
        zone_connection_ref = ""
        for zone in dest_sector.zones:
            if zone["gate_name"] == destination:
                zone_connection_ref = zone["connection_ref"]
        dest_path = f"../../../../../{dest_cluster.connection_ref}/{dest_sector.connection_ref}/{zone_connection_ref}/{destination}"

        clean_name = conn_name.replace("connection_", "")
        connection = ElementTree.SubElement(connections_element, "connection")
        connection.set("name", clean_name)
        connection.set("ref", "destination")
        connection.set("path", conn_values["path"])

        macro = ElementTree.SubElement(connection, "macro")
        macro.set("connection", "destination")
        macro.set("path", dest_path)


if __name__ == "__main__":
    input_json = None
    with open(sys.argv[1]) as input_file:
        input_json = json.load(input_file)

    name = input_json["name"]
    prefix = input_json["prefix"]
    for cluster in input_json["clusters"]:
        CLUSTERS.append(Cluster(prefix, cluster))

    galaxy_root = build_galaxy_file(name, prefix)

    doc = minidom.parseString(ElementTree.tostring(galaxy_root))
    with open("galaxy.xml", "wb") as galaxy_file:
        galaxy_file.write(doc.toprettyxml(encoding="utf-8"))

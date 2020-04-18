import json
import sys
from xml.dom import minidom
from xml.etree import ElementTree

from generator.utils import create_sub_element
from generator.maps.cluster import Cluster


X_HEX_SPACING = 15000000
Z_HEX_SPACING = 17320000
Z_HALF_SPACING = 8660000
CLUSTERS = []
CONNECTIONS = {}


def build_galaxy_file(name, prefix):
    root = ElementTree.Element("macros")
    macro = create_sub_element(
        root, "macro", name=f"{prefix}_{name}_macro", class_attr="galaxy"
    )

    create_sub_element(macro, "component", ref="standardgalaxy")

    connections = create_sub_element(macro, "connections")
    for cluster in CLUSTERS:
        _add_cluster(connections, cluster)
        _collect_connections(cluster)
    _add_connection(connections, CLUSTERS)

    return root


def build_clusters_file():
    root = ElementTree.Element("macros")
    for cluster in CLUSTERS:
        cluster.add_xml(root)
    return root


def build_sectors_file():
    root = ElementTree.Element("macros")
    for cluster in CLUSTERS:
        cluster.add_sector_xml(root)
    return root


def build_zones_file():
    root = ElementTree.Element("macros")
    for cluster in CLUSTERS:
        cluster.add_zone_xml(root)
    return root


def build_mapdefaults_file():
    root = ElementTree.Element("defaults")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "libraries.xsd")
    for cluster in CLUSTERS:
        _add_dataset_xml(root, cluster)
        for sector in cluster.sectors:
            _add_dataset_xml(root, sector)

    return root


def write_xml_file(name, root_element):
    doc = minidom.parseString(ElementTree.tostring(root_element))
    file_name = f"{name}.xml"
    with open(file_name, "wb") as new_file:
        new_file.write(doc.toprettyxml(encoding="utf-8"))


def _add_cluster(connections, cluster):
    x_position, y_position = _calculate_absolute_position(cluster.x, cluster.z)
    connection = create_sub_element(
        connections, "connection", name=cluster.connection_ref, ref="clusters"
    )
    offset = create_sub_element(connection, "offset")
    create_sub_element(offset, "position", x=x_position, y="0", z=y_position)
    create_sub_element(connection, "macro", ref=cluster.macro_ref, connection="galaxy")


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
            for zone_object in zone.objects:
                if zone_object["name"] == destination:
                    zone_connection_ref = zone.connection_ref
        dest_path = f"../../../../../{dest_cluster.connection_ref}/{dest_sector.connection_ref}/{zone_connection_ref}/{destination}"

        clean_name = conn_name.replace("connection_", "")
        connection = ElementTree.SubElement(connections_element, "connection")
        connection.set("name", clean_name)
        connection.set("ref", "destination")
        connection.set("path", conn_values["path"])

        macro = ElementTree.SubElement(connection, "macro")
        macro.set("connection", "destination")
        macro.set("path", dest_path)


def _add_dataset_xml(parent_element, macro):
    dataset = create_sub_element(parent_element, "dataset", macro=macro.macro_ref)
    props = create_sub_element(dataset, "properties")
    try:
        create_sub_element(
            props,
            "identification",
            name=macro.name,
            description=macro.description,
            system=macro.system,
        )
    except AttributeError:
        create_sub_element(
            props, "identification", name=macro.name, description=macro.description,
        )


if __name__ == "__main__":
    input_json = None
    with open(sys.argv[1]) as input_file:
        input_json = json.load(input_file)

    name = input_json["name"]
    prefix = input_json["prefix"]
    for cluster in input_json["clusters"]:
        CLUSTERS.append(Cluster(prefix, cluster))

    galaxy_root = build_galaxy_file(name, prefix)
    write_xml_file("galaxy", galaxy_root)

    clusters_root = build_clusters_file()
    write_xml_file("clusters", clusters_root)

    sectors_root = build_sectors_file()
    write_xml_file("sectors", sectors_root)

    zones_root = build_zones_file()
    write_xml_file("zones", zones_root)

    mapdefaults_root = build_mapdefaults_file()
    write_xml_file("mapdefaults", mapdefaults_root)

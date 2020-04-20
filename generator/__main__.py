import json
import sys
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree

from generator.builders.map_builder import MapBuilder
from generator.maps.galaxy import Galaxy
from generator.utils import create_sub_element


GALAXY = None


def build_galaxy_file(builder):
    builder.build_galaxy(GALAXY)


def build_clusters_file(builder):
    for cluster in GALAXY.clusters:
        builder.build_cluster(cluster)


def build_sectors_file(builder):
    for cluster in GALAXY.clusters:
        for sector in cluster.sectors:
            builder.build_sector(sector)


def build_zones_file(builder):
    for cluster in GALAXY.clusters:
        for sector in cluster.sectors:
            for zone in sector.zones:
                builder.build_zone(zone)


def build_mapdefaults_file():
    root = ElementTree.Element("defaults")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "libraries.xsd")
    for cluster in GALAXY.clusters:
        _add_dataset_xml(root, cluster)
        for sector in cluster.sectors:
            _add_dataset_xml(root, sector)

    return root


def build_macros_file():
    root = ElementTree.Element("index")
    create_sub_element(
        root, "entry", name=GALAXY.macro_ref, value=f"maps\\{GALAXY.map_name}\\galaxy",
    )
    create_sub_element(
        root,
        "entry",
        name=f"{GALAXY.prefix}_cluster*",
        value=f"maps\\{GALAXY.map_name}\\clusters",
    )
    for cluster in GALAXY.clusters:
        create_sub_element(
            root,
            "entry",
            name=f"{cluster.internal_name}_sector*",
            value=f"maps\\{GALAXY.map_name}\\sectors",
        )
        for sector in cluster.sectors:
            create_sub_element(
                root,
                "entry",
                name=f"{sector.internal_name}_zone*",
                value=f"maps\\{GALAXY.map_name}\\zones",
            )
    return root


def write_xml_file(name, root_element):
    doc = minidom.parseString(root_element)
    file_name = f"{name}.xml"
    with open(file_name, "wb") as new_file:
        new_file.write(doc.toprettyxml(encoding="utf-8"))


def write_old_xml_file(name, root_element):
    doc = minidom.parseString(ElementTree.tostring(root_element))
    file_name = f"{name}.xml"
    with open(file_name, "wb") as new_file:
        new_file.write(doc.toprettyxml(encoding="utf-8"))


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

    GALAXY = Galaxy(input_json["prefix"], input_json["name"], input_json["clusters"])

    ind_path = "./output/index"
    lib_path = "./output/libraries"
    map_path = f"./output/maps/{GALAXY.map_name}"

    Path(ind_path).mkdir(parents=True, exist_ok=True)
    Path(lib_path).mkdir(parents=True, exist_ok=True)
    Path(map_path).mkdir(parents=True, exist_ok=True)

    builder = MapBuilder()
    build_galaxy_file(builder)
    build_clusters_file(builder)
    build_sectors_file(builder)
    build_zones_file(builder)

    result = builder.get_result()
    write_xml_file(f"{map_path}/galaxy", result[0])
    write_xml_file(f"{map_path}/clusters", result[1])
    write_xml_file(f"{map_path}/sectors", result[2])
    write_xml_file(f"{map_path}/zones", result[3])

    mapdefaults_root = build_mapdefaults_file()
    write_old_xml_file(f"{lib_path}/mapdefaults", mapdefaults_root)

    macros_root = build_macros_file()
    write_old_xml_file(f"{ind_path}/macros", macros_root)

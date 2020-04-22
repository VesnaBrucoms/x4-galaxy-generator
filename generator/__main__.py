import json
import sys
from pathlib import Path
from xml.dom import minidom

from generator.builders.defaults_builder import MapDefaultsBuilder
from generator.builders.index_builder import IndexBuilder
from generator.builders.map_builder import MapBuilder
from generator.maps.galaxy import Galaxy
from generator.utils import create_sub_element


GALAXY = None


def build_map_files(builder):
    builder.build_galaxy(GALAXY)
    for cluster in GALAXY.clusters:
        builder.build_cluster(cluster)
        for sector in cluster.sectors:
            builder.build_sector(sector)
            for zone in sector.zones:
                builder.build_zone(zone)


def build_mapdefaults_file(builder):
    builder.build_defaults(GALAXY.clusters)


def build_macros_file(builder):
    builder.build_entries(GALAXY)


def write_xml_file(name, root_element):
    doc = minidom.parseString(root_element)
    file_name = f"{name}.xml"
    with open(file_name, "wb") as new_file:
        new_file.write(doc.toprettyxml(encoding="utf-8"))


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
    build_map_files(builder)

    results = builder.get_result()
    write_xml_file(f"{map_path}/galaxy", results[0])
    write_xml_file(f"{map_path}/clusters", results[1])
    write_xml_file(f"{map_path}/sectors", results[2])
    write_xml_file(f"{map_path}/zones", results[3])

    defaults_builder = MapDefaultsBuilder()
    build_mapdefaults_file(defaults_builder)
    write_xml_file(f"{lib_path}/mapdefaults", defaults_builder.get_result())

    index_builder = IndexBuilder()
    build_macros_file(index_builder)
    write_xml_file(f"{ind_path}/macros", index_builder.get_result())

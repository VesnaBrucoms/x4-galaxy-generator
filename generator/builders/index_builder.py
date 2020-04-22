from xml.etree import ElementTree

from generator.utils import create_root_element, create_sub_element


class IndexBuilder:
    def __init__(self):
        self._root = create_root_element("index")

    def build_entries(self, galaxy):
        directory = f"maps\\{galaxy.map_name}"
        self._build_entry(galaxy.macro_ref, directory, "galaxy")
        self._build_entry(f"{galaxy.prefix}_cluster*", directory, "clusters")
        for cluster in galaxy.clusters:
            self._build_entry(f"{cluster.internal_name}_sector*", directory, "sectors")
            for sector in cluster.sectors:
                self._build_entry(f"{sector.internal_name}_zone*", directory, "zones")

    def get_result(self):
        return ElementTree.tostring(self._root)

    def _build_entry(self, name, directory, file):
        create_sub_element(
            self._root, "entry", name=name, value=f"{directory}\\{file}",
        )

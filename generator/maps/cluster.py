"""Cluster class."""
from xml.etree import ElementTree

from generator.utils import add_component_ref_element
from generator.maps.sector import Sector


class Cluster:
    def __init__(self, prefix, cluster):
        self.id = cluster["id"]
        self.x = cluster["x"]
        self.z = cluster["z"]
        self.name = cluster.get("name", f"CLUSTER{self.id:03}")
        self.description = cluster.get("description", "UNKNOWN")
        self.environment = cluster.get("environment", None)
        self.internal_name = f"{prefix}_cluster{self.id:03}"

        self.sectors = self._add_sectors(cluster["sectors"])

    def __getitem__(self, key):
        matching_sector = None
        for sector in self.sectors:
            if sector.id == key:
                matching_sector = sector
                break
        return matching_sector

    @property
    def connection_ref(self):
        return f"{self.internal_name}_connection"

    @property
    def macro_ref(self):
        return f"{self.internal_name}_macro"

    def get_cluster_connections(self):
        connections = {}
        for sector in self.sectors:
            connections.update(sector.gates)
        return connections

    def add_xml(self, parent_element):
        macro = ElementTree.SubElement(parent_element, "macro")
        macro.set("name", self.macro_ref)
        macro.set("class", "cluster")

        add_component_ref_element(macro, "standardcluster")

        connections = ElementTree.SubElement(macro, "connections")
        for sector in self.sectors:
            connection = ElementTree.SubElement(connections, "connection")
            connection.set("name", sector.connection_ref)
            connection.set("ref", "sectors")
            macro = ElementTree.SubElement(connection, "macro")
            macro.set("ref", sector.macro_ref)
            macro.set("connection", "cluster")

        if self.environment:
            connection = ElementTree.SubElement(connections, "connection")
            connection.set("ref", "content")
            new_macro = ElementTree.SubElement(connection, "macro")
            component = ElementTree.SubElement(new_macro, "component")
            component.set("connection", "space")
            component.set("ref", self.environment)

    def add_sector_xml(self, parent_element):
        for sector in self.sectors:
            sector.add_xml(parent_element)

    def _add_sectors(self, sectors):
        created_sectors = []
        for sector in sectors:
            created_sectors.append(Sector(sector, self.id, self.internal_name))
        return created_sectors

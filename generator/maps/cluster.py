"""Cluster class."""
from generator.utils import create_sub_element
from generator.maps.sector import Sector


class Cluster:
    def __init__(self, prefix, cluster):
        self.id = cluster["id"]
        self.x = cluster["x"]
        self.z = cluster["z"]
        self.name = cluster.get("name", f"CLUSTER{self.id:03}")
        self.description = cluster.get("description", "UNKNOWN")
        if "system" in cluster.keys():
            self.system = cluster["system"]
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
        macro = create_sub_element(
            parent_element, "macro", name=self.macro_ref, class_attr="cluster"
        )

        create_sub_element(macro, "component", ref="standardcluster")

        connections = create_sub_element(macro, "connections")
        for sector in self.sectors:
            connection = create_sub_element(
                connections, "connection", name=sector.connection_ref, ref="sectors"
            )
            create_sub_element(
                connection, "macro", ref=sector.macro_ref, connection="cluster"
            )

        if self.environment:
            connection = create_sub_element(connections, "connection", ref="content")
            env_macro = create_sub_element(connection, "macro")
            create_sub_element(
                env_macro, "component", connection="space", ref=self.environment
            )

    def add_sector_xml(self, parent_element):
        for sector in self.sectors:
            sector.add_xml(parent_element)

    def add_zone_xml(self, parent_element):
        for sector in self.sectors:
            for zone in sector.zones:
                zone.add_xml(parent_element)

    def _add_sectors(self, sectors):
        created_sectors = []
        for sector in sectors:
            created_sectors.append(Sector(sector, self.id, self.internal_name))
        return created_sectors

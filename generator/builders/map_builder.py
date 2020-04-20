"""Map builder class."""
from xml.etree import ElementTree

from generator.utils import create_sub_element


X_HEX_SPACING = 15000000
Z_HEX_SPACING = 17320000
Z_HALF_SPACING = 8660000


class MapBuilder:
    def __init__(self):
        self.galaxy_root = ElementTree.Element("macros")
        self.clusters_root = ElementTree.Element("macros")
        self.sectors_root = ElementTree.Element("macros")
        self.zones_root = ElementTree.Element("macros")

    def build_galaxy(self, galaxy):
        macro = create_sub_element(
            self.galaxy_root, "macro", name=galaxy.macro_ref, class_attr="galaxy"
        )
        create_sub_element(macro, "component", ref="standardgalaxy")
        connections = create_sub_element(macro, "connections")
        for cluster in galaxy.clusters:
            self._add_galaxy_cluster(connections, cluster)
        for source, dest in galaxy.connections.items():
            source_gate_name = source.split("/")[-1]
            clean_name = source_gate_name.replace("connection_", "")
            connection = create_sub_element(
                connections,
                "connection",
                name=clean_name,
                ref="destination",
                path=source,
            )
            create_sub_element(connection, "macro", connection="destination", path=dest)

    def _add_galaxy_cluster(self, parent_element, cluster):
        x_position, y_position = self._calculate_absolute_position(cluster.x, cluster.z)
        connection = create_sub_element(
            parent_element, "connection", name=cluster.connection_ref, ref="clusters"
        )
        offset = create_sub_element(connection, "offset")
        create_sub_element(offset, "position", x=x_position, y="0", z=y_position)
        create_sub_element(
            connection, "macro", ref=cluster.macro_ref, connection="galaxy"
        )

    def _calculate_absolute_position(self, x_coord, z_coord):
        x_absolute = x_coord * X_HEX_SPACING
        z_absolute = z_coord * Z_HEX_SPACING
        if x_coord % 2 != 0:
            z_absolute += Z_HALF_SPACING

        return (x_absolute, z_absolute)

    def build_cluster(self, cluster):
        macro = create_sub_element(
            self.clusters_root, "macro", name=cluster.macro_ref, class_attr="cluster"
        )

        create_sub_element(macro, "component", ref="standardcluster")

        connections = create_sub_element(macro, "connections")
        for sector in cluster.sectors:
            connection = create_sub_element(
                connections, "connection", name=sector.connection_ref, ref="sectors"
            )
            create_sub_element(
                connection, "macro", ref=sector.macro_ref, connection="cluster"
            )

        if cluster.environment:
            connection = create_sub_element(connections, "connection", ref="content")
            env_macro = create_sub_element(connection, "macro")
            create_sub_element(
                env_macro, "component", connection="space", ref=cluster.environment
            )

    def build_sector(self, sector):
        macro = create_sub_element(
            self.sectors_root, "macro", name=sector.macro_ref, class_attr="sector"
        )

        create_sub_element(macro, "component", ref="standardsector")

        connections = create_sub_element(macro, "connections")
        for zone in sector.zones:
            connection = create_sub_element(
                connections, "connection", name=zone.connection_ref, ref="zones"
            )
            create_sub_element(
                connection, "macro", ref=zone.macro_ref, connection="sector"
            )

    def build_zone(self, zone):
        macro = create_sub_element(
            self.zones_root, "macro", name=zone.macro_ref, class_attr="zone"
        )

        create_sub_element(macro, "component", ref="standardzone")

        connections = create_sub_element(macro, "connections")
        for zone_object in zone.objects:
            connection = create_sub_element(
                connections,
                "connection",
                name=zone_object["name"],
                ref=zone_object["type"],
            )
            offset = create_sub_element(connection, "offset")
            create_sub_element(
                offset,
                "position",
                x=zone_object["x"],
                y=zone_object["y"],
                z=zone_object["z"],
            )
            create_sub_element(
                offset,
                "rotation",
                yaw=zone_object["yaw"],
                pitch=zone_object["pitch"],
                roll=zone_object["roll"],
            )
            create_sub_element(
                connection, "macro", ref=zone_object["prop"], connection="space"
            )

    def get_result(self):
        return (
            ElementTree.tostring(self.galaxy_root),
            ElementTree.tostring(self.clusters_root),
            ElementTree.tostring(self.sectors_root),
            ElementTree.tostring(self.zones_root),
        )

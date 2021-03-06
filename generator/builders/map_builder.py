"""Map builder class."""
from xml.etree import ElementTree

from generator.utils import create_root_element, create_sub_element


X_HEX_SPACING = 15000000
Z_HEX_SPACING = 17320000
Z_HALF_SPACING = 8660000


class MapBuilder:
    def __init__(self):
        self._galaxy_root = create_root_element("macros")
        self._clusters_root = create_root_element("macros")
        self._sectors_root = create_root_element("macros")
        self._zones_root = create_root_element("macros")

    def build_galaxy(self, galaxy):
        macro = create_sub_element(
            self._galaxy_root, "macro", name=galaxy.macro_ref, class_attr="galaxy"
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

    def build_cluster(self, cluster):
        macro = create_sub_element(
            self._clusters_root, "macro", name=cluster.macro_ref, class_attr="cluster"
        )
        create_sub_element(macro, "component", ref="standardcluster")
        connections = create_sub_element(macro, "connections")
        for sector in cluster.sectors:
            self._add_connection(
                connections,
                sector.connection_ref,
                "sectors",
                sector.macro_ref,
                "cluster",
            )

        if cluster.environment:
            connection = create_sub_element(connections, "connection", ref="content")
            env_macro = create_sub_element(connection, "macro")
            create_sub_element(
                env_macro, "component", connection="space", ref=cluster.environment
            )

    def build_sector(self, sector):
        macro = create_sub_element(
            self._sectors_root, "macro", name=sector.macro_ref, class_attr="sector"
        )
        create_sub_element(macro, "component", ref="standardsector")
        connections = create_sub_element(macro, "connections")
        for zone in sector.zones:
            self._add_connection(
                connections, zone.connection_ref, "zones", zone.macro_ref, "sector"
            )

    def build_zone(self, zone):
        macro = create_sub_element(
            self._zones_root, "macro", name=zone.macro_ref, class_attr="zone"
        )
        create_sub_element(macro, "component", ref="standardzone")
        connections = create_sub_element(macro, "connections")
        for zone_object in zone.objects:
            position = {
                "x": zone_object["x"],
                "y": zone_object["y"],
                "z": zone_object["z"],
            }
            rotation = {
                "yaw": zone_object["yaw"],
                "pitch": zone_object["pitch"],
                "roll": zone_object["roll"],
            }
            self._add_connection(
                connections,
                zone_object["name"],
                zone_object["type"],
                zone_object["prop"],
                "space",
                pos=position,
                rot=rotation,
            )

    def get_result(self):
        return (
            ElementTree.tostring(self._galaxy_root),
            ElementTree.tostring(self._clusters_root),
            ElementTree.tostring(self._sectors_root),
            ElementTree.tostring(self._zones_root),
        )

    def _add_galaxy_cluster(self, parent_element, cluster):
        x_position, y_position = self._calculate_absolute_position(cluster.x, cluster.z)
        position = {
            "x": x_position,
            "y": "0",
            "z": y_position,
        }
        self._add_connection(
            parent_element,
            cluster.connection_ref,
            "clusters",
            cluster.macro_ref,
            "galaxy",
            pos=position,
        )

    def _add_connection(
        self, parent_element, name, ref, macro_name, connection_ref, pos=None, rot=None,
    ):
        connection = create_sub_element(
            parent_element, "connection", name=name, ref=ref
        )
        if pos or rot:
            self._add_offset(connection, position=pos, rotation=rot)
        create_sub_element(
            connection, "macro", ref=macro_name, connection=connection_ref
        )

    def _calculate_absolute_position(self, x_coord, z_coord):
        x_absolute = x_coord * X_HEX_SPACING
        z_absolute = z_coord * Z_HEX_SPACING
        if x_coord % 2 != 0:
            z_absolute += Z_HALF_SPACING

        return (x_absolute, z_absolute)

    def _add_offset(self, parent_element, position=None, rotation=None):
        offset = create_sub_element(parent_element, "offset")
        if position:
            create_sub_element(
                offset, "position", x=position["x"], y=position["y"], z=position["z"],
            )
        if rotation:
            create_sub_element(
                offset,
                "rotation",
                yaw=rotation["yaw"],
                pitch=rotation["pitch"],
                roll=rotation["roll"],
            )

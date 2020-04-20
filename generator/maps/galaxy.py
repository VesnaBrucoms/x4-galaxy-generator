"""Galaxy class."""
from generator.maps.cluster import Cluster
from generator.utils import create_sub_element


X_HEX_SPACING = 15000000
Z_HEX_SPACING = 17320000
Z_HALF_SPACING = 8660000


class Galaxy:
    def __init__(self, prefix, name, clusters):
        self.prefix = prefix
        self.name = name
        self.internal_name = f"{prefix}_{name}"
        self.map_name = f"{prefix}_map"
        self.clusters = []
        self.connections = {}
        for cluster in clusters:
            self.clusters.append(Cluster(prefix, cluster))

    @property
    def connection_ref(self):
        return f"{self.internal_name}_connection"

    @property
    def macro_ref(self):
        return f"{self.internal_name}_macro"

    def add_xml(self, parent_element):
        macro = create_sub_element(
            parent_element, "macro", name=self.macro_ref, class_attr="galaxy"
        )
        create_sub_element(macro, "component", ref="standardgalaxy")
        connections = create_sub_element(macro, "connections")
        for cluster in self.clusters:
            self._add_cluster(connections, cluster)
            self._collect_connections(cluster)
        self._add_connections(connections)

    def _add_cluster(self, parent_element, cluster):
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

    def _collect_connections(self, cluster):
        cluster_gates = cluster.get_cluster_connections()
        for name, values in cluster_gates.items():
            for source in self.connections.keys():
                if source == values["destination"]:
                    break
            else:
                sector_ref = values.pop("sector")
                zone_ref = values.pop("zone")
                path = f"../{cluster.connection_ref}/{sector_ref}/{zone_ref}/{name}"
                values["path"] = path
                self.connections[name] = values

    def _add_connections(self, parent_element):
        for conn_name, conn_values in self.connections.items():
            destinaiton_sig = conn_name.split("_")[-1]
            dest_cluster_id = int(destinaiton_sig[1:4])
            dest_sector_id = int(destinaiton_sig[5:8])
            dest_cluster = None
            for cluster in self.clusters:
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
            connection = create_sub_element(
                parent_element,
                "connection",
                name=clean_name,
                ref="destination",
                path=conn_values["path"],
            )

            create_sub_element(
                connection, "macro", connection="destination", path=dest_path
            )

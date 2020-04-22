"""Galaxy class."""
from generator.maps.cluster import Cluster
from generator.utils import create_sub_element


class Galaxy:
    def __init__(self, prefix, name, clusters):
        self.prefix = prefix
        self.name = name
        self.internal_name = f"{prefix}_{name}"
        self.map_name = f"{prefix}_map"
        self.clusters = []
        self.connections = {}
        collected_connections = {}
        for cluster in clusters:
            new_cluster = Cluster(prefix, cluster)
            self.clusters.append(new_cluster)
            collected_connections.update(new_cluster.get_cluster_connections())
        self._prepare_and_deduplicate_connections(collected_connections)

    @property
    def connection_ref(self):
        return f"{self.internal_name}_connection"

    @property
    def macro_ref(self):
        return f"{self.internal_name}_macro"

    def _prepare_and_deduplicate_connections(self, collected_connections):
        sorted_conns = {}
        unpaired_source_paths = []
        for gate_name, values in collected_connections.items():
            for source_path in unpaired_source_paths:
                source_gate_name = source_path.split("/")[-1]
                if source_gate_name == values["destination"]:
                    cluster_ref = values["cluster"]
                    sector_ref = values["sector"]
                    zone_ref = values["zone"]
                    path = f"../../../../../{cluster_ref}/{sector_ref}/{zone_ref}/{gate_name}"
                    sorted_conns[source_path] = path
                    break
            else:
                cluster_ref = values["cluster"]
                sector_ref = values["sector"]
                zone_ref = values["zone"]
                path = f"../{cluster_ref}/{sector_ref}/{zone_ref}/{gate_name}"
                unpaired_source_paths.append(path)
        self.connections = sorted_conns

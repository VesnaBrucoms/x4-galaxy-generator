"""Sector class."""
from generator.utils import create_sub_element
from generator.maps.zone import Zone


class Sector:
    def __init__(self, sector, cluster_id, cluster_name):
        self.id = sector["id"]
        self.name = sector.get("name", f"SECTOR{self.id:03}")
        self.description = sector.get("description", "UNKNOWN")
        self.zones = sector["zones"]
        self.internal_name = f"{cluster_name}_sector{self.id:03}"

        self.gates = self._add_gate_zones(
            sector["gates"], cluster_id, f"{cluster_name}_connection"
        )

    @property
    def connection_ref(self):
        return f"{self.internal_name}_connection"

    @property
    def macro_ref(self):
        return f"{self.internal_name}_macro"

    def _add_gate_zones(self, gates, parent_id, parent_ref):
        created_gates = {}
        for gate in gates:
            dest_cluster_id = gate.pop("dest_cluster")
            dest_sector_id = gate.pop("dest_sector")
            source_sig = f"c{parent_id:03}s{self.id:03}"
            destination_sig = f"c{dest_cluster_id:03}s{dest_sector_id:03}"
            gate_name = f"connection_{source_sig}_to_{destination_sig}"
            gate_dest = f"connection_{destination_sig}_to_{source_sig}"

            zone_id = len(self.zones) + 1
            gate_object = {
                "name": gate_name,
                "type": "gates",
                "x": gate["x"],
                "y": gate["y"],
                "z": gate["z"],
                "yaw": gate["yaw"],
                "pitch": gate["pitch"],
                "roll": gate["roll"],
                "prop": gate["prop"],
            }
            new_gate_zone = Zone(
                {"id": zone_id, "objects": [gate_object]}, self.internal_name,
            )
            self.zones.append(new_gate_zone)
            created_gates[gate_name] = {
                "destination": gate_dest,
                "zone": new_gate_zone.connection_ref,
                "sector": self.connection_ref,
                "cluster": parent_ref,
            }

        return created_gates

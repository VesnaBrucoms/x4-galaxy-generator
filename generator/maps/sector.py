"""Sector class."""
from generator.utils import create_sub_element


class Sector:
    def __init__(self, sector, cluster_id, cluster_name):
        self.id = sector["id"]
        self.name = sector.get("name", f"SECTOR{self.id:03}")
        self.description = sector.get("description", "UNKNOWN")
        self.zones = sector["zones"]
        self.internal_name = f"{cluster_name}_sector{self.id:03}"

        self.gates = self._add_gate_zones(sector["gates"], cluster_id)

    @property
    def connection_ref(self):
        return f"{self.internal_name}_connection"

    @property
    def macro_ref(self):
        return f"{self.internal_name}_macro"

    def add_xml(self, parent_element):
        macro = create_sub_element(
            parent_element, "macro", name=self.macro_ref, class_attr="sector"
        )

        create_sub_element(macro, "component", ref="standardsector")

        connections = create_sub_element(macro, "connections")
        for zone in self.zones:
            connection = create_sub_element(
                connections, "connection", name=zone["connection_ref"], ref="zones"
            )
            create_sub_element(
                connection, "macro", ref=zone["macro_ref"], connection="sector"
            )

    def _add_gate_zones(self, gates, parent_id):
        created_gates = {}
        for gate in gates:
            dest_cluster_id = gate.pop("dest_cluster")
            dest_sector_id = gate.pop("dest_sector")
            source_sig = f"c{parent_id:03}s{self.id:03}"
            destination_sig = f"c{dest_cluster_id:03}s{dest_sector_id:03}"
            name = f"connection_{source_sig}_to_{destination_sig}"
            dest = f"connection_{destination_sig}_to_{source_sig}"

            zone_id = len(self.zones) + 1
            zone_internal_name = f"{self.internal_name}_zone{zone_id:03}"
            zone_connection_ref = f"{zone_internal_name}_connection"
            zone_macro_ref = f"{zone_internal_name}_macro"
            created_gates[name] = {
                "destination": dest,
                "zone": zone_connection_ref,
                "sector": self.connection_ref,
            }

            self.zones.append(
                {
                    "id": zone_id,
                    "internal_name": zone_internal_name,
                    "connection_ref": zone_connection_ref,
                    "macro_ref": zone_macro_ref,
                    "gate_name": name,
                    "x": gate["x"],
                    "y": gate["y"],
                    "z": gate["z"],
                    "yaw": gate["yaw"],
                    "pitch": gate["pitch"],
                    "roll": gate["roll"],
                    "prop": gate["prop"],
                }
            )

        return created_gates

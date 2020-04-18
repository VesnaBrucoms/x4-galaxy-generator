"""Zone class."""
from generator.utils import create_sub_element


class Zone:
    def __init__(self, zone, sector_name):
        self.id = zone["id"]
        self.objects = zone["objects"]
        self.internal_name = f"{sector_name}_zone{self.id:03}"

    @property
    def connection_ref(self):
        return f"{self.internal_name}_connection"

    @property
    def macro_ref(self):
        return f"{self.internal_name}_macro"

    def add_xml(self, parent_element):
        macro = create_sub_element(
            parent_element, "macro", name=self.macro_ref, class_attr="zone"
        )

        create_sub_element(macro, "component", ref="standardzone")

        connections = create_sub_element(macro, "connections")
        for zone_object in self.objects:
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

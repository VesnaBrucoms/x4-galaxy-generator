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

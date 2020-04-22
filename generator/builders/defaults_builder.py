"""Defaults builder class."""
from xml.etree import ElementTree

from generator.utils import create_root_element, create_sub_element


class MapDefaultsBuilder:
    def __init__(self):
        self._root = create_root_element(
            "defaults",
            namespace="http://www.w3.org/2001/XMLSchema-instance",
            schema="libraries.xsd",
        )

    def build_defaults(self, clusters):
        for cluster in clusters:
            self._add_dataset_xml(cluster)
            for sector in cluster.sectors:
                self._add_dataset_xml(sector)

    def get_result(self):
        return ElementTree.tostring(self._root)

    def _add_dataset_xml(self, macro):
        dataset = create_sub_element(self._root, "dataset", macro=macro.macro_ref)
        props = create_sub_element(dataset, "properties")
        enc_image = macro.encyclopedia.get("image", None)
        try:
            self._add_identification(
                props, macro.name, macro.description, enc_image, macro.system
            )
        except AttributeError:
            self._add_identification(props, macro.name, macro.description, enc_image)

    def _add_identification(self, parent_element, name, desc, image, system=None):
        create_sub_element(
            parent_element,
            "identification",
            name=name,
            description=desc,
            system=system,
            image=image,
        )

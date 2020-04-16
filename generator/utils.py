"""Holds common functions."""
from xml.etree import ElementTree


def add_component_ref_element(parent, value):
    component = ElementTree.SubElement(parent, "component")
    component.set("ref", value)

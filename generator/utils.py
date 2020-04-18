"""Holds common functions."""
from xml.etree import ElementTree


def create_sub_element(
    parent: ElementTree.Element, element_name: str, **kwargs
) -> ElementTree:
    """Creates new sub element of parent with 0 to many attributes.

    Any kwargs are added as attributes of the new element. For any
    attributes with names like "class", append "_attr" to the kwarg
    and the suffix will be stripped. For example, if the new element
    has an attribute of "class='cluster'", then pass in a kwarg of
    "class_attr='cluster'".
    """
    new_sub_element = ElementTree.SubElement(parent, element_name)
    for key, value in kwargs.items():
        checked_key = key
        if checked_key.endswith("_attr"):
            checked_key = key.replace("_attr", "")
        new_sub_element.set(checked_key, str(value))
    return new_sub_element

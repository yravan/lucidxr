"""Compact XML serialization with explicit parse errors."""

from lxml import etree


def walk_leaves(element, fn):
    """Visit an element and its descendants in document order."""
    for node in element.iter():
        fn(node)


class Minimize:
    def __call__(self, xml_string: str) -> str:
        root = etree.fromstring(xml_string.encode(), etree.XMLParser(remove_blank_text=True))
        for node in root.iter():
            if node.text:
                node.text = node.text.strip() or None
            if node.tail:
                node.tail = node.tail.strip() or None
        return etree.tostring(root, encoding="unicode").strip()

    def __ror__(self, xml_string: str) -> str:
        return self(xml_string)


class MinimizeMany(Minimize):
    def __call__(self, xml_string: str) -> str:
        root = etree.fromstring(super().__call__(f"<fragments>{xml_string}</fragments>"))
        return "".join(etree.tostring(child, encoding="unicode") for child in root)


minimize = Minimize()
minimize_many = MinimizeMany()

"""Small XML/file pipeline helpers. Errors propagate to the caller."""

from pathlib import Path

from lxml import etree


class MetaFile(type):
    def __matmul__(cls, filepath):
        return Path(filepath).read_text()


class File(metaclass=MetaFile):
    """Read with ``File @ path``."""


class Prettify:
    def __call__(self, xml_string: str) -> str:
        root = etree.fromstring(xml_string.encode(), etree.XMLParser(remove_blank_text=True))
        return etree.tostring(root, encoding="unicode", pretty_print=True)

    def __ror__(self, xml_string: str) -> str:
        return self(xml_string)


def Read(path) -> str:
    return Path(path).read_text()


class Save:
    def __init__(self, path, append=False):
        self.path = Path(path)
        self.append = append

    def __call__(self, xml_string: str):
        with self.path.open("a" if self.append else "w") as output:
            output.write(xml_string)

    def __ror__(self, xml_string: str):
        return self(xml_string)

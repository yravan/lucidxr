import inspect
from collections.abc import Iterable
from html import escape
from numbers import Integral, Real
from typing import Tuple

from lucidxr.sim.xml_schema.utils.minimizer import minimize


def attribute_value(value) -> str:
    """Serialize scalar and vector MJCF values consistently before XML escaping."""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, Real) and not isinstance(value, Integral):
        # Platform arithmetic (notably SIMD uniform sampling) can differ in the
        # last bits. Emit stable MJCF, not merely a tolerant recording hash.
        return format(value, ".12g")
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
        return " ".join(map(attribute_value, value))
    return str(value)


class XmlString(type):
    def __matmul__(cls, other):
        return cls(other)

    def __ror__(cls, other):
        return cls(other)


class Raw(metaclass=XmlString):
    def __init__(self, string, **kwargs):
        self._xml = string
        if kwargs:
            self._xml = self._xml.format(**kwargs)

    def __str__(self):
        return self._xml


class Xml(metaclass=XmlString):
    """This is the base class for all XML elements."""

    tag = "xml"
    _attributes: dict
    _children: Tuple["Xml"] = None
    _children_raw: str = ""

    def __init__(self, *_children, tag=None, children: Tuple = None, **attributes):
        if _children and children is not None:
            raise TypeError("Use positional children or children=, not both")
        self.tag = tag or self.tag
        self._attributes = {**getattr(self, "_attributes", {}), **attributes}
        selected = children if children is not None else (_children or self._children or ())
        if isinstance(selected, (str, Xml, Raw)):
            selected = (selected,)
        elif not isinstance(selected, Iterable):
            raise TypeError("Children must be XML nodes, strings, or an iterable of them")
        self._children = tuple(selected)

    def __str__(self) -> str:
        return self._xml

    @property
    def attributes(self) -> str:
        """Return the string representation of the attributes."""
        return " ".join(
            [f'{key}="{escape(attribute_value(value), quote=True)}"' for key, value in self._attributes.items()]
        )

    @property
    def children(self) -> str:
        """Return the string representation of the children."""
        child_strings = []
        for child in self._children or []:
            if hasattr(child, "_xml"):
                child_strings.append(child._xml)
            elif isinstance(child, str):
                child_strings.append(child)

        return "\n".join(child_strings)

    @property
    def _xml(self) -> str:
        """Return the XML representation of the model."""
        return f"""
        <{self.tag} {self.attributes}>{self.children}</{self.tag}>
        """

    @property
    def _minimized(self) -> str:
        """Return the minimized XML representation of the model."""
        raw_xml = self._xml
        minimized_xml = minimize(raw_xml)
        return minimized_xml


class XmlTemplate(Xml):
    """XML component with formatted body and recursively merged side sections.

    Public class/instance fields and XML attributes are available to templates.
    Child preambles and postambles propagate to their enclosing document.
    """

    _preamble: str = ""
    _postamble: str = ""
    _children_raw: str = ""
    template: str = ""
    _children: tuple = ()

    def __init__(
        self,
        *args,
        preamble: str = None,
        postamble: str = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if preamble is not None:
            self._preamble = preamble
        if postamble is not None:
            self._postamble = postamble

    def _format_dict(self, omit: set | None = None) -> dict:
        omit = omit or set()
        all_properties = {}

        for cls in reversed(type(self).__mro__):
            for name, value in vars(cls).items():
                if (
                    name not in omit
                    and not name.startswith("_")
                    and not isinstance(value, property)
                    and not callable(value)
                ):
                    all_properties[name] = value

        for name, value in inspect.getmembers(type(self), lambda x: isinstance(x, property)):
            if name not in omit and not name.startswith("_"):
                all_properties[name] = getattr(self, name)

        for key, value in self.__dict__.items():
            if key not in omit and not key.startswith("_"):
                all_properties[key] = value

        all_properties.update(self._attributes)

        return all_properties

    def join(self, *s: str):
        filtered = [_ for _ in s if _.strip()]
        return "\n".join(filtered)

    @property
    def preamble(self):
        """Render this component and its children's document-level declarations."""
        values = self._format_dict({"preamble", "children", "postamble", "template"})
        string = self._preamble.format(**values)

        child_preambles = [p.preamble for p in self._children or [] if hasattr(p, "preamble")]

        if child_preambles:
            preamble = self.join(string, *child_preambles)
            return preamble
        else:
            return string

    @property
    def children(self) -> str:
        values = self._format_dict({"children", "preamble", "postamble", "template"})
        string = self._children_raw.format(**values)
        return "\n".join(part for part in (string, super().children) if part.strip())

    @property
    def postamble(self):
        """Render this component and its children's document-level declarations."""
        values = self._format_dict({"preamble", "children", "postamble", "template"})
        string = self._postamble.format(**values)

        child_postambles = [p.postamble for p in self._children or [] if hasattr(p, "postamble")]
        if child_postambles:
            postamble = self.join(string, *child_postambles)
            return postamble
        else:
            return string

    def __str__(self):
        return self._xml

    @property
    def _xml(self) -> str:
        values = self._format_dict()
        return self.template.format(**values)


def chain(*elements: Xml) -> Xml:
    """Nest elements in order, preserving each node's existing children."""
    if not elements:
        raise ValueError("chain requires at least one XML element")
    for parent, child in zip(elements, elements[1:]):
        parent._children = (*parent._children, child)
    return elements[0]

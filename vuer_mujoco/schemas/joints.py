from .schema import Body


class FloatingBase(Body):
    _attributes = {
        "name": "floating-base",
    }
    _children_raw = """
    <joint name="{name}-floating-base" type="free"/>
    """

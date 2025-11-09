from vuer_mujoco.schemas.base import Xml


def chain(*elements: Xml):
    for child, next in zip(elements[:-1], elements[1:]):
        if child._children:
            child._children = (*child._children, next)
        else:
            child._children = (next,)
    return elements[0]

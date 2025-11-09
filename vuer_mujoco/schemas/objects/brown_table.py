from vuer_mujoco.schemas.schema import Body


class BrownTable(Body):
    assets = "brown-table"

    _attributes = {
        "name": "brown-table",
    }
    _preamble = """
    <default>
        <default class="brown-table-visual">
            <geom group="2" type="mesh" contype="0" conaffinity="0"/>
        </default>
        <default class="brown-table-collision">
            <geom group="3" type="mesh"/>
        </default>
    </default>

    <asset>
        <texture type="2d" name="{name}-ER_TableTop_BaseColor" file="{assets}/ER_TableTop_BaseColor.png"/>
        <material name="{name}-TableTop" texture="{name}-ER_TableTop_BaseColor" specular="0.5" shininess="0.5"/>
        <texture type="2d" name="{name}-ER_Table_WhiteWood_BaseColor" file="{assets}/ER_Table_WhiteWood_BaseColor.png"/>
        <material name="{name}-WhiteWood" texture="{name}-ER_Table_WhiteWood_BaseColor" specular="0.5" shininess="0.5"/>
        <mesh name="{name}-EastRural_Table_0" file="{assets}/EastRural_Table_0.obj"/>
        <mesh name="{name}-EastRural_Table_1" file="{assets}/EastRural_Table_1.obj"/>
    </asset>
    """

    _children_raw = """
        <geom mesh="{name}-EastRural_Table_0" material="{name}-WhiteWood" class="brown-table-visual"/>
        <geom mesh="{name}-EastRural_Table_1" material="{name}-TableTop" class="brown-table-visual"/>
        <geom mesh="{name}-EastRural_Table_0" class="brown-table-collision"/>
        <geom mesh="{name}-EastRural_Table_1" class="brown-table-collision"/>
    """

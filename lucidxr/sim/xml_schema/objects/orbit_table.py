from lucidxr.sim.xml_schema.schema import Body


class OpticalTable(Body):
    assets = "objects/optical_table"
    classname = "optical_table"
    free = True
    alpha = 1.0
    _files = ["model"]

    _attributes = {
        "name": "object",
    }

    _preamble = """
        <default>
            <default class="{classname}-visual">
                <geom group="2" type="mesh" contype="0" conaffinity="0"/>
            </default>
            <default class="{classname}-collision">
                <geom group="3" type="mesh"/>
            </default>
        </default>
        <asset>
          <!-- Materials ported from MTL file -->
          <material name="{name}-mat_1" rgba="0.501961 0.517647 0.501961 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_2" rgba="1 1 1 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_3" rgba="0.752941 0.752941 0.752941 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_4" rgba="0.647059 0.619608 0.588235 {alpha}" roughness="0" shininess="1" specular="0.4"/> <!-- Good wood-like color for tabletop -->
          <material name="{name}-mat_5" rgba="0.101961 0.101961 0.101961 {alpha}" roughness="0" shininess="1" specular="0.4"/> <!-- Dark color for legs/structure -->
          <material name="{name}-mat_6" rgba="0.109804 0.109804 0.109804 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_7" rgba="0.792157 0.819608 0.933333 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_8" rgba="0.529412 0.549020 0.549020 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_9" rgba="0.098039 0.098039 0.098039 {alpha}" shininess=""/>
          <material name="{name}-mat_10" rgba="0 0 0 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_11" rgba="0.294118 0.294118 0.294118 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_12" rgba="0.250980 0.250980 0.250980 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_13" rgba="0.698039 0.698039 0.698039 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_14" rgba="0.956863 0.956863 0.956863 {alpha}" roughness="0" shininess="1" specular="0.4"/>

          <mesh name="{classname}-model_0" file="{assets}/model_0.obj"/>
          <mesh name="{classname}-model_1" file="{assets}/model_1.obj"/>
          <mesh name="{classname}-model_2" file="{assets}/model_2.obj"/>
          <mesh name="{classname}-model_3" file="{assets}/model_3.obj"/>
          <mesh name="{classname}-model_4" file="{assets}/model_4.obj"/>
          <mesh name="{classname}-model_5" file="{assets}/model_5.obj"/>
          <mesh name="{classname}-model_6" file="{assets}/model_6.obj"/>
          <mesh name="{classname}-model_7" file="{assets}/model_7.obj"/>
          <mesh name="{classname}-model_8" file="{assets}/model_8.obj"/>
          <mesh name="{classname}-model_9" file="{assets}/model_9.obj"/>
          <mesh name="{classname}-model_10" file="{assets}/model_10.obj"/>
          <mesh name="{classname}-model_11" file="{assets}/model_11.obj"/>
          <mesh name="{classname}-model_12" file="{assets}/model_12.obj"/>
          <mesh name="{classname}-model_13" file="{assets}/model_13.obj"/>
        </asset>
        """

    _children_raw = """
        <!--<freejoint/>-->
        <geom mesh="{classname}-model_0" class="{classname}-visual"  material="{name}-mat_1" />
        <geom mesh="{classname}-model_1" class="{classname}-visual"  material="{name}-mat_2" />
        <geom mesh="{classname}-model_2" class="{classname}-visual"  material="{name}-mat_3" />
        <geom mesh="{classname}-model_3" class="{classname}-visual"  material="{name}-mat_4" />
        <geom mesh="{classname}-model_4" class="{classname}-visual"  material="{name}-mat_5" />
        <geom mesh="{classname}-model_5" class="{classname}-visual"  material="{name}-mat_6" />
        <geom mesh="{classname}-model_6" class="{classname}-visual"  material="{name}-mat_7" />
        <geom mesh="{classname}-model_7" class="{classname}-visual"  material="{name}-mat_8" />
        <geom mesh="{classname}-model_8" class="{classname}-visual"  material="{name}-mat_9" />
        <geom mesh="{classname}-model_9" class="{classname}-visual"  material="{name}-mat_10"/>
        <geom mesh="{classname}-model_10" class="{classname}-visual" material="{name}-mat_11"/>
        <geom mesh="{classname}-model_11" class="{classname}-visual" material="{name}-mat_12"/>
        <geom mesh="{classname}-model_12" class="{classname}-visual" material="{name}-mat_13"/>
        <geom mesh="{classname}-model_13" class="{classname}-visual" material="{name}-mat_14"/>
        """

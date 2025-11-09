# fridge.py
from vuer_mujoco.schemas.schema import Body


class KitchenFridge(Body):
    """
    Auto-generated template for the refrigerator.

    Parameters you are most likely to tweak:

    assets      directory that contains ``visuals/`` and (optionally) ``collision/``.
    prefix      short string to avoid name clashes when instantiating more than one.
    mesh_scale  uniform OBJ scale, written once and applied to every <mesh>.
    """

    # ------------------------------------------------------------------ #
    # high-level knobs
    # ------------------------------------------------------------------ #
    assets      = "fridge"        # e.g.      assets/fridge/visuals/Body001.obj
    prefix      = "fr"            # becomes   fr-Body001_vis   etc.
    mesh_scale  = "1.0 1.0 1.0"   # OBJ-space scaling applied to *all* meshes

    _attributes = {
        "name":        "{prefix}-frame",   # root body name, may be overridden
    }

    # ------------------------------------------------------------------ #
    #  assets section: textures, materials, meshes
    # ------------------------------------------------------------------ #
    _preamble = """
    <asset>
        <mesh file="{assets}/visuals/Body001.obj" name="{prefix}/Body001_vis"/>
        <mesh file="{assets}/visuals/Body002.obj" name="{prefix}/Body002_vis"/>
        <mesh file="{assets}/visuals/Door001.obj" name="{prefix}/Door001_vis"/>
        <mesh file="{assets}/visuals/Door001_Clear.obj" name="{prefix}/Door001_Clear_vis"/>
        <mesh file="{assets}/visuals/Drawer001.obj" name="{prefix}/Drawer001_vis"/>
        <mesh file="{assets}/visuals/Drawer002.obj" name="{prefix}/Drawer002_vis"/>
        <texture file="{assets}/visuals/T_BC001.png" name="{prefix}/Body001_material" type="2d"/>
        <material name="{prefix}/Body001_material" rgba="1 1 1 1.0" texture="{prefix}/Body001_material" shininess="0.31350553035736084" specular="0.3103448502657381"/>
        <texture file="{assets}/visuals/T_BC001.png" name="{prefix}/Body002_material" type="2d"/>
        <material name="{prefix}/Body002_material" rgba="1 1 1 1.0" texture="{prefix}/Body002_material" shininess="0.31350553035736084" specular="0.3103448502657381"/>
        <texture file="{assets}/visuals/T_BC001.png" name="{prefix}/Door001_material" type="2d"/>
        <material name="{prefix}/Door001_material" rgba="1 1 1 1.0" texture="{prefix}/Door001_material" shininess="0.31350553035736084" specular="0.3103448502657381"/>
        <texture file="{assets}/visuals/T_BC001.png" name="{prefix}/Drawer001_material" type="2d"/>
        <material name="{prefix}/Drawer001_material" rgba="1 1 1 1.0" texture="{prefix}/Drawer001_material" shininess="0.31350553035736084" specular="0.3103448502657381"/>
        <texture file="{assets}/visuals/T_BC001.png" name="{prefix}/Drawer002_material" type="2d"/>
        <material name="{prefix}/Drawer002_material" rgba="1 1 1 1.0" texture="{prefix}/Drawer002_material" shininess="0.31350553035736084" specular="0.3103448502657381"/>
        <material name="{prefix}/Door001_Clear_material" rgba="0.800000011920929 0.800000011920929 0.800000011920929 0.08733627200126648" shininess="0.5" specular="0.3103448502657381"/>
    </asset>
    <default>
        <default class="{prefix}">
            <default class="{prefix}-visual">
                <geom type="mesh" contype="0" conaffinity="0" group="0"/>
            </default>
            <default class="{prefix}-collision">
                <geom group="3" rgba="0.5 0 0 0.5"/>
            </default>
            <default class="{prefix}-region">
                <geom group="0" contype="0" conaffinity="0" rgba="0 1 0 0"/>
            </default>
        </default>
    </default>
    """

    # ------------------------------------------------------------------ #
    #  world-body  (all numbers identical to the original)
    # ------------------------------------------------------------------ #
    _children_raw = """
        <geom mesh="{prefix}/Body001_vis" type="mesh" solimp="0.998 0.998 0.001" solref="0.001 1" density="100" friction="0.95 0.3 0.1" class="{prefix}-visual" material="{prefix}/Body001_material"/>
        <geom class="{prefix}-collision" type="box" pos="-0.3940710127353668 0.06275410205125809 -0.0006774307112209499" size="0.031181402504444122 0.37738826870918274 0.9359207153320312" quat="1.0 0.0 0.0 0.0"/>
        <geom class="{prefix}-collision" type="box" pos="0.3919791281223297 0.06275410950183868 -0.0006774307112209499" size="0.030255861580371857 0.3773885667324066 0.9359207153320312" quat="1.0 0.0 0.0 0.0"/>
        <geom class="{prefix}-collision" type="box" pos="-0.003005377249792218 0.06247815489768982 0.9109719395637512" size="0.4162082374095917 0.37711286544799805 0.024271223694086075" quat="1.0 0.0 0.0 0.0"/>
        <geom class="{prefix}-collision" type="box" pos="-0.003005377249792218 0.4117155075073242 -0.0009676485788077116" size="0.4162082374095917 0.027595268562436104 0.9359143972396851" quat="1.0 0.0 0.0 0.0"/>
        <geom class="{prefix}-collision" type="box" pos="-0.003005377249792218 0.06275410950183868 -0.8789532780647278" size="0.4162082374095917 0.3773896396160126 0.05723448842763901" quat="1.0 0.0 0.0 0.0"/>
        <geom class="{prefix}-collision" type="box" pos="-0.003005377249792218 -0.35098278522491455 -0.8917291760444641" size="0.4084376096725464 0.0465230792760849 0.0444585345685482" quat="1.0 0.0 0.0 0.0"/>
        <body name="{name}-Body002">
          <geom mesh="{prefix}/Body002_vis" type="mesh" solimp="0.998 0.998 0.001" solref="0.001 1" density="100" friction="0.95 0.3 0.1" class="{prefix}-visual" material="{prefix}/Body002_material"/>
          <geom class="{prefix}-collision" type="box" pos="-0.0014342060312628746 0.09791933000087738 0.5651807188987732" size="0.3656265139579773 0.2948967516422272 0.008134711533784866" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.001195636112242937 0.04632935672998428 0.24166375398635864" size="0.3633967638015747 0.3461066484451294 0.00927546713501215" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.001195636112242937 0.059925638139247894 -0.10092896223068237" size="0.3633967638015747 0.3794723451137543 0.017055664211511612" quat="1.0 0.0 0.0 0.0"/>
        </body>
        <body name="{name}-Door001">
          <joint axis="0.0 0.0 1.0" pos="0.3793938457965851 -0.3540734648704529 0.4236448109149933" limited="true" name="{name}-Door001_joint" range="0.0 1.5707963267948966" type="hinge" damping="1" frictionloss="1" armature=".01" stiffness="0.05"/>
          <geom mesh="{prefix}/Door001_vis" type="mesh" solimp="0.998 0.998 0.001" solref="0.001 1" density="100" friction="0.95 0.3 0.1" class="{prefix}-visual" material="{prefix}/Door001_material"/>
          <geom class="{prefix}-collision" type="box" pos="-0.02830483205616474 -0.3667275309562683 0.4207412898540497" size="0.3724071681499481 0.02750129997730255 0.5125665664672852" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.3156786859035492 -0.42462262511253357 0.4115767180919647" size="0.03464058041572571 0.006546389311552048 0.4979086220264435" quat="0.9950294494628906 0.0 0.0 -0.09958113729953766"/>
          <body name="{name}-Door001_Clear">
            <geom mesh="{prefix}/Door001_Clear_vis" type="mesh" solimp="0.998 0.998 0.001" solref="0.001 1" density="100" friction="0.95 0.3 0.1" class="{prefix}-visual" material="{prefix}/Door001_Clear_material"/>
            <geom class="{prefix}-collision" type="box" pos="0.3027845323085785 -0.24827545881271362 0.37747132778167725" size="0.005082062911242247 0.08504998683929443 0.0777270495891571" quat="1.0 0.0 0.0 0.0"/>
            <geom class="{prefix}-collision" type="box" pos="-0.3163357377052307 -0.24827545881271362 0.37747135758399963" size="0.005082057788968086 0.08504989743232727 0.07772698253393173" quat="1.0 0.0 0.0 0.0"/>
            <geom class="{prefix}-collision" type="box" pos="-0.007146106101572514 -0.24822264909744263 0.3075364828109741" size="0.31459107995033264 0.07752437889575958 0.00779131893068552" quat="1.0 0.0 0.0 0.0"/>
            <geom class="{prefix}-collision" type="box" pos="-0.007146095857024193 -0.16828928887844086 0.37747135758399963" size="0.3145938515663147 0.004805755335837603 0.0777268260717392" quat="1.0 0.0 0.0 0.0"/>
            <geom class="{prefix}-collision" type="box" pos="-0.007146095857024193 -0.16828928887844086 0.6888020634651184" size="0.31459343433380127 0.004805749747902155 0.07772675156593323" quat="1.0 0.0 0.0 0.0"/>
            <geom class="{prefix}-collision" type="box" pos="-0.007146106101572514 -0.24822264909744263 0.6188671588897705" size="0.31459107995033264 0.07752411812543869 0.00779131893068552" quat="1.0 0.0 0.0 0.0"/>
            <geom class="{prefix}-collision" type="box" pos="-0.3163357377052307 -0.24827545881271362 0.6888020634651184" size="0.005082026589661837 0.08504942059516907 0.07772659510374069" quat="1.0 0.0 0.0 0.0"/>
            <geom class="{prefix}-collision" type="box" pos="0.3027845323085785 -0.24827545881271362 0.6888020038604736" size="0.00508201913908124 0.08504932373762131 0.07772649824619293" quat="1.0 0.0 0.0 0.0"/>
          </body>
        </body>
        <body name="{name}-Drawer001">
          <joint axis="0.0 -1.0 0.0" pos="-0.022611111402511597 0.04361245781183243 0.03509211167693138" limited="true" name="{name}-Drawer001_joint" range="0.0 0.45" type="slide" damping="1" frictionloss="1" armature=".01" stiffness="0.05"/>
          <geom mesh="{prefix}/Drawer001_vis" type="mesh" solimp="0.998 0.998 0.001" solref="0.001 1" density="100" friction="0.95 0.3 0.1" class="{prefix}-visual" material="{prefix}/Drawer001_material"/>
          <geom class="{prefix}-collision" type="box" pos="-0.02497066743671894 -0.28286805748939514 0.032526299357414246" size="0.3206898868083954 0.004805822391062975 0.10691582411527634" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.02497066743671894 0.35859888792037964 0.032526299357414246" size="0.32068946957588196 0.004805815871804953 0.10691565275192261" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.02497066743671894 0.03844917565584183 -0.06659462302923203" size="0.3206806480884552 0.31774669885635376 0.007791309151798487" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.3402498960494995 0.03839649632573128 0.032526299357414246" size="0.005082127638161182 0.3252722918987274 0.10691531002521515" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="0.2910495400428772 0.03839649632573128 0.032526299357414246" size="0.005082123447209597 0.325271874666214 0.10691513866186142" quat="1.0 0.0 0.0 0.0"/>
        </body>
        <body name="{name}-Drawer002">
          <joint axis="0.0 -1.0 0.0" pos="-7.969141006469727e-05 -0.03420105576515198 -0.4718346893787384" limited="true" name="{name}-Drawer002_joint" range="0.0 0.5" type="slide" damping="1" frictionloss="1" armature=".01" stiffness="0.05"/>
          <geom mesh="{prefix}/Drawer002_vis" type="mesh" solimp="0.998 0.998 0.001" solref="0.001 1" density="100" friction="0.95 0.3 0.1" class="{prefix}-visual" material="{prefix}/Drawer002_material"/>
          <geom class="{prefix}-collision" type="box" pos="-0.0011914935894310474 0.3628953993320465 -0.48247089982032776" size="0.341813325881958 0.004805789794772863 0.3093748092651367" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.010098197497427464 -0.00039964914321899414 -0.7799317240715027" size="0.32364463806152344 0.3330284655094147 0.017229238525032997" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.33811312913894653 0.0170903243124485 -0.4841383993625641" size="0.005082099698483944 0.3525598347187042 0.307706743478775" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="0.33599114418029785 0.013876717537641525 -0.48419347405433655" size="0.0050820945762097836 0.3493458032608032 0.3076513707637787" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.02944262884557247 -0.3667554259300232 -0.4704700708389282" size="0.38856837153434753 0.026475509628653526 0.36812254786491394" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="-0.0011914935894310474 -0.33533552289009094 -0.48247089982032776" size="0.34181052446365356 0.004805746953934431 0.30937305092811584" quat="1.0 0.0 0.0 0.0"/>
          <geom class="{prefix}-collision" type="box" pos="0.0007595455390401185 -0.43163663148880005 -0.16591814160346985" size="0.031590551137924194 0.007566715590655804 0.3390676975250244" quat="0.7045928239822388 -0.05957247316837311 0.7045928835868835 -0.059572722762823105"/>
        </body>
        <geom class="{prefix}-region" name="{name}-reg_main" type="box" pos="0.0 0.02290348708629608 0.0" size="0.42529571056365967 0.4173002243041992 0.9352431297302246"/>
    """

    # ------------------------------------------------------------------ #
    # optional: create the three motors exactly like the source MJCF
    # ------------------------------------------------------------------ #
    # _postamble = """
    # <actuator>
    #     <motor name="{name}-Door001_act"   joint="{name}-Door001_hinge"     gear="50"/>
    #     <motor name="{name}-Drawer001_act" joint="{name}-Drawer001_slide"   gear="50"/>
    #     <motor name="{name}-Drawer002_act" joint="{name}-Drawer002_slide"   gear="50"/>
    # </actuator>
    # """

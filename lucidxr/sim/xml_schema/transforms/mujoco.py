from math import cos, sin
from typing import NamedTuple

import numpy as np

from lucidxr.sim.xml_schema.base import attribute_value
from lucidxr.sim.xml_schema.transforms.helpers import Pipe

from .vector import Vector3

π = 3.141592653589793238462643383279502884197169399375105820974944592307816406286


null_vec = Vector3(0, 0, 0)


# todo: not sure if this is useful.
class WXYZ(NamedTuple):
    w: float
    x: float
    y: float
    z: float

    def __str__(self):
        return attribute_value(tuple(self))

    def __add__(self, other: "WXYZ") -> "WXYZ":
        """Compose WXYZ rotations with Hamilton multiplication."""
        return apply_quaternion(self, other)

    def __radd__(self, other) -> "WXYZ":
        return apply_quaternion(other, self)

    def __invert__(self) -> "WXYZ":
        return invert(self)


to_vec = Pipe(Vector3)
as_wxyz = Pipe(WXYZ)


def apply_quaternion(q1: WXYZ, q2: WXYZ) -> WXYZ:
    """
    Applies quaternion q2 to quaternion q1.

    Parameters:
    - q1: A 4-tuple representing the first quaternion (w, x, y, z).
    - q2: A 4-tuple representing the second quaternion (w, x, y, z).

    Returns:
    - A 4-tuple representing the resulting quaternion.
    """
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

    return WXYZ(w, x, y, z)


def invert(q: WXYZ) -> WXYZ:
    """
    Computes the inverse of a quaternion.

    Parameters:
    - q: A 4-tuple representing the quaternion (w, x, y, z).

    Returns:
    - A 4-tuple representing the inverse quaternion.
    """
    w, x, y, z = q
    norm = w**2 + x**2 + y**2 + z**2
    if norm == 0:
        raise ValueError("Cannot invert a zero-norm quaternion")
    return WXYZ(w / norm, -x / norm, -y / norm, -z / norm)


def x_rot(θ: float) -> WXYZ:
    """
    Creates a quaternion representing a rotation of θ radians around the x-axis.

    Parameters:
    - θ: Rotation angle in radians.

    Returns:
    - A Quaternion representing the rotation.
    """
    half_θ = θ / 2
    return WXYZ(cos(half_θ), sin(half_θ), 0.0, 0.0)


def y_rot(θ: float) -> WXYZ:
    """
    Creates a quaternion representing a rotation of θ radians around the y-axis.

    Parameters:
    - θ: Rotation angle in radians.

    Returns:
    - A Quaternion representing the rotation.
    """
    half_θ = θ / 2
    return WXYZ(cos(half_θ), 0.0, sin(half_θ), 0.0)


def z_rot(θ: float) -> WXYZ:
    """
    Creates a quaternion representing a rotation of θ radians around the z-axis.

    Parameters:
    - θ: Rotation angle in radians.

    Returns:
    - A Quaternion representing the rotation.
    """
    half_θ = θ / 2
    return WXYZ(cos(half_θ), 0.0, 0.0, sin(-half_θ))


def apply_euler(q: WXYZ, tx: float = 0, ty: float = 0, tz: float = 0) -> WXYZ:
    """
    Applies extrinsic Euler rotations (tx, ty, tz) to the quaternion `q`.

    Parameters:
    - q: WXYZ, original quaternion to rotate.
    - tx: Rotation in radians around the X-axis (global frame).
    - ty: Rotation in radians around the Y-axis (global frame).
    - tz: Rotation in radians around the Z-axis (global frame).

    Returns:
    - The rotated quaternion accounting for extrinsic Euler rotations.
    """
    # Create the global frame rotation quaternions
    qx = x_rot(tx)  # Rotation around the X-axis
    qy = y_rot(ty)  # Rotation around the Y-axis
    qz = z_rot(tz)  # Rotation around the Z-axis

    # Combine rotations in order ZYX (extrinsic rotations in global frame)
    combined_rotation = apply_quaternion(qz, apply_quaternion(qy, qx))

    # Apply the combined rotation to the original quaternion
    return apply_quaternion(combined_rotation, q)


def apply_euler_vec(pos: Vector3, tx: float = 0, ty: float = 0, tz: float = 0) -> Vector3:
    """
    Applies extrinsic Euler rotations (tx, ty, tz) to the vector `pos`.

    Parameters:
    - pos: Vector3, original vector to rotate.
    - tx: Rotation in radians around the X-axis (global frame).
    - ty: Rotation in radians around the Y-axis (global frame).
    - tz: Rotation in radians around the Z-axis (global frame).

    Returns:
    - The rotated vector accounting for extrinsic Euler rotations.
    """
    # Create the global frame rotation quaternions
    rx = np.array(quat2xmat(x_rot(tx))).reshape(3, 3)  # Rotation around the X-axis
    ry = np.array(quat2xmat(y_rot(ty))).reshape(3, 3)  # Rotation around the Y-axis
    rz = np.array(quat2xmat(z_rot(tz))).reshape(3, 3)  # Rotation around the Z-axis

    # Combine rotations in order ZYX (extrinsic rotations in global frame)
    combined_rotation = rz @ ry @ rx
    # Apply the combined rotation to the original vector
    rotated_vector = combined_rotation @ np.array([pos.x, pos.y, pos.z])
    return Vector3(rotated_vector[0], rotated_vector[1], rotated_vector[2])


# // [0, 2, -1]
def m2t_vec(x, y, z):
    return x, z, -y


def t2m_vec(x, y, z):
    return x, -z, y


# // [1, 3, -2, 0]
def m2t_quat(w, x, y, z):
    return x, z, -y, w


def t2m_quat(w, x, y, z):
    return w, x, -z, y


to_mujoco_wxyz = Pipe(lambda *args: t2m_quat(*args) | as_wxyz)
to_mujoco_vec = Pipe(lambda *args: t2m_vec(*args) | to_vec)


def xmat2quat(site_xmat):
    """
    Convert a flattened 3x3 rotation matrix (MuJoCo site_xmat) to quaternion [w, x, y, z].

    Args:
        site_xmat (list or np.ndarray): A list of 9 elements representing a 3x3 rotation matrix in row-major order.

    Mathematical Conversion:
        Given a rotation matrix R:
         R = | r11 r12 r13 |
             | r21 r22 r23 |
             | r31 r32 r33 |

        The quaternion values (q_w, q_x, q_y, q_z) can be computed as follows:
        - q_w = sqrt(1 + r11 + r22 + r33) / 2
        - q_x = (r32 - r23) / (4 * q_w)
        - q_y = (r13 - r31) / (4 * q_w)
        - q_z = (r21 - r12) / (4 * q_w)

    Returns:
        WXYZ: Quaternion in MuJoCo's [w, x, y, z] format.
    """
    from scipy.spatial.transform import Rotation

    xyzw = Rotation.from_matrix(np.asarray(site_xmat).reshape(3, 3)).as_quat()
    return [xyzw[3], *xyzw[:3]]


def quat2xmat(quat):
    """
    Convert a quaternion [w, x, y, z] to a flattened 3x3 rotation matrix.

    Args:
        quat (list or np.ndarray): A list of 4 elements representing the quaternion [w, x, y, z].

    Returns:
        list: A flattened 3x3 rotation matrix in row-major order.
    """
    w, x, y, z = quat
    return [
        1 - 2 * (y**2 + z**2),
        2 * (x * y - w * z),
        2 * (x * z + w * y),
        2 * (x * y + w * z),
        1 - 2 * (x**2 + z**2),
        2 * (y * z - w * x),
        2 * (x * z - w * y),
        2 * (y * z + w * x),
        1 - 2 * (x**2 + y**2),
    ]


def transform_point(position, quaternion, point):
    """Apply a WXYZ orientation and translation to a local point."""
    from scipy.spatial.transform import Rotation

    w, x, y, z = quaternion
    rotated = Rotation.from_quat((x, y, z, w)).apply(point)
    return Vector3(*(np.asarray(position) + rotated))

import numpy as np
from scipy.spatial.transform import Rotation

HAND_JOINTS = {
    "wrist": 0,
    "thumb-metacarpal": 1,
    "thumb-phalanx-proximal": 2,
    "thumb-phalanx-distal": 3,
    "thumb-tip": 4,
    "index-finger-metacarpal": 5,
    "index-finger-phalanx-proximal": 6,
    "index-finger-phalanx-intermediate": 7,
    "index-finger-phalanx-distal": 8,
    "index-finger-tip": 9,
    "middle-finger-metacarpal": 10,
    "middle-finger-phalanx-proximal": 11,
    "middle-finger-phalanx-intermediate": 12,
    "middle-finger-phalanx-distal": 13,
    "middle-finger-tip": 14,
    "ring-finger-metacarpal": 15,
    "ring-finger-phalanx-proximal": 16,
    "ring-finger-phalanx-intermediate": 17,
    "ring-finger-phalanx-distal": 18,
    "ring-finger-tip": 19,
    "pinky-finger-metacarpal": 20,
    "pinky-finger-phalanx-proximal": 21,
    "pinky-finger-phalanx-intermediate": 22,
    "pinky-finger-phalanx-distal": 23,
    "pinky-finger-tip": 24,
}


class RelativeMocapTracker:
    def __init__(self):
        self.base_mocap_pose = None  # 4x4 matrix
        self.base_hand_pose = None  # 4x4 matrix
        self.is_active = False

    def update(self, *, hand_poses, hand_state, joint_name, value, squeeze_condition, physics, align_mujoco_frame=False):
        """Update mocap pose based on hand tracking and squeeze condition"""

        # Get hand joint index
        joint_idx = HAND_JOINTS.get(joint_name, 0)
        print("joint_idx", joint_idx, "joint_name", joint_name)
        joint_matrix = hand_poses[joint_idx * 16 : (joint_idx + 1) * 16]
        joint_matrix = np.array(joint_matrix).reshape(4, 4).T

        # Check squeeze condition
        is_squeezed = hand_state.get(squeeze_condition, False)

        if is_squeezed and self.base_mocap_pose is not None and self.base_hand_pose is not None:
            # ACTIVE: Compute relative transformation
            self.is_active = True

            # Get current hand position
            current_hand_position = joint_matrix[:3, 3]

            # Get base positions
            base_mocap_position = self.base_mocap_pose[:3, 3]
            base_hand_position = self.base_hand_pose[:3, 3]

            # Calculate relative hand movement
            relative_hand_movement = current_hand_position - base_hand_position

            # Apply relative movement to base mocap position
            new_mocap_position = base_mocap_position + relative_hand_movement

            # Handle rotation (local coordinate system transformation)
            # 1. Compute relative transformation in hand's local space
            inv_base_hand = np.linalg.inv(self.base_hand_pose)
            relative_transform = joint_matrix @ inv_base_hand
            # relative_transform = inv_base_hand @ joint_matrix

            # 2. Extract rotation from relative transformation
            relative_rotation = relative_transform[:3, :3]

            # 3. Extract rotation from base mocap pose (local coordinate system)
            base_mocap_rotation = self.base_mocap_pose[:3, :3]

            # 4. Apply relative rotation in local coordinate system (premultiply)
            # This is the key: we apply the relative rotation in the mocap's local space
            new_mocap_rotation = relative_rotation @ base_mocap_rotation

            # Extract quaternion and position
            quaternion = self._rotation_matrix_to_quaternion(new_mocap_rotation)
            # quaternion = np.array([0, 0, 1, 0])
            position = new_mocap_position

        else:
            # INACTIVE: Store base poses for next activation
            self.is_active = False
            # self.base_mocap_pose = joint_matrix.copy()  # Current hand pose becomes base
            init_mocap_pos = physics.data.mocap_pos[0].copy()
            init_mocap_quat = physics.data.mocap_quat[0].copy()
            position = np.array([init_mocap_pos[0], init_mocap_pos[2], -init_mocap_pos[1]])
            quaternion = np.array([init_mocap_quat[0], init_mocap_quat[1], init_mocap_quat[3], -init_mocap_quat[2]])

            # print('inactive, setting default pose of', init_mocap_pos, init_mocap_quat)
            self.base_mocap_pose = self.quaternion_position_to_matrix(quaternion, position)

            self.base_hand_pose = joint_matrix.copy()

        # Apply MuJoCo coordinate frame alignment if requested
        if align_mujoco_frame:
            position = np.array([position[0], -position[2], position[1]])
            quaternion = np.array([quaternion[0], quaternion[1], -quaternion[3], quaternion[2]])

        control_value = self.compute_control_value(
            hand_poses=hand_poses,
            hand_state=hand_state,
            value=value,
            offset=0.10,
            scale=-12,
            low=0,
            high=1,
        )

        return dict(
            position=position,
            quaternion=quaternion,
            active=self.is_active,
            control=control_value,
        )

    def compute_control_value(
        self, hand_poses, hand_state, value="right:thumb-tip,right:index-finger-tip", offset=0.10, scale=-12, low=0, high=1
    ):
        """Compute control value based on distance between two hand joints"""

        # Parse the value parameter to get joint names
        parts = value.split(",")
        if len(parts) != 2:
            return None

        # Extract joint names from the value string
        joint1_name = parts[0].split(":")[-1]  # Get 'thumb-tip' from 'right:thumb-tip'
        joint2_name = parts[1].split(":")[-1]  # Get 'index-finger-tip' from 'right:index-finger-tip'

        # Extract joint indices
        joint1_idx = HAND_JOINTS.get(joint1_name)
        joint2_idx = HAND_JOINTS.get(joint2_name)

        if joint1_idx is None or joint2_idx is None:
            return None

        # Compute distance between joints
        distance = self.compute_distance_between_joints(hand_poses, joint1_idx, joint2_idx)
        if distance is None:
            return None

        # Apply offset and scale (matching HandActuator logic)
        adjusted_distance = distance - offset
        scaled_value = adjusted_distance * scale

        # Clamp to range
        control_value = np.clip(scaled_value, low, high)

        return control_value

    def compute_distance_between_joints(self, hand_poses, joint1_index, joint2_index):
        """Compute distance between two hand joints"""
        if hand_poses is None or len(hand_poses) < (max(joint1_index, joint2_index) + 1) * 16:
            return None

        # Extract positions from matrices
        pos1 = self.extract_position_from_matrix(hand_poses[joint1_index * 16 : (joint1_index + 1) * 16])
        pos2 = self.extract_position_from_matrix(hand_poses[joint2_index * 16 : (joint2_index + 1) * 16])

        # Compute distance
        distance = np.linalg.norm(pos1 - pos2)
        return distance

    def extract_position_from_matrix(self, matrix_values):
        """Extract position from 4x4 matrix (16 values)"""
        matrix = np.array(matrix_values).reshape(4, 4).T
        # Position is the last column (translation)
        position = matrix[:3, 3]  # [x, y, z]
        return position

    def _rotation_matrix_to_quaternion(self, rotation_matrix):
        """Convert rotation matrix to quaternion using scipy"""
        rotation = Rotation.from_matrix(rotation_matrix)
        quaternion = rotation.as_quat()  # [x, y, z, w]
        return np.array([quaternion[3], quaternion[0], quaternion[1], quaternion[2]])  # [w, x, y, z]

    def quaternion_position_to_matrix(self, quaternion, position):
        """
        Convert quaternion and position to 4x4 transformation matrix

        Args:
            quaternion: [w, x, y, z] format
            position: [x, y, z] format

        Returns:
            4x4 transformation matrix
        """
        # Normalize quaternion
        quaternion = np.array(quaternion)
        quaternion = quaternion / np.linalg.norm(quaternion)

        # Convert quaternion to rotation matrix
        rotation = Rotation.from_quat([quaternion[1], quaternion[2], quaternion[3], quaternion[0]])  # [x, y, z, w]
        rotation_matrix = rotation.as_matrix()

        # Create 4x4 transformation matrix
        matrix = np.eye(4)
        matrix[:3, :3] = rotation_matrix
        matrix[:3, 3] = position

        return matrix

import numpy as np
from .helpers import geometry as geom


class PointCloudManipulator:
    def __init__(self, medial_point_cloud, side):
        self.original_x_bounds = (min(medial_point_cloud[:, 0]),
                                  max(medial_point_cloud[:, 0]))
        self.original_y_bounds = (min(medial_point_cloud[:, 1]),
                                  max(medial_point_cloud[:, 1]))
        self.original_z_bounds = (min(medial_point_cloud[:, 2]),
                                  max(medial_point_cloud[:, 2]))
        self.original_density_bounds = (min(medial_point_cloud[:, 3]),
                                        max(medial_point_cloud[:, 3]))
        self.roi_points = medial_point_cloud
        # centered_points = self.__get_centered_point_cloud(self.roi_points)
        centered_points = self.__get_dim_normalised_point_cloud(self.roi_points,
                                                                side)
        self.centred_nomalised_points = self.__get_normalized_point_cloud(
            centered_points)
        if side == 'right':
            self.cn_x_bounds = (min(self.centred_nomalised_points[:, 0]),
                                max(self.centred_nomalised_points[:, 0]))
        else:
            self.cn_x_bounds = (max(self.centred_nomalised_points[:, 0]),
                                min(self.centred_nomalised_points[:, 0]))
        self.cn_y_bounds = (min(self.centred_nomalised_points[:, 1]),
                            max(self.centred_nomalised_points[:, 1]))
        self.cn_z_bounds = (min(self.centred_nomalised_points[:, 2]),
                            max(self.centred_nomalised_points[:, 2]))
        self.cn_density_bounds = (min(self.centred_nomalised_points[:, 3]),
                                  max(self.centred_nomalised_points[:, 3]))

        self.original_space_bounds = np.array([self.original_x_bounds,
                                               self.original_y_bounds,
                                               self.original_z_bounds])
        self.cn_space_bounds = np.array([self.cn_x_bounds,
                                         self.cn_y_bounds,
                                         self.cn_z_bounds])

    def __get_normalized_point_cloud(self, point_cloud):
        x, y, z, density = zip(*point_cloud)
        density_min, density_max = min(density), max(density)
        normalized_density = [(d - density_min) /
                              (density_max - density_min) for d in density]
        return np.array(list(zip(x, y, z, normalized_density)))

    def __get_centered_point_cloud(self, point_cloud):
        """
        Centers a 4D point cloud (x, y, z, density) by subtracting the mean of the x, y, z coordinates.

        Args:
            point_cloud (np.array): 4D array of shape (n, 4) where n is the number of points

        Returns:
            np.array: Centered 4D point cloud of shape (n, 4)
        """
        mean = np.mean(point_cloud[:, :3], axis=0)
        centered_cloud = point_cloud.copy()
        centered_cloud[:, :3] -= mean
        return centered_cloud

    def un_normalize(self, point_cloud):
        new_point_cloud = point_cloud.copy()
        new_point_cloud[:, 3] = geom.translate_space_1d(
            self.cn_density_bounds, self.original_density_bounds, point_cloud[:, 3])
        return new_point_cloud

    def __get_dim_normalised_point_cloud(self, point_cloud, side):
        """
        Normalizes a 4D point cloud to be within a bounding cube of dimension 1 in the first 3 dimensions.
        If the 'side' argument is 'left', it scales the x-values to be between -0.5 and 0.5.
        If the 'side' argument is 'right', it scales the x-values to be between 0.5 and -0.5.
        The y- and z-values are scaled to be between -0.5 and 0.5 in both cases.
        The 4th dimension is left unchanged.

        Args:
        - point_cloud: a numpy array of shape (N, 4) representing the point cloud
        - side: a string indicating which side the point cloud is from ('left' or 'right')

        Returns:
        - a numpy array of shape (N, 4) representing the normalized point cloud
        """
        # Extract the first 3 dimensions of the point cloud
        point_cloud_xyz = point_cloud[:, :3]

        # Compute the bounding box of the point cloud
        min_vals = np.min(point_cloud_xyz, axis=0)
        max_vals = np.max(point_cloud_xyz, axis=0)

        # Compute the center of the bounding box
        center = (min_vals + max_vals) / 2

        # Translate the point cloud to be centered at the origin
        point_cloud_xyz = point_cloud_xyz - center

        # Scale the point cloud to be within a bounding cube of dimension 1
        max_range = np.max(np.abs(point_cloud_xyz))
        scale_factor = 0.5 / max_range
        point_cloud_xyz = point_cloud_xyz * scale_factor

        if side == 'left':
            point_cloud_xyz[:, 0] *= -1

        # Concatenate the normalized xyz coordinates with the unchanged 4th dimension
        point_cloud_norm = np.concatenate(
            [point_cloud_xyz, point_cloud[:, 3:]], axis=1)

        return point_cloud_norm

    def __get_dim_un_normalised_point_cloud(self, point_cloud_norm, side):
        """
        Reverses the normalization process applied to a 4D point cloud in the first 3 dimensions.
        The 'side' argument should be the same as the one used to normalize the point cloud.
        The 4th dimension is left unchanged.

        Args:
        - point_cloud_norm: a numpy array of shape (N, 4) representing the normalized point cloud
        - side: a string indicating which side the point cloud is from ('left' or 'right')

        Returns:
        - a numpy array of shape (N, 4) representing the original point cloud
        """
        # Extract the first 3 dimensions of the normalized point cloud
        point_cloud_norm_xyz = point_cloud_norm[:, :3]

        # Reverse the x-scaling according to the side argument
        if side == 'left':
            point_cloud_norm_xyz[:, 0] = point_cloud_norm_xyz[:, 0] + 0.5
        elif side == 'right':
            point_cloud_norm_xyz[:, 0] = 0.5 - point_cloud_norm_xyz[:, 0]

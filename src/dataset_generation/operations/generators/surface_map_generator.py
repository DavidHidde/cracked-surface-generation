import bpy
import math
import mathutils

import cv2
import numpy as np
from tqdm import tqdm
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial._qhull import QhullError

from crack_generation.models.surface import BoundingBox, SurfaceMap

GRID_RESOLUTION = 1000
NORMAL_MAIN_AXES_THRESHOLD = 0.5
DEPTH_MAP_THRESHOLD = 0.05


def calculate_bounding_box(obj: bpy.types.Object) -> BoundingBox:
    """
    Get the bounding box in world space.
    Assumes the location of the object to be the center.
    """
    center = np.array([
        obj.location.x,
        obj.location.y,
        obj.location.z,
    ])
    dimensions = np.array([
        obj.dimensions.x,
        obj.dimensions.y,
        obj.dimensions.z
    ])

    return BoundingBox(
        center - dimensions / 2.,
        center + dimensions / 2.,
        dimensions[0],
        dimensions[2],
        dimensions[1]
    )


class SurfaceMapGenerator:
    """
    Generates a surface map off off an object.
    Takes x=x and y=z and uses the y-dimension for surface height data.
    Assumes the object to be positioned along the x-axis or y-axis.
    """

    def __call__(self, wall: bpy.types.Object) -> SurfaceMap:
        """
        Generate the surface map of an object.
        """
        bounding_box = calculate_bounding_box(wall)

        # Setup the grid - We want millimeter precision and Blender dimensions are in meters, so we multiply by a resolution factor
        grid = np.full(
            (math.ceil(bounding_box.height * GRID_RESOLUTION), math.ceil(bounding_box.width * GRID_RESOLUTION)),
            -1.,
            dtype=np.float32
        )

        # Retrieve all relevant faces
        mesh = wall.data
        if bounding_box.width >= bounding_box.height:  # X-axis aligned - Get faces pointing to positive y
            faces = [face for face in mesh.polygons if NORMAL_MAIN_AXES_THRESHOLD < face.normal.y]
            point_transform = mathutils.Matrix.Identity(4)
        else:  # Y-axis aligned - Get faces pointing to positive x
            faces = [face for face in mesh.polygons if NORMAL_MAIN_AXES_THRESHOLD < face.normal.x]
            point_transform = mathutils.Matrix.Rotation(math.radians(90.), 4, 'Z')

        point_transform = wall.matrix_world @ point_transform

        # Draw faces
        print(f'Processing faces of "{wall.name}"...')
        skipped_faces = 0
        min_y = np.inf
        max_y = -np.inf
        for face in tqdm(faces):
            # Transform points to world space and interpolate depth values
            verts = np.array([point_transform @ mesh.vertices[idx].co for idx in face.vertices])
            coords = np.round((verts[:, [0, 2]] - bounding_box.min_vertex[[0, 2]]) * GRID_RESOLUTION)
            coeffs = np.squeeze(verts[:, 1])

            try:
                interpolator = LinearNDInterpolator(coords, coeffs)
                x, y = np.meshgrid(np.arange(grid.shape[1]), np.arange(grid.shape[0]))
                marked_grid = interpolator(x, y)

                mask = ~np.isnan(marked_grid)
                grid[mask] = np.maximum(grid[mask], marked_grid[mask])

                min_y = min(np.min(coeffs), min_y)
                max_y = max(np.min(coeffs), max_y)
            except QhullError:
                skipped_faces += 1

        if skipped_faces > 0:
            print(
                f'Encountered {skipped_faces} QHull error(s) for which the faces were skipped.\
                Consider changing the normal threshold or your model.'
            )

        # Post process grid
        grid[grid != -1] = (grid[grid != -1] - min_y) / (max_y - min_y)
        grid[grid == -1] = 1  # Set all outside values to max

        # Compute final maps
        mask = grid >= DEPTH_MAP_THRESHOLD
        distance_transform = cv2.distanceTransform((mask == False).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_5)
        gradients = np.gradient(distance_transform)
        angles = np.arctan2(gradients[0], gradients[1])

        return SurfaceMap(
            mask,
            distance_transform,
            angles,
            GRID_RESOLUTION,
            bounding_box
        )

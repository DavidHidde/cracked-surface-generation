import bpy
import math

import cv2
import numpy as np
from skimage import draw

from dataset_generation.models import BoundingBox, SurfaceMap


def rasterize_face(verts: np.array, grid: np.array) -> None:
    """
    Rasterize the lines of the face.
    """
    num_verts = len(verts)
    int_verts = np.rint(verts).astype(int)
    for idx in range(num_verts):
        curr_vert = int_verts[idx]
        next_vert = int_verts[(idx + 1) % num_verts]
        rows, columns = draw.line(curr_vert[2], curr_vert[0], next_vert[2], next_vert[0])
        depths = np.linspace(verts[idx][1], verts[(idx + 1) % num_verts][1], len(rows))
        grid[rows, columns] = np.maximum(grid[rows, columns], depths)


def get_background_mask(grid: np.array) -> np.array:
    """
    Fill all faces on the surface in a single pass
    """
    _, labels, stats, _ = cv2.connectedComponentsWithStatsWithAlgorithm(
        (grid == 0).astype(np.uint8),
        4,
        cv2.CV_32S,
        -1  # Default algorithm
    )
    # We assume the component with the biggest area to be the background
    background_component_idx = np.argmax(stats[:, cv2.CC_STAT_AREA])

    # Place original edges back
    mask = np.logical_or(labels > background_component_idx, grid > 0)

    # Make the label smaller through a dilation
    kernel = np.ones((3, 3), np.uint8)
    return cv2.erode(mask.astype(np.uint8), kernel).astype(bool)


def calculate_bounding_box(object: bpy.types.Object) -> BoundingBox:
    """
    Get the bounding box in world space.
    Assumes the location of the object to be the center.
    """
    center = np.array([
        object.location.x,
        object.location.y,
        object.location.z,
    ])
    dimensions = np.array([
        object.dimensions.x,
        object.dimensions.y,
        object.dimensions.z
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
    Takes x=x and y=z and uses the y-dimension for surface heigth data.
    Assumes the object to be positioned along the x-axis
    """

    def __call__(self, objects: list[bpy.types.Object]) -> SurfaceMap:
        """
        Generate the surface map of an object.
        Takes x=x and z=z and disregards the y-dimension.
        """

        # Get the total bounding box
        bounding_box = calculate_bounding_box(objects[0])
        for idx in range(1, len(objects)):
            bounding_box = bounding_box.combine(calculate_bounding_box(objects[idx]))

        # Setup the grid - We want millimeter precision and Blender dimensions are in meters, so we multiply by 1000
        grid_factor = 1000
        grid = np.zeros((
            math.ceil(bounding_box.height * grid_factor) + 1,
            math.ceil(bounding_box.width * grid_factor) + 1
        ))

        # Draw faces
        for obj in objects:
            mesh = obj.data
            for face in mesh.polygons:
                # Ignore faces that are not facing us
                if face.normal.y < 0.2:
                    continue

                verts = [obj.matrix_world @ mesh.vertices[vertex_idx].co for vertex_idx in face.vertices]
                verts = np.array([[vert.x, vert.y, vert.z] for vert in verts])
                verts = np.subtract(verts, bounding_box.min_vertex)  # Make sure all values are positive
                verts *= grid_factor  # Cast to grid dimensions
                rasterize_face(verts, grid)

        mask = get_background_mask(grid)
        distance_transform = cv2.distanceTransform((mask == False).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_5)
        gradients = np.gradient(distance_transform)
        angles = np.arctan2(gradients[0], gradients[1])

        return SurfaceMap(
            grid,
            mask,
            distance_transform,
            angles,
            bounding_box,
            grid_factor
        )

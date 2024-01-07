import bpy
import math

import cv2
import numpy as np

from crack_generation.models.surface import BoundingBox, SurfaceMap


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
    Takes x=x and y=z and uses the y-dimension for surface heigth data.
    Assumes the object to be positioned along the x-axis
    """

    def __call__(self, mortar: bpy.types.Object) -> SurfaceMap:
        """
        Generate the surface map of an object.
        Takes x=x and z=z and disregards the y-dimension.
        """
        bounding_box = calculate_bounding_box(mortar)

        # Setup the grid - We want millimeter precision and Blender dimensions are in meters, so we multiply by 1000
        grid_factor = 1000
        grid = np.zeros(
            (
                math.ceil(bounding_box.height * grid_factor) + 1,
                math.ceil(bounding_box.width * grid_factor) + 1,
            ),
            np.uint8
        )

        # Draw faces
        mesh = mortar.data
        faces = [face for face in mesh.polygons if face.normal.y < 0.2]
        face_verts = [[mortar.matrix_world @ mesh.vertices[idx].co for idx in face.vertices] for face in faces]
        verts = [np.array([
            [
                round((vert.x - bounding_box.min_vertex[0]) * grid_factor),
                round((vert.z - bounding_box.min_vertex[2]) * grid_factor)
            ] for vert in verts]) for verts in face_verts]
        cv2.fillPoly(grid, verts, 255)

        # Compute other maps
        mask = grid == 0
        distance_transform = cv2.distanceTransform((mask == False).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_5)
        gradients = np.gradient(distance_transform)
        angles = np.arctan2(gradients[0], gradients[1])

        return SurfaceMap(
            mask,
            distance_transform,
            angles,
            grid_factor,
            bounding_box
        )

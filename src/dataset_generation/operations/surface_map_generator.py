import bpy
import math
import numpy as np
from skimage import draw

from dataset_generation.models import BoundingBox, SurfaceMap


def rasterize_face(verts: np.array, grid: np.array) -> None:
    """
    Rasterize the lines of the face. Note that we
    """
    num_verts = len(verts)
    for idx in range(num_verts):
        curr_vert = verts[idx]
        next_vert = verts[(idx + 1) % num_verts]
        rows, columns = draw.line(curr_vert[2], curr_vert[0], next_vert[2], next_vert[0])
        depths = np.linspace(curr_vert[1], next_vert[1], len(rows))
        grid[rows, columns] = np.maximum(grid[rows, columns], depths)


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

                verts = [mesh.vertices[vertex_idx] for vertex_idx in face.vertices]
                verts = np.array([[vert.co.x, vert.co.y, vert.co.z] for vert in verts])
                verts = np.subtract(verts, bounding_box.min_vertex)  # Make sure all values are positive
                verts *= grid_factor  # Cast to grid dimensions
                rasterize_face(np.rint(verts).astype(int), grid)

        # Cast depths ranges to [0, 255].
        contrast_stretch_factor = 255. / np.max(grid)
        grid *= contrast_stretch_factor

        return SurfaceMap(grid, bounding_box, contrast_stretch_factor, grid_factor)

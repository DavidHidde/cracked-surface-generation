from crack_generation.models import CrackModel


class ObjFileExporter:
    """
    Class that exports scipy convex hulls into .obj files
    """

    def __call__(self, model: CrackModel, filepath: str) -> bool:
        """
        Export a model to a .obj file
        """

        points = model.points
        faces = model.faces + 1
        side_faces = model.side_faces + 1

        # Scale down to 1% to get a reasonable size.
        points = [coords * 0.01 for coords in points]

        try:
            with open(filepath, 'w') as objfile:
                for vertex in points:
                    objfile.write('v %.4f %.4f %.4f\n' % (vertex[0], vertex[1], vertex[2]))
                for quad in faces:
                    objfile.write('f %d %d %d %d\n' % (quad[0], quad[1], quad[2], quad[3]))
                for triangle in side_faces:
                    objfile.write('f %d %d %d\n' % (triangle[0], triangle[1], triangle[2]))
        except IOError:
            return False

        return True

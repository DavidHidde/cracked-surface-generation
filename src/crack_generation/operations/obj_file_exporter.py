from crack_generation.models.crack import Crack


class ObjFileExporter:
    """
    Class that exports crack models into .obj files
    """

    def __call__(self, crack: Crack, filepath: str) -> bool:
        """
        Export a crack to a .obj file
        """

        faces = crack.mesh.faces + 1
        side_faces = crack.mesh.side_faces + 1

        try:
            with open(filepath, 'w') as objfile:
                for vertex in crack.mesh.vertices:
                    objfile.write('v %.4f %.4f %.4f\n' % (vertex[0], vertex[1], vertex[2]))
                for quad in faces:
                    objfile.write('f %d %d %d %d\n' % (quad[0], quad[1], quad[2], quad[3]))
                for triangle in side_faces:
                    objfile.write('f %d %d %d\n' % (triangle[0], triangle[1], triangle[2]))
        except IOError:
            return False

        return True

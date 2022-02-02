from audioop import cross
import pygame
import numpy as np

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

WIDTH = 800  # Dimensions of the screen.
HEIGHT = 450

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
SCREEN.fill(BLACK)

FPS = 60
THETA_INCREMENT = 0.02

# Constants for the projection matrix / other use.
OFFSET = 3
NEAR = 0.1
FAR = 1000
FOV = 90
ASPECTRATIO = HEIGHT / WIDTH  # 1.7777777
FOVRAD = 1 / (np.tan(FOV * 0.5 / 180 * np.pi))  # 1.0000000000000002

clock = pygame.time.Clock()

class Vec3D:  # Each Vec3D should be a point, with an x, y, z coordinate.
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def display(self):
        return self.x, self.y, self.z


class Triangle:  # Each triangle should be made up of 3 Vec3Ds
    def __init__(self, point1, point2, point3):
        self.points = [0, 0, 0]
        self.points[0] = Vec3D(point1[0], point1[1], point1[2])
        self.points[1] = Vec3D(point2[0], point2[1], point2[2])
        self.points[2] = Vec3D(point3[0], point3[1], point3[2])

    def display(self, index):  # Returns the Vec3D at each point.
        return self.points[index]


class Mesh:  # Each Mesh should be made up of triangles.
    def __init__(self, tris):
        self.tris = np.array(tris)

    def display_tris(self):
        print(self.tris)


class Matrix4x4:
    def __init__(self, type):
        self.matrix = np.full((4, 4), 0.0)  # Creates a 4x4 matrix of 0s.

        if type == "projection":
            self.matrix[0][0] = ASPECTRATIO * FOVRAD
            self.matrix[1][1] = FOVRAD
            self.matrix[2][2] = FAR / (FAR - NEAR)
            self.matrix[3][2] = ((-1 * FAR) * NEAR) / (FAR - NEAR)
            self.matrix[2][3] = 1.0
            self.matrix[3][3] = 0.0

        elif type == "z":  # Rotation around the z-axis
            self.matrix[0][0] = np.cos(theta)
            self.matrix[0][1] = np.sin(theta)
            self.matrix[1][0] = -1 * np.sin(theta)
            self.matrix[1][1] = np.cos(theta)
            self.matrix[2][2] = 1
            self.matrix[3][3] = 1

        elif type == "x":  # Rotation around the x-axis
            self.matrix[0][0] = 1
            self.matrix[1][1] = np.cos(theta * 0.5)
            self.matrix[1][2] = np.sin(theta * 0.5)
            self.matrix[2][1] = -1 * np.sin(theta * 0.5)
            self.matrix[2][2] = np.cos(theta * 0.5)
            self.matrix[3][3] = 1

    def display_matrix(self):
        return self.matrix


def matrix_vector_multiplication(inputv, matrix):  # Inputv is a vector, from the Vec3D class. Matrix is of the Matrix4x4 Class.
                                
    x = inputv.x * matrix.matrix[0][0] + inputv.y * matrix.matrix[1][0] + inputv.z * matrix.matrix[2][0] + matrix.matrix[3][0]
    y = inputv.x * matrix.matrix[0][1] + inputv.y * matrix.matrix[1][1] + inputv.z * matrix.matrix[2][1] + matrix.matrix[3][1]
    z = inputv.x * matrix.matrix[0][2] + inputv.y * matrix.matrix[1][2] + inputv.z * matrix.matrix[2][2] + matrix.matrix[3][2]
    w = inputv.x * matrix.matrix[0][3] + inputv.y * matrix.matrix[1][3] + inputv.z * matrix.matrix[2][3] + matrix.matrix[3][3]  # Has to be included due to the 4x4 matrix.

    outputv = Vec3D(x, y, z)

    if w != 0:
        outputv.x /= w
        outputv.y /= w
        outputv.z /= w

    return outputv


def update():
    pygame.display.update()


def on_user_update():

    points = [  # Coordinates of cube split into triangles.
        # South
        [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]],
        [[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 0.0, 0.0]],

        # East
        [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]],
        [[1.0, 0.0, 0.0], [1.0, 1.0, 1.0], [1.0, 0.0, 1.0]],

        # North
        [[1.0, 0.0, 1.0], [1.0, 1.0, 1.0], [0.0, 1.0, 1.0]],
        [[1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.0, 0.0, 1.0]],

        # West
        [[0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.0, 1.0, 0.0]],
        [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]],

        # Top
        [[0.0, 1.0, 0.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0]],
        [[0.0, 1.0, 0.0], [1.0, 1.0, 1.0], [1.0, 1.0, 0.0]],

        # Bottom
        [[1.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]],
        [[1.0, 0.0, 1.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]]

    cubeMesh = Mesh(points)

    projection = Matrix4x4("projection")  # Creates an instance of the projection matrix.

    rotation_z = Matrix4x4("z")  # Matrix for rotation around the z-axis.

    rotation_x = Matrix4x4("x")  # Matrix for rotation around the x-axis.

    SCREEN.fill(BLACK)
    for i in cubeMesh.tris:  # Iterates through .tris, getting each triangle's coordinates and feeding to the instance
        # of the Triangle class, called tri_projected.

        vec_one = Vec3D(i[0][0], i[0][1], i[0][2])
        vec_two = Vec3D(i[1][0], i[1][1], i[1][2])
        vec_three = Vec3D(i[2][0], i[2][1], i[2][2])

        vec_one = matrix_vector_multiplication(vec_one, rotation_z)  # Translates the vectors by a rotation in the z-axis.                                  
        vec_two = matrix_vector_multiplication(vec_two, rotation_z)
        vec_three = matrix_vector_multiplication(vec_three, rotation_z)

        vec_one = matrix_vector_multiplication(vec_one, rotation_x)  # Translates the vectors by a rotation in the x-axis.
        vec_two = matrix_vector_multiplication(vec_two, rotation_x)
        vec_three = matrix_vector_multiplication(vec_three, rotation_x)

        vec_one.z += OFFSET  # Offset
        vec_two.z += OFFSET
        vec_three.z += OFFSET

        line1 = Vec3D(); line2 = Vec3D(); normal = Vec3D()

        line1.x = vec_two.x - vec_one.x  # Line 1 is the vector A->B
        line1.y = vec_two.y - vec_one.y
        line1.z = vec_two.z - vec_one.z

        line2.x = vec_three.x - vec_one.x  # Line 2 is the vector A->C
        line2.y = vec_three.y - vec_one.y
        line2.z = vec_three.z - vec_one.z

        # Normal is the cross product of the two lines.
        normal.x = line1.y * line2.z - line1.z * line2.y
        normal.y = line1.z * line2.x - line1.x * line2.z
        normal.z = line1.x * line2.y - line1.y * line2.x

        # Normal is "normalised" into a unit vector, via calculating the magnitude of the normal and dividing each component
        # of the vector by said magnitude.

        normal_magnitude = np.sqrt(np.square(normal.x) + np.square(normal.y) + np.square(normal.z))
        normal.x /= normal_magnitude; normal.y /= normal_magnitude; normal.z /= normal_magnitude

        cross_product = normal.x * (vec_one.x - camera.x) + \
                        normal.y * (vec_one.y - camera.y) + \
                        normal.z * (vec_one.z - camera.z)

        if cross_product < 0:
            proj_vec1 = matrix_vector_multiplication(vec_one, projection)  # Multiplies vector by projection matrix.
            proj_vec2 = matrix_vector_multiplication(vec_two, projection)
            proj_vec3 = matrix_vector_multiplication(vec_three, projection)

            projected_triangle = Triangle(proj_vec1.display(), proj_vec2.display(), proj_vec3.display())

            # "Scale into view"
            projected_triangle.display(0).x += 1.0
            projected_triangle.display(0).y += 1.0
            projected_triangle.display(1).x += 1.0
            projected_triangle.display(1).y += 1.0
            projected_triangle.display(2).x += 1.0
            projected_triangle.display(2).y += 1.0

            projected_triangle.display(0).x *= 0.5 * WIDTH
            projected_triangle.display(0).y *= 0.5 * HEIGHT
            projected_triangle.display(1).x *= 0.5 * WIDTH
            projected_triangle.display(1).y *= 0.5 * HEIGHT
            projected_triangle.display(2).x *= 0.5 * WIDTH
            projected_triangle.display(2).y *= 0.5 * HEIGHT

            draw_triangle(projected_triangle)

    pygame.display.update()

    return


def draw_triangle(input_triangle):
    pygame.draw.line(SCREEN, WHITE, (input_triangle.display(0).x, input_triangle.display(0).y), (input_triangle.display(1).x, input_triangle.display(1).y))

    pygame.draw.line(SCREEN, WHITE, (input_triangle.display(1).x, input_triangle.display(1).y), (input_triangle.display(2).x, input_triangle.display(2).y))

    pygame.draw.line(SCREEN, WHITE, (input_triangle.display(2).x, input_triangle.display(2).y), (input_triangle.display(0).x, input_triangle.display(0).y))


def main():
    global theta
    global camera
    theta = 0
    camera = Vec3D()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Program has finished running.")
                running = False

        theta += THETA_INCREMENT  # Elapsed time.
        on_user_update()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


pygame.init()
main()

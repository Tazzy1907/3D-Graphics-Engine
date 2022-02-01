import pygame
import numpy as np

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

WIDTH = 1600 # Dimensions of the screen.
HEIGHT = 900

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
SCREEN.fill(BLACK)

# Constants for the projection matrix / other use.
NEAR = 0.1
FAR = 1000
FOV = 90
ASPECTRATIO = HEIGHT / WIDTH  # 1.7777777
FOVRAD = 1 / (np.tan(FOV * 0.5 / 180 * np.pi))  # 1.0000000000000002


class Vec3D: # Each Vec3D should be a point, with an x, y, z coordinate.
    def __init__(self, x, y, z):
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
            

class Mesh: # Each Mesh should be made up of triangles.
    def __init__(self):
        pass


    def add_tris(self, tris):
        self.tris = np.array(tris)


    def display_tris(self):
        print(self.tris)


class Matrix4x4:
    def __init__(self):
      self.matrix = np.full((4, 4), 0.0) # Creates a 4x4 matrix of 0s.
      self.projection_matrix()

  
    def display_matrix(self):
      print(self.matrix)

    
    def projection_matrix(self):
      self.matrix[0][0] = ASPECTRATIO * FOVRAD
      self.matrix[1][1] = FOVRAD
      self.matrix[2][2] = FAR / (FAR - NEAR)
      self.matrix[3][2] = ((-1 * FAR) * NEAR) / (FAR - NEAR)
      self.matrix[2][3] = 1.0
      self.matrix[3][3] = 0.0

    
    def rotation_z(self):
        self.matrix[0][0] = np.cos(theta)
        self.matrix[0][1] = np.sin(theta)
        self.matrix[1][0] = -1 * np.sin(theta)
        self.matrix[1][1] = np.cos(theta)
        self.matrix[2][2] = 1
        self.matrix[2][2] = 1
    

    def rotation_x(self):
        self.matrix[0][0] = 1
        self.matrix[1][1] = np.cos(theta * 0.5)
        self.matrix[1][2] = np.sin(theta * 0.5)
        self.matrix[2][1] = -1 * np.sin(theta * 0.5)
        self.matrix[2][2] = np.cos(theta * 0.5)
        self.matrix[3][3] = 1


def matrix_vector_multiplication(inputv, matrix): # Inputv is a vector, from the Vec3D class. Matrix is of the Matrix4x4 Class.
    x = inputv.x * matrix.matrix[0][0] + inputv.y * matrix.matrix[1][0] + inputv.z * matrix.matrix[2][0] + matrix.matrix[3][0]
    y = inputv.x * matrix.matrix[0][1] + inputv.y * matrix.matrix[1][1] + inputv.z * matrix.matrix[2][1] + matrix.matrix[3][1]
    z = inputv.x * matrix.matrix[0][2] + inputv.y * matrix.matrix[1][2] + inputv.z * matrix.matrix[2][2] + matrix.matrix[3][2]
    w = inputv.x * matrix.matrix[0][3] + inputv.y * matrix.matrix[1][3] + inputv.z * matrix.matrix[2][3] + matrix.matrix[3][3] # Has to be included due to the 4x4 matrix.

    outputv= Vec3D(x, y, z)

    if w != 0:
        outputv.x /= w
        outputv.y /= w
        outputv.z /= w

    return outputv


def update():
    pygame.display.update()


def on_user_update():
    cubeMesh = Mesh()
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

    cubeMesh.add_tris(points)

    projection = Matrix4x4() 
    projection.projection_matrix() # Creates an instance of the projection matrix.

    rotation_z = Matrix4x4() # Matrix for rotation around the z-axis.
    rotation_z.rotation_z
    
    rotation_x = Matrix4x4() # Matrix for rotation around the x-axis.
    rotation_x.rotation_x


    for i in cubeMesh.tris: # Iterates through .tris, getting each triangle's coordinates and feeding to the instance
         # of the Triangle class, called tri_projected.

        vec_one = Vec3D(i[0][0], i[0][1], i[0][2])
        vec_two = Vec3D(i[1][0], i[1][1], i[1][2])
        vec_three = Vec3D(i[2][0], i[2][1], i[2][2])
        
        vec_one.z += 3
        vec_two.z += 3
        vec_three.z += 3

        temp = Triangle(vec_one.display(), vec_two.display(), vec_three.display())

        proj_vec1 = matrix_vector_multiplication(temp.display(0), projection)  # Multiplies vector by projection matrix.
        proj_vec2 = matrix_vector_multiplication(temp.display(1), projection)
        proj_vec3 = matrix_vector_multiplication(temp.display(2), projection)
        
        projected_triangle = Triangle(proj_vec1.display(), proj_vec2.display(), proj_vec3.display())

        # "Scale into view"
        projected_triangle.display(0).x += 1.0; projected_triangle.display(0).y += 1.0
        projected_triangle.display(1).x += 1.0; projected_triangle.display(1).y += 1.0
        projected_triangle.display(2).x += 1.0; projected_triangle.display(2).y += 1.0

        projected_triangle.display(0).x *= 0.5 * WIDTH
        projected_triangle.display(0).y *= 0.5 * HEIGHT
        projected_triangle.display(1).x *= 0.5 * WIDTH
        projected_triangle.display(1).y *= 0.5 * HEIGHT
        projected_triangle.display(2).x *= 0.5 * WIDTH
        projected_triangle.display(2).y *= 0.5 * HEIGHT

        draw_triangle(projected_triangle)
        
    return    


def draw_triangle(input_triangle):
    
    pygame.draw.line(SCREEN, WHITE, (input_triangle.display(0).x, input_triangle.display(0).y),
                    (input_triangle.display(1).x, input_triangle.display(1).y))
    pygame.draw.line(SCREEN, WHITE, (input_triangle.display(1).x, input_triangle.display(1).y),
                    (input_triangle.display(2).x, input_triangle.display(2).y))
    pygame.draw.line(SCREEN, WHITE, (input_triangle.display(2).x, input_triangle.display(2).y),
                    (input_triangle.display(0).x, input_triangle.display(0).y))


def main():
    global theta
    theta = 1


    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Program has finished running.")
                running = False
        
        theta += 1  # Elapsed time.
        on_user_update()
        pygame.display.flip()

    pygame.quit()

pygame.init()
main()

    

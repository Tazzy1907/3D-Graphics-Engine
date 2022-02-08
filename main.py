import pygame
import numpy as np

# Constants

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

WIDTH = 1600  # Dimensions of the screen.
HEIGHT = 900

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))  # PyGame init constants.
SCREEN.fill(BLACK)

clock = pygame.time.Clock()  # FPS / Clock Function
FPS = 60

theta = 0  # Theta is used for elapsed time.
THETA_INCREMENT = 0.02

LEAVE_TRAIL = False  # Change if user wishes to leave a trail behind. (Not refreshing the screen after an image has been drawn.)
DRAW_NET = False  # Change if the user wishes only to view the edges of the shape, and not whole colours.

# Constants for the mathematic functions.
OFFSET = 6
NEAR = 0.1
FAR = 1000
FOV = 90
ASPECTRATIO = HEIGHT / WIDTH  # 1.7777777
FOVRAD = 1 / (np.tan(FOV * 0.5 / 180 * np.pi))  # 1.0000000000000002

# Locations
SPHERE_LOCATION = r'sphereblend.obj'
TORUS_LOCATION = r'torus.obj'
MONKEY_LOCATION = '' # Needs to be input.


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
        return self.tris


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


def analyse_file(file):  # Function to read through object files.
    file_contents = []
    coords = []
    addresses = []

    for line in file:
        file_contents.append(line)

    for i in range(3):
        file_contents.pop(0)

    address_count = 0
    for i in range(len(file_contents)):
        if file_contents[i][0] == 'v':
            file_contents[i] = file_contents[i][2:]
            file_contents[i] == file_contents[i][:-1]
            coords.append(file_contents[i].split())

            for j in range(len(coords[i])):
                coords[i][j] = float(coords[i][j])

        
        elif file_contents[i][0] == "f":
            file_contents[i] = file_contents[i][2:]
            file_contents[i] == file_contents[i][:-1]
            addresses.append(file_contents[i].split())

            for j in range(len(addresses[address_count])):
                addresses[address_count][j] = int(addresses[address_count][j])
            address_count += 1
    
    return coords, addresses


def create_tris(file):  # Creates triangles for the mesh to form.
    coords, addresses = analyse_file(file)
    triangles = []
    for triangle_face in addresses:
        triangle = []
        for address in triangle_face:
            triangle.append(coords[address - 1])
        triangles.append(triangle)
        
    return triangles


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


def normalise(vector, component):  # Function to normalise vectors by creating a unit vector.
    magnitude = np.sqrt(np.square(vector.x) + np.square(vector.y) + np.square(vector.z))
    vector.x /= magnitude; vector.y /= magnitude; vector.z /= magnitude

    if component == 'x':
        return vector.x
    elif component == 'y':
        return vector.y
    elif component == 'z':
        return vector.z


def dot_product(vector1, vector2):
    dp = (vector1.x * vector2.x) + (vector1.y * vector2.y) + (vector1.z * vector2.z)

    return dp


def cube():
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

    return cubeMesh


def sphere():
    file = open(SPHERE_LOCATION)
    
    points = create_tris(file)

    sphereMesh = Mesh(points)

    return sphereMesh


def torus():
    file = open(TORUS_LOCATION)

    points = create_tris(file)

    torusMesh = Mesh(points)

    return torusMesh


def colour_scale(dot_product, colour=np.full(3, 0.0)):
    for i in range(3):
        colour[0] = 255 * abs(dot_product)  # Abs function has been added as a temporary fix.
        colour[2] = 255 * abs(dot_product)

    return colour


def draw_points(mesh):
    projection = Matrix4x4("projection")  # Creates an instance of the projection matrix.
    rotation_z = Matrix4x4("z")  # Matrix for rotation around the z-axis.
    rotation_x = Matrix4x4("x")  # Matrix for rotation around the x-axis.

    if not LEAVE_TRAIL:
        SCREEN.fill(BLACK)

    for i in mesh.tris:  # Iterates through .tris, getting each triangle's coordinates and feeding to the instance
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

        normal.x = normalise(normal, 'x'); normal.y = normalise(normal, 'y'); normal.z = normalise(normal, 'z') 

        camera_to_normal = Vec3D(vec_one.x - camera.x, vec_one.y - camera.y, vec_one.z - camera.z) # Vector of camera to the normal.

        normal_dp = dot_product(normal, camera_to_normal)

        if normal_dp < 0:
            
            light_direction = Vec3D(0, 0, -1)  # Lighting, facing towards the play. Done so that we check how aligned the normal of a 
            # plane is with the light direction. Just like above, the light direction is normalised to a unit vector.
            light_direction.x = normalise(light_direction, 'x'); light_direction.y = normalise(light_direction, 'y')
            light_direction.z = normalise(light_direction, 'z')

            light_dp = dot_product(normal, light_direction)

            colour_scale(light_dp)

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

            draw_triangle(projected_triangle, colour_scale(light_dp))

    pygame.display.update()
    
    return
    

def draw_triangle(input_triangle, colour=WHITE):
    if not DRAW_NET:
        pygame.draw.polygon(SCREEN, colour, (
            (input_triangle.display(0).x, input_triangle.display(0).y),  # Points of triangle.
            (input_triangle.display(1).x, input_triangle.display(1).y),
            (input_triangle.display(2).x, input_triangle.display(2).y)))
    else:
        pygame.draw.line(SCREEN, colour, (input_triangle.display(0).x, input_triangle.display(0).y),
                     (input_triangle.display(1).x, input_triangle.display(1).y))
        pygame.draw.line(SCREEN, WHITE, (input_triangle.display(1).x, input_triangle.display(1).y),
                        (input_triangle.display(2).x, input_triangle.display(2).y))
        pygame.draw.line(SCREEN, WHITE, (input_triangle.display(2).x, input_triangle.display(2).y),
                        (input_triangle.display(0).x, input_triangle.display(0).y))

    return


def on_user_update():
    cubeMesh = cube()  # Contains points for a 3D cube.
    sphereMesh = sphere()
    torusMesh = torus()
    
    draw_points(torusMesh)
    
    return


def main():
    global camera
    global theta

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

    return


pygame.init()
main()

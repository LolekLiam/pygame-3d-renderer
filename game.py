import pygame
import math

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("3D Renderer")
clock = pygame.time.Clock()
running = True

# cam settings
cam_x, cam_y, cam_z = 0, 0, -500
cam_f = 500
move_speed = 1
mouse_sensitivity = 0.002

# cam rotation
cam_yaw = -math.pi  # left/right
cam_pitch = math.pi  # up/down

# cube rotation (roll, pitch, yaw)
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0 

# mouse control
mouse_locked = True
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

font = pygame.font.SysFont("Arial", 20)

class Render:
    def __init__(self, x, y, z, f): # def __init__(self, x, y, z, f, size): (old code)
        self.x = x
        self.y = y
        self.z = z
        self.f = f  # perspective (view distance)
        #self.size = size  # scale

    #def scale(self):
        #"""Scale the object (size adjustment)."""
        #self.x *= self.size
        #self.y *= self.size
        #self.z *= self.size

    def rotate_x(self, angle_x):
        """Rotate around the X-axis (pitch)."""
        cos_x = math.cos(angle_x)
        sin_x = math.sin(angle_x)
        new_y = self.y * cos_x - self.z * sin_x
        new_z = self.y * sin_x + self.z * cos_x
        self.y, self.z = new_y, new_z

    def rotate_y(self, angle_y):
        """Rotate around the Y-axis (yaw)."""
        cos_y = math.cos(angle_y)
        sin_y = math.sin(angle_y)
        new_x = self.x * cos_y + self.z * sin_y
        new_z = -self.x * sin_y + self.z * cos_y
        self.x, self.z = new_x, new_z

    def rotate_z(self, angle_z):
        """Rotate around the Z-axis (roll)."""
        cos_z = math.cos(angle_z)
        sin_z = math.sin(angle_z)
        new_x = self.x * cos_z - self.y * sin_z
        new_y = self.x * sin_z + self.y * cos_z
        self.x, self.y = new_x, new_y

    def project(self):
        """Project the 3D point to 2D screen coordinates."""
        if self.z <= 0.1:  # prevent division by very small or negative numbers
            return None  # don't render points behind or too close to cam

        proj_x = (self.x / self.z) * self.f
        proj_y = (self.y / self.z) * self.f
        return (int(proj_x + 640), int(proj_y + 360))

    def process(self, cam_x, cam_y, cam_z, cam_yaw, cam_pitch, angle_x, angle_y, angle_z):
        #self.scale()

        # rotate the cube around its own center
        self.rotate_x(angle_x)
        self.rotate_y(angle_y)
        self.rotate_z(angle_z)

        # translate relative to the cam
        self.x -= cam_x
        self.y -= cam_y
        self.z -= cam_z

        # rotate the cube relative to the cam yaw and pitch
        self.rotate_y(cam_yaw)  # apply cam yaw (left/right)
        self.rotate_x(cam_pitch)  # apply cam pitch (up/down)

        return self.project()


def draw_cube(cube_x, cube_y, cube_z, scale, angle_x, angle_y, angle_z, cam_x, cam_y, cam_z, cam_yaw, cam_pitch):
    # cube vertices (reset every frame)
    vertices = [
        Render(cube_x+scale, cube_y+scale, cube_z+scale, cam_f),
        Render(-cube_x-scale, cube_y+scale, cube_z+scale, cam_f),
        Render(-cube_x-scale, -cube_y-scale, cube_z+scale, cam_f),
        Render(cube_x+scale, -cube_y-scale, cube_z+scale, cam_f),
        Render(cube_x+scale, cube_y+scale, -cube_z-scale, cam_f),
        Render(-cube_x-scale, cube_y+scale, -cube_z-scale, cam_f),
        Render(-cube_x-scale, -cube_y-scale, -cube_z-scale, cam_f),
        Render(cube_x+scale, -cube_y-scale, -cube_z-scale, cam_f)
    ]

    # cube edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    # process and store projected points
    projected_vertices = []
    for v in vertices:
        projected = v.process(cam_x, cam_y, cam_z, cam_yaw, cam_pitch, angle_x, angle_y, angle_z)
        if projected:  # only render points in front of cam
            projected_vertices.append(projected)

    # draw edges only if both vertices are visible
    for start, end in edges:
        if start < len(projected_vertices) and end < len(projected_vertices):
            pygame.draw.line(screen, (255, 255, 255), projected_vertices[start], projected_vertices[end], 2)

    # draw vertices
    for p in projected_vertices:
        pygame.draw.circle(screen, (255, 255, 255), p, 5)

    return angle_x, angle_y, angle_z

def draw_grid(cam_x, cam_y, cam_z, cam_yaw, cam_pitch):
    grid_size = 500
    grid_step = 10
    for x in range(-grid_size, grid_size + 1, grid_step):
        for z in range(-grid_size, grid_size + 1, grid_step):
            # create a point on the grid
            point = Render(x, 0, z, cam_f)
            projected = point.process(cam_x, cam_y, cam_z, cam_yaw, cam_pitch, 0, 0, 0)
            if projected:
                pygame.draw.circle(screen, (100, 100, 100), projected, 1)

# function for doing nothing
def do_nothing():
    return None

def draw_text():
    # cam direction (yaw and pitch)
    direction_text = f"Yaw: {cam_yaw:.2f}, Pitch: {cam_pitch:.2f}"
    direction_surface = font.render(direction_text, True, (255, 255, 255))
    screen.blit(direction_surface, (10, 10))

    # cam position (x, y, z)
    position_text = f"Position: ({cam_x:.2f}, {cam_y:.2f}, {cam_z:.2f})"
    position_surface = font.render(position_text, True, (255, 255, 255))
    screen.blit(position_surface, (screen.get_width() - position_surface.get_width() - 10, 10))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                mouse_locked = not mouse_locked
                pygame.mouse.set_visible(not mouse_locked)
                pygame.event.set_grab(mouse_locked)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not mouse_locked:
                mouse_locked = True
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        cam_x += move_speed * math.sin(cam_yaw)
        cam_z -= move_speed * math.cos(cam_yaw)
    if keys[pygame.K_s]:
        cam_x -= move_speed * math.sin(cam_yaw)
        cam_z += move_speed * math.cos(cam_yaw)
    if keys[pygame.K_a]:
        cam_x -= move_speed * math.cos(cam_yaw)
        cam_z -= move_speed * math.sin(cam_yaw)
    if keys[pygame.K_d]:
        cam_x += move_speed * math.cos(cam_yaw)
        cam_z += move_speed * math.sin(cam_yaw)
    if keys[pygame.K_SPACE]:
        cam_y += move_speed 
    if keys[pygame.K_LSHIFT]:
        cam_y -= move_speed

    if mouse_locked:
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        cam_yaw += mouse_dx * mouse_sensitivity
        cam_pitch += mouse_dy * mouse_sensitivity

        # clamp pitch by radians
        cam_pitch = max(math.pi/2, min((3*math.pi)/2, cam_pitch))

    # cube rotation
    #angle_x += 0.01
    #angle_y += 0.01
    #angle_z += 0.01

    screen.fill("black")
    draw_grid(cam_x, cam_y, cam_z, cam_yaw, cam_pitch)
    # draw cube with custom width, height and lenght
    angle_x, angle_y, angle_z = draw_cube(30, 10, 60, 50, angle_x, angle_y, angle_z, cam_x, cam_y, cam_z, cam_yaw, cam_pitch) # width, height, lenght, scale
    draw_text()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# todo:
# - make draw cube accept coords based on where the origin point/absolute center of the cube would be
# - fix camera bug where putting the mouse back in focus affects the camera
# - make cube grid
# - add collision and movement physics
# - make the rest of the game
# - try not to go insane

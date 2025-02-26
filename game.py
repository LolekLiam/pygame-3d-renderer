import pygame
import math

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("3D Renderer")
clock = pygame.time.Clock()
running = True

class Render:
    def __init__(self, x, y, z, f, size):
        self.x = x
        self.y = y
        self.z = z
        self.f = f  # Perspective factor (view distance)
        self.size = size  # Scale factor

    def scale(self):
        """Scale the object (size adjustment)."""
        self.x *= self.size
        self.y *= self.size
        self.z *= self.size

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
        if self.z <= 0.1:  # Prevent division by very small or negative numbers
            return (640, 360)  # Default to center of screen (optional safeguard)

        proj_x = (self.x / self.z) * self.f
        proj_y = (self.y / self.z) * self.f
        return (int(proj_x + 640), int(proj_y + 360))

    def process(self, cam_x, cam_y, cam_z, angle_x, angle_y, angle_z):

        self.scale()

    # Rotate around its own center
        self.rotate_x(angle_x)
        self.rotate_y(angle_y)
        self.rotate_z(angle_z)

    # Now translate relative to the camera
        self.x -= cam_x
        self.y -= cam_y
        self.z -= cam_z

        return self.project()


def draw_cube(angle_x, angle_y, angle_z):
    """Create a rotating cube and project its vertices."""
    # Define the cube's vertices (reset every frame)
    vertices = [
        Render(1, 1, 1, 500, 100),
        Render(-1, 1, 1, 500, 100),
        Render(-1, -1, 1, 500, 100),
        Render(1, -1, 1, 500, 100),
        Render(1, 1, -1, 500, 100),
        Render(-1, 1, -1, 500, 100),
        Render(-1, -1, -1, 500, 100),
        Render(1, -1, -1, 500, 100),
    ]

    # Cube's edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    # Camera settings
    cam_x, cam_y, cam_z = 0, 0, -500

    # Process and store projected points
    projected_vertices = [v.process(cam_x, cam_y, cam_z, angle_x, angle_y, angle_z) for v in vertices]

    # Draw vertices
    for p in projected_vertices:
        pygame.draw.circle(screen, (255, 255, 255), p, 5)

    # Draw edges
    for start, end in edges:
        pygame.draw.line(screen, (255, 255, 255), projected_vertices[start], projected_vertices[end], 2)

    return angle_x, angle_y, angle_z


# Initialize rotation angles before the loop
angle_x, angle_y, angle_z = 0.01, 0.01, 0.01

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Increment the rotation angles to create rotation effect
    angle_x += 0.01
    angle_y += 0.01
    angle_z += 0.01

    screen.fill("black")  # Clear the screen
    angle_x, angle_y, angle_z = draw_cube(angle_x, angle_y, angle_z)  # Draw rotating cube and update angles
    pygame.display.flip()  # Update the display
    clock.tick(60)  # Control the frame rate

pygame.quit()

import pygame
import math

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("3D Renderer")
clock = pygame.time.Clock()
running = True

# Camera settings (persistent across frames)
cam_x, cam_y, cam_z = 0, 0, -500  # Initial camera position (farther away)
move_speed = 1  # Faster movement speed
mouse_sensitivity = 0.002

# Camera rotation (yaw and pitch)
cam_yaw = -math.pi  # Left/right rotation
cam_pitch = math.pi  # Up/down rotation

# Cube rotation (roll, pitch, yaw)
angle_x, angle_y, angle_z = 0.01, 0.01, 0.01  # Cube's rotation angles

# Mouse control settings
mouse_locked = True
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# Font for displaying text
font = pygame.font.SysFont("Arial", 20)


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
        """Project the 3D point to 2D screen coordinates."""
        if self.z <= 0.1:  # Prevent division by very small or negative numbers
            return None  # Don't render points behind or too close to the camera

        proj_x = (self.x / self.z) * self.f
        proj_y = (self.y / self.z) * self.f
        return (int(proj_x + 640), int(proj_y + 360))

    def process(self, cam_x, cam_y, cam_z, cam_yaw, cam_pitch, angle_x, angle_y, angle_z):
        self.scale()

        # Rotate the cube around its own center
        self.rotate_x(angle_x)
        self.rotate_y(angle_y)
        self.rotate_z(angle_z)

        # Translate relative to the camera
        self.x -= cam_x
        self.y -= cam_y
        self.z -= cam_z

        # Rotate the cube relative to the camera's yaw and pitch
        self.rotate_y(cam_yaw)  # Apply camera yaw (left/right)
        self.rotate_x(cam_pitch)  # Apply camera pitch (up/down)

        return self.project()


def draw_cube(angle_x, angle_y, angle_z, cam_x, cam_y, cam_z, cam_yaw, cam_pitch):
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

    # Process and store projected points
    projected_vertices = []
    for v in vertices:
        projected = v.process(cam_x, cam_y, cam_z, cam_yaw, cam_pitch, angle_x, angle_y, angle_z)
        if projected:  # Only render points in front of the camera
            projected_vertices.append(projected)

    # Draw edges (only if both vertices are visible)
    for start, end in edges:
        if start < len(projected_vertices) and end < len(projected_vertices):
            pygame.draw.line(screen, (255, 255, 255), projected_vertices[start], projected_vertices[end], 2)

    # Draw vertices
    for p in projected_vertices:
        pygame.draw.circle(screen, (255, 255, 255), p, 5)

    return angle_x, angle_y, angle_z


def draw_grid(cam_x, cam_y, cam_z, cam_yaw, cam_pitch):
    """Draw a grid on the ground for visual reference."""
    grid_size = 10
    grid_step = 1
    for x in range(-grid_size, grid_size + 1, grid_step):
        for z in range(-grid_size, grid_size + 1, grid_step):
            # Create a point on the grid
            point = Render(x, 0, z, 500, 100)
            projected = point.process(cam_x, cam_y, cam_z, cam_yaw, cam_pitch, 0, 0, 0)
            if projected:
                pygame.draw.circle(screen, (100, 100, 100), projected, 1)


def draw_text():
    """Draw camera direction and position on the screen."""
    # Camera direction (yaw and pitch)
    direction_text = f"Yaw: {cam_yaw:.2f}, Pitch: {cam_pitch:.2f}"
    direction_surface = font.render(direction_text, True, (255, 255, 255))
    screen.blit(direction_surface, (10, 10))

    # Camera position (x, y, z)
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

    # Handle keyboard input for camera movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        # Move forward relative to camera yaw
        cam_x += move_speed * math.sin(cam_yaw)
        cam_z -= move_speed * math.cos(cam_yaw)
    if keys[pygame.K_s]:
        # Move backward relative to camera yaw
        cam_x -= move_speed * math.sin(cam_yaw)
        cam_z += move_speed * math.cos(cam_yaw)
    if keys[pygame.K_a]:
        # Strafe left relative to camera yaw
        cam_x -= move_speed * math.cos(cam_yaw)
        cam_z -= move_speed * math.sin(cam_yaw)
    if keys[pygame.K_d]:
        # Strafe right relative to camera yaw
        cam_x += move_speed * math.cos(cam_yaw)
        cam_z += move_speed * math.sin(cam_yaw)
    if keys[pygame.K_SPACE]:
        cam_y += move_speed  # Move up
    if keys[pygame.K_LSHIFT]:
        cam_y -= move_speed  # Move down

    # Handle mouse movement for camera rotation
    if mouse_locked:
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        cam_yaw += mouse_dx * mouse_sensitivity  # Yaw (left/right)
        cam_pitch += mouse_dy * mouse_sensitivity  # Pitch (up/down)

        # Clamp pitch to avoid flipping
        cam_pitch = max(math.pi/2, min((3*math.pi)/2, cam_pitch))

    # Increment the cube's rotation angles for animation
    angle_x += 0.01
    angle_y += 0.01
    angle_z += 0.01

    screen.fill("black")  # Clear the screen
    draw_grid(cam_x, cam_y, cam_z, cam_yaw, cam_pitch)  # Draw grid for visual reference
    angle_x, angle_y, angle_z = draw_cube(angle_x, angle_y, angle_z, cam_x, cam_y, cam_z, cam_yaw, cam_pitch)  # Draw cube
    draw_text()  # Draw camera direction and position
    pygame.display.flip()  # Update the display
    clock.tick(60)  # Control the frame rate

pygame.quit()

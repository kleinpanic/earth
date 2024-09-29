import curses
import numpy as np
import math
import time

# Define the rotation speed of the globe
ROTATION_SPEED = 0.02

# Define the radius of the globe (in terms of terminal characters)
RADIUS = 10

# Define the number of latitude and longitude lines for the wireframe
NUM_LATITUDE_LINES = 12
NUM_LONGITUDE_LINES = 24

# Define characters for drawing the wireframe
WIREFRAME_CHAR = '◦'
CONTINENT_CHAR = '■'  # Different character for continents outline

# A simplified list of latitude and longitude points for continents
# This is a minimal representation; a real globe would need a much larger dataset
CONTINENT_POINTS = [
    # Example points for North America, Europe, Africa, etc.
    (45, -100), (60, -100), (30, -90),  # North America
    (50, 0), (55, 10), (60, 20),  # Europe
    (0, 10), (-10, 20), (-30, 10),  # Africa
    (-20, -50), (-30, -60), (-10, -70),  # South America
    (10, 100), (20, 120), (-10, 130),  # Asia
]

# Function to convert latitude and longitude into 3D points on the globe
def lat_lon_to_xyz(lat, lon, radius):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = radius * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius * math.sin(lat_rad)
    return x, y, z

# Function to project 3D points to 2D terminal coordinates
def project(x, y, z, screen_width, screen_height, scale=1):
    factor = scale / (z + 3)
    proj_x = int(screen_width / 2 + x * factor * screen_width / 4)
    proj_y = int(screen_height / 2 - y * factor * screen_height / 4)
    return proj_x, proj_y

# Function to generate globe wireframe points
def generate_globe(radius, lat_lines, long_lines):
    points = []
    for lat in range(0, lat_lines + 1):
        theta = lat * math.pi / lat_lines
        for lon in range(0, long_lines + 1):
            phi = lon * 2 * math.pi / long_lines
            x = radius * math.sin(theta) * math.cos(phi)
            y = radius * math.sin(theta) * math.sin(phi)
            z = radius * math.cos(theta)
            points.append((x, y, z))
    return points

# Function to apply rotation to the globe
def rotate(point, angle_x, angle_y, angle_z):
    x, y, z = point

    # Rotation around X-axis
    y, z = y * math.cos(angle_x) - z * math.sin(angle_x), y * math.sin(angle_x) + z * math.cos(angle_x)
    
    # Rotation around Y-axis
    x, z = x * math.cos(angle_y) + z * math.sin(angle_y), -x * math.sin(angle_y) + z * math.cos(angle_y)
    
    # Rotation around Z-axis
    x, y = x * math.cos(angle_z) - y * math.sin(angle_z), x * math.sin(angle_z) + y * math.cos(angle_z)

    return x, y, z

# Main drawing function
def draw_globe(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)
    stdscr.timeout(50)

    screen_height, screen_width = stdscr.getmaxyx()
    globe_points = generate_globe(RADIUS, NUM_LATITUDE_LINES, NUM_LONGITUDE_LINES)
    angle_x = angle_y = angle_z = 0

    # Convert continent points to 3D points
    continent_points_3d = [lat_lon_to_xyz(lat, lon, RADIUS) for lat, lon in CONTINENT_POINTS]

    while True:
        stdscr.clear()

        # Increment angles for rotation
        angle_x += ROTATION_SPEED
        angle_y += ROTATION_SPEED / 2  # Slow Y-axis rotation for realism
        angle_z += ROTATION_SPEED / 4  # Slow Z-axis rotation for realism

        # Draw the wireframe globe by rotating points and projecting them
        for point in globe_points:
            rotated_point = rotate(point, angle_x, angle_y, angle_z)
            proj_x, proj_y = project(*rotated_point, screen_width, screen_height)
            if 0 <= proj_x < screen_width and 0 <= proj_y < screen_height:
                stdscr.addch(proj_y, proj_x, WIREFRAME_CHAR)

        # Draw the continent outlines
        for point in continent_points_3d:
            rotated_point = rotate(point, angle_x, angle_y, angle_z)
            proj_x, proj_y = project(*rotated_point, screen_width, screen_height)
            if 0 <= proj_x < screen_width and 0 <= proj_y < screen_height:
                stdscr.addch(proj_y, proj_x, CONTINENT_CHAR)

        stdscr.refresh()

        try:
            key = stdscr.getch()
            if key == ord('q'):
                break  # Quit the application
        except Exception:
            pass

        time.sleep(0.05)

# Main entry point for curses wrapper
if __name__ == "__main__":
    curses.wrapper(draw_globe)

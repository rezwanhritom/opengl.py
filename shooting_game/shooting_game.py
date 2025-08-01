# Import OpenGL modules for 3D graphics rendering
from OpenGL.GL import *    # Core OpenGL functions
from OpenGL.GLUT import *  # OpenGL Utility Toolkit for window management and input
from OpenGL.GLU import *   # OpenGL Utility Library for higher level functions
import random             # For generating random positions of enemies
import math              # For trigonometric calculations and other math operations
import time             # For timing-based animations

# Basic game configuration constants
GRID_LENGTH = 1000      # Defines the size of the game world grid (2000x2000 total area)
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800  # Window dimensions in pixels
FOV_Y = 120            # Field of view angle in degrees (vertical)

# Player related variables
player_pos = [0, 400, 0]  # Initial player position [x, y, z] - starts at middle-front
player_angle = 180        # Initial player rotation angle (facing north)

# Camera control variables
camera_mode = 0           # 0 for third-person view, 1 for first-person view
camera_angle = 0          # Rotation angle of the orbit camera
camera_radius = 1200      # Distance of camera from center in third-person view
camera_height = 500       # Height of camera above ground
camera_min_radius = 300   # Minimum zoom distance
camera_max_radius = 2000  # Maximum zoom distance

# Game state variables
bullets = []              # List to store active bullets [position, velocity]
enemies = []              # List to store enemy positions
enemy_size = 80          # Size of enemy models (collision detection)
enemy_pulse_scale = 1.0   # Current scale factor for enemy pulsing animation
lives = 5                # Player's starting lives
missed = 0               # Counter for missed shots
score = 0                # Player's score
cheat_mode = False       # Toggle for automatic aiming/shooting
cheat_vision = False     # Toggle for enhanced vision (not implemented)
game_over = False        # Game state flag

# Animation timing
pulse_time = 0           # Timer for enemy pulsing animation

def reset_enemies():
    """
    Initializes or resets the enemy positions in the game.
    Creates 5 enemies at random positions within the game grid.
    Called at game start and when restarting the game.
    """
    global enemies
    enemies = []  # Clear existing enemies
    for _ in range(5):  # Create 5 enemies
        # Random x,y positions between -900 and 900 to keep enemies within walls
        x, y = random.randint(-900, 900), random.randint(-900, 900)
        enemies.append([x, y, 0])  # Add enemy with z=0 (ground level)

# Initialize enemies at game start
reset_enemies()


"""
Function: draw_text
Purpose: Renders 2D text overlay on the OpenGL scene for displaying game information
Parameters:
    x, y: Screen coordinates for text position
    text: String to display
    font: GLUT bitmap font to use (default: GLUT_BITMAP_HELVETICA_18)
"""
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)  # Set text color to white
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix
    glPushMatrix()  # Save current projection matrix
    glLoadIdentity()  # Reset projection matrix
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)  # Set up 2D orthographic projection
    glMatrixMode(GL_MODELVIEW)  # Switch to modelview matrix
    glPushMatrix()  # Save current modelview matrix
    glLoadIdentity()  # Reset modelview matrix
    glRasterPos2f(x, y)  # Set position for text drawing
    for ch in text:  # Draw each character
        glutBitmapCharacter(font, ord(ch))  # Convert char to ASCII and draw
    glPopMatrix()  # Restore previous modelview matrix
    glMatrixMode(GL_PROJECTION)  # Switch back to projection matrix
    glPopMatrix()  # Restore previous projection matrix
    glMatrixMode(GL_MODELVIEW)  # Switch back to modelview matrix


"""
Function: draw_tapered_cylinder
Purpose: Creates a 3D cylinder with different radii at top and bottom
Parameters:
    base_radius: Radius at the bottom of cylinder
    top_radius: Radius at the top of cylinder
    height: Height of the cylinder
    color: RGB tuple for cylinder color
Used for: Creating limbs and gun parts of the player model
"""
def draw_tapered_cylinder(base_radius, top_radius, height, color):
    glColor3f(*color)  # Set cylinder color
    quadric = gluNewQuadric()  # Create new quadric object
    gluCylinder(quadric, base_radius, top_radius, height, 20, 8)  # Draw cylinder body
    
    # Draw bottom cap
    glPushMatrix()
    gluDisk(quadric, 0, base_radius, 20, 8)  # Create circular base
    glPopMatrix()
    
    # Draw top cap
    glPushMatrix()
    glTranslatef(0, 0, height)  # Move to top of cylinder
    gluDisk(quadric, 0, top_radius, 20, 8)  # Create circular top
    glPopMatrix()


"""
Function: draw_player
Purpose: Renders the player character model using OpenGL primitives
Components:
    - Body: Olive colored cuboid
    - Head: Black sphere
    - Gun: Gray tapered cylinder
    - Arms: Yellow tapered cylinders
    - Legs: Blue tapered cylinders
"""
def draw_player():
    glPushMatrix()  # Save current transformation matrix
    # Position player in world and apply rotation
    glTranslatef(player_pos[0], player_pos[1], player_pos[2] + 160)
    glRotatef(player_angle, 0, 0, 1)

    # Draw body
    glColor3f(0.5, 0.5, 0.0)
    glPushMatrix()
    glScalef(1.0, 0.8, 2.0)  # Scale for body proportions
    glutSolidCube(100)
    glPopMatrix()

    # Head (black sphere)
    glPushMatrix()
    glTranslatef(0, 0, 120)
    glColor3f(0, 0, 0)
    glutSolidSphere(25, 20, 20)
    glPopMatrix()

    # Gun - centered and pointing forward
    glPushMatrix()
    glTranslatef(0, 60, 80)   # Position in front of body
    glRotatef(-90, 1, 0, 0)   # Point forward horizontally
    draw_tapered_cylinder(25, 10, 120, (0.5, 0.5, 0.5))  # Larger and more tapered
    glPopMatrix()

    # Left arm
    glPushMatrix()
    glTranslatef(-25, 60, 80)
    glRotatef(-90, 1, 0, 0)
    glRotatef(15, 0, 1, 0)
    draw_tapered_cylinder(18, 6, 100, (1.0, 1.0, 0.5))
    glPopMatrix()

    # Right arm
    glPushMatrix()
    glTranslatef(25, 60, 80)
    glRotatef(-90, 1, 0, 0)
    glRotatef(-15, 0, 1, 0)
    draw_tapered_cylinder(18, 6, 100, (1.0, 1.0, 0.5))
    glPopMatrix()

    # Left leg - pointing straight down
    glPushMatrix()
    glTranslatef(-30, 0, -100)  # Attach to bottom of body
    glRotatef(180, 1, 0, 0)     # Point downwards
    draw_tapered_cylinder(25, 8, 120, (0.0, 0.0, 0.5))
    glPopMatrix()

    # Right leg - pointing straight down
    glPushMatrix()
    glTranslatef(30, 0, -100)   # Attach to bottom of body
    glRotatef(180, 1, 0, 0)     # Point downwards
    draw_tapered_cylinder(25, 8, 120, (0.0, 0.0, 0.5))
    glPopMatrix()

    glPopMatrix()


"""
Function: draw_enemy
Purpose: Renders enemy characters with pulsing animation effect
Parameters:
    pos: [x, y, z] position of enemy in world space
Features:
    - Red spherical body
    - Black spherical head
    - Pulsing scale animation
"""
def draw_enemy(pos):
    x, y, z = pos  # Extract position components
    glPushMatrix()
    glTranslatef(x, y, z)  # Position enemy in world
    glScalef(enemy_pulse_scale, enemy_pulse_scale, enemy_pulse_scale)  # Apply pulse animation

    # Draw main body
    glColor3f(1, 0, 0)  # Red color
    glutSolidSphere(enemy_size, 20, 20)  # Create sphere

    # Draw head
    glPushMatrix()
    glTranslatef(0, 0, enemy_size + 5)  # Position head above body
    glColor3f(0, 0, 0)  # Black color
    glutSolidSphere(enemy_size * 0.5, 20, 20)  # Create smaller sphere
    glPopMatrix()

    glPopMatrix()


"""
Function: draw_bullet
Purpose: Renders a single bullet in the game world
Parameters:
    bullet: [x, y, z] position coordinates of the bullet
Features:
    - Creates a small green cube to represent the bullet
"""
def draw_bullet(bullet):
    x, y, z = bullet  # Extract bullet position coordinates
    glPushMatrix()  # Save current transformation state
    glTranslatef(x, y, z)  # Move to bullet position
    glColor3f(0, 1, 0)  # Set bullet color to green
    glutSolidCube(10)  # Draw a small cube for the bullet
    glPopMatrix()  # Restore transformation state


"""
Function: fire_bullet
Purpose: Creates a new bullet when player shoots
Features:
    - Calculates bullet spawn position at gun tip
    - Sets bullet velocity based on player angle
    - Handles game over state
    - Applies proper coordinate transformations
"""
def fire_bullet():
    if game_over:  # Don't shoot if game is over
        return
    angle_rad = math.radians(player_angle)  # Convert angle to radians

    # Calculate gun position in world space
    gun_local_x = 0  # Gun centered horizontally on player
    gun_local_y = 60  # Gun extends forward from player
    gun_local_z = 80  # Gun height above player base
    gun_length = 60   # Distance to gun tip

    # Transform gun position to world coordinates
    gun_world_x = player_pos[0] + gun_local_x * math.cos(angle_rad) - gun_local_y * math.sin(angle_rad)
    gun_world_y = player_pos[1] + gun_local_x * math.sin(angle_rad) + gun_local_y * math.cos(angle_rad)
    gun_world_z = player_pos[2] + 160 + gun_local_z  # Add player height offset

    # Calculate bullet direction vector
    dir_x = -math.sin(angle_rad)  # X component of direction
    dir_y = math.cos(angle_rad)   # Y component of direction

    # Set bullet spawn position at gun tip
    bx = gun_world_x + dir_x * gun_length
    by = gun_world_y + dir_x * gun_length
    bz = gun_world_z

    # Add new bullet to game with position and velocity
    bullets.append([[bx, by, bz], [dir_x * 20, dir_y * 20, 0]])


"""
Function: keyboardListener
Purpose: Handles keyboard input for player movement and game controls
Parameters:
    key: ASCII value of pressed key
    x, y: Mouse position when key was pressed (unused)
Controls:
    - W: Move forward
    - S: Move backward
    - A: Rotate left
    - D: Rotate right
    - C: Toggle cheat mode
    - V: Toggle enhanced vision
    - R: Restart game
"""
def keyboardListener(key, x, y):
    global player_angle, cheat_mode, cheat_vision, game_over
    if game_over and key != b'r':  # Only allow restart when game over
        return

    # Handle movement keys with proper trigonometry
    if key == b'w':  # Forward movement
        player_pos[1] += 10 * math.cos(math.radians(player_angle))
        player_pos[0] -= 10 * math.sin(math.radians(player_angle))
    if key == b's':  # Backward movement
        player_pos[1] -= 10 * math.cos(math.radians(player_angle))
        player_pos[0] += 10 * math.sin(math.radians(player_angle))
    if key == b'a': player_angle += 5  # Rotate left
    if key == b'd': player_angle -= 5  # Rotate right
    if key == b'c': cheat_mode = not cheat_mode  # Toggle auto-aim
    if key == b'v': cheat_vision = not cheat_vision  # Toggle enhanced vision
    if key == b'r': restart_game()  # Restart game


"""
Function: specialKeyListener
Purpose: Handles special key input for camera control
Parameters:
    key: Special key code (arrow keys)
    x, y: Mouse coordinates when key was pressed (unused)
Controls:
    - LEFT/RIGHT: Rotate camera angle
    - UP/DOWN: Zoom camera in/out
"""
def specialKeyListener(key, x, y):
    global camera_angle, camera_radius  # Access global camera variables
    if key == GLUT_KEY_LEFT: camera_angle -= 5  # Rotate camera left
    if key == GLUT_KEY_RIGHT: camera_angle += 5  # Rotate camera right
    if key == GLUT_KEY_UP: camera_radius = max(camera_radius - 50, camera_min_radius)  # Zoom in
    if key == GLUT_KEY_DOWN: camera_radius = min(camera_radius + 50, camera_max_radius)  # Zoom out

"""
Function: mouseListener
Purpose: Handles mouse input for shooting and camera mode switching
Parameters:
    button: Mouse button identifier
    state: Button state (pressed/released)
    x, y: Mouse coordinates
Actions:
    - Left click: Fire bullet
    - Right click: Toggle camera mode
"""
def mouseListener(button, state, x, y):
    global camera_mode  # Access global camera mode variable
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:  # Left click
        fire_bullet()  # Shoot bullet
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:  # Right click
        camera_mode = 1 - camera_mode  # Toggle between first/third person

"""
Function: setupCamera
Purpose: Configures the camera view based on current mode
Features:
    - Sets up perspective projection
    - Handles both third-person and first-person views
    - Calculates camera position and orientation
"""
def setupCamera():
    # Set up projection matrix
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset projection matrix
    gluPerspective(FOV_Y, WINDOW_WIDTH / WINDOW_HEIGHT, 1, 3000)  # Set perspective parameters
    
    # Switch to modelview matrix for camera positioning
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 0:  # Third-person view
        # Calculate camera position using spherical coordinates
        cam_x = camera_radius * math.sin(math.radians(camera_angle))
        cam_y = camera_radius * math.cos(math.radians(camera_angle))
        cam_z = camera_height
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)
    else:  # First-person view
        px, py, pz = player_pos  # Get player position
        angle_rad = math.radians(player_angle)  # Convert player angle to radians
        
        # Set camera position at player's head
        cam_x = px
        cam_y = py
        cam_z = pz + 160 + 120  # Add offsets for body height and head position
        
        # Calculate look-at point in front of player
        look_x = cam_x + math.cos(angle_rad)
        look_y = cam_y + math.sin(angle_rad)
        look_z = cam_z
        
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)


"""
Function: update_enemy_pulse
Purpose: Controls the pulsing animation of enemy models
Features:
    - Updates global pulse scale factor
    - Creates sinusoidal scaling effect
    - Controls timing of animation
"""
def update_enemy_pulse():
    global enemy_pulse_scale, pulse_time
    pulse_time += 0.03  # Increment time for animation speed
    enemy_pulse_scale = 1 + 0.1 * math.sin(pulse_time)  # Calculate scale factor

"""
Function: update_game
Purpose: Main game logic update function
Features:
    - Handles cheat mode auto-targeting
    - Updates bullet positions and collisions
    - Manages enemy movement and player collision
    - Updates game state (score, lives, game over)
"""
def update_game():
    global bullets, enemies, lives, missed, score, game_over

    if game_over:  # Skip updates if game is over
        return

    update_enemy_pulse()  # Update enemy animation

    # Cheat mode auto-targeting logic
    if cheat_mode:
        player_angle = (player_angle + 2) % 360  # Rotate player
        for ex, ey, _ in enemies:
            px, py, _ = player_pos
            # Calculate angle to enemy
            angle_to_enemy = math.degrees(math.atan2(ey - py, ex - px))
            if abs((player_angle - angle_to_enemy) % 360) < 10:
                fire_bullet()  # Auto-fire when aimed at enemy
                break

    # Bullet physics and collision detection
    new_bullets = []
    for bullet in bullets:
        pos, vel = bullet
        # Update bullet position
        pos[0] += vel[0]
        pos[1] += vel[1]

        hit = False
        for i, enemy in enumerate(enemies):
            # Vector from bullet to enemy (XY plane)
            to_enemy_x = enemy[0] - pos[0]
            to_enemy_y = enemy[1] - pos[1]
            to_enemy_len = math.hypot(to_enemy_x, to_enemy_y)
            
            # Check for direct hits
            if to_enemy_len < 30:
                enemies[i] = [random.randint(-900, 900), random.randint(-900, 900), 0]
                score += 1
                hit = True
                break

            # Angle-based "aim assist" hit detection
            bullet_dir_x, bullet_dir_y = vel[0], vel[1]
            bullet_dir_len = math.hypot(bullet_dir_x, bullet_dir_y)
            if bullet_dir_len > 0 and to_enemy_len > 0:
                # Normalize vectors
                bullet_dir_x /= bullet_dir_len
                bullet_dir_y /= bullet_dir_len
                to_enemy_x /= to_enemy_len
                to_enemy_y /= to_enemy_len
                # Calculate dot product for angle check
                dot = bullet_dir_x * to_enemy_x + bullet_dir_y * to_enemy_y
                if dot > math.cos(math.radians(20)) and to_enemy_len < 1000:
                    enemies[i] = [random.randint(-900, 900), random.randint(-900, 900), 0]
                    score += 1
                    hit = True
                    break

        # Keep bullet if still in bounds and hasn't hit anything
        if not hit and abs(pos[0]) < 1500 and abs(pos[1]) < 1500:
            new_bullets.append(bullet)
        else:
            if not hit:
                missed += 1  # Count missed shots
    
    bullets = new_bullets  # Update active bullets list

    # Enemy movement and player collision
    for i, (ex, ey, ez) in enumerate(enemies):
        px, py, _ = player_pos
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)
        if dist > 5:  # Move enemies toward player
            enemies[i][0] += dx / dist * 0.5
            enemies[i][1] += dy / dist * 0.5
        if dist < 50:  # Check for collision with player
            lives -= 1
            enemies[i] = [random.randint(-900, 900), random.randint(-900, 900), 0]

    # Check game over conditions
    if lives <= 0 or missed >= 10:
        game_over = True


"""
Function: restart_game
Purpose: Resets all game variables to their initial states
Features:
    - Resets player position and angle
    - Clears bullets and resets enemies
    - Resets score, lives, and game state
    - Resets animation timers
"""
def restart_game():
    global player_pos, player_angle, camera_mode, lives, missed, score, bullets, game_over, pulse_time
    player_pos[:] = [0, 400, 0]  # Reset player position
    player_angle = 180           # Reset player orientation
    camera_mode = 0             # Reset to third-person view
    bullets.clear()             # Remove all bullets
    reset_enemies()             # Reset enemy positions
    lives, missed, score = 5, 0, 0  # Reset game stats
    pulse_time = 0              # Reset animation timer
    game_over = False           # Reset game state

"""
Function: idle
Purpose: GLUT idle callback for continuous updates
Features:
    - Updates game state
    - Triggers screen refresh
"""
def idle():
    update_game()               # Update game logic
    glutPostRedisplay()         # Request screen redraw

"""
Function: draw_grid
Purpose: Renders the game world environment
Features:
    - Draws checkered floor pattern
    - Creates colored boundary walls
    - Defines play area limits
"""
def draw_grid():
    # Draw checkered floor tiles
    tile_size = 100            # Size of each floor tile
    for i in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
        for j in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
            glBegin(GL_QUADS)
            # Alternate tile colors for checkerboard pattern
            if (i // tile_size + j // tile_size) % 2 == 0:
                glColor3f(1, 1, 1)  # White tiles
            else:
                glColor3f(0.8, 0.7, 0.9)  # Light purple tiles
            # Draw tile vertices
            glVertex3f(i, j, 0)
            glVertex3f(i + tile_size, j, 0)
            glVertex3f(i + tile_size, j + tile_size, 0)
            glVertex3f(i, j + tile_size, 0)
            glEnd()

    # Define wall properties
    wall_height = 200          # Height of boundary walls
    wall_color = {
        'left': (0.2, 0.4, 1),    # Blue wall
        'right': (0.3, 1, 0.3),   # Green wall
        'front': (1, 1, 1),       # White wall
        'back': (1, 0.8, 0.9),    # Pink wall
    }

    # Draw all four boundary walls
    # ... (wall drawing code continues as in original)

"""
Function: showScreen
Purpose: Main rendering function for the game
Features:
    - Clears screen buffers
    - Sets up camera view
    - Renders all game elements
    - Displays game UI and text
"""
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear screen and depth buffer
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)  # Set display viewport
    setupCamera()  # Configure camera position and view
    draw_grid()  # Draw game environment

    # Render all game objects
    for enemy in enemies:  # Draw all enemies
        draw_enemy(enemy)
    draw_player()  # Draw player character

    # Draw all active bullets
    for bullet in bullets:
        draw_bullet(bullet[0])  # Pass bullet position to draw function

    # Draw UI elements
    draw_text(10, 770, f"Lives: {lives}  Score: {score}  Missed: {missed}")  # Game stats
    if game_over:
        draw_text(400, 400, "GAME OVER. Press 'R' to restart.")  # Game over message

    glutSwapBuffers()  # Swap display buffers

"""
Function: main
Purpose: Program entry point and OpenGL initialization
Features:
    - Initializes GLUT window and display mode
    - Sets up callback functions
    - Enables depth testing
    - Starts the main game loop
"""
def main():
    glutInit()  # Initialize GLUT
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GL_DEPTH_BUFFER_BIT)  # Set display mode
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # Set window dimensions
    glutCreateWindow(b"Bullet Frenzy 3D")  # Create window with title
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for 3D rendering
    
    # Register callback functions
    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard handler
    glutSpecialFunc(specialKeyListener)  # Register special key handler
    glutMouseFunc(mouseListener)  # Register mouse handler
    glutIdleFunc(idle)  # Register idle function
    
    glutMainLoop()  # Start the main event loop

# Program entry point
if __name__ == "__main__":
    main()

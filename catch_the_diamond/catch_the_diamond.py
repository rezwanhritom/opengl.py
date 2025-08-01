# -*- coding: utf-8 -*-
# This is a standard encoding declaration for Python files, ensuring compatibility
# with characters beyond basic ASCII, although not strictly necessary here.

# --- Imports ---
import time  # Needed to calculate delta time for smooth animation.
import random # Needed for random.randint() (diamond horizontal position) and random.choice() (diamond color).

# Import necessary modules from the PyOpenGL library
from OpenGL.GL import * # Core OpenGL functions (drawing, setting color, clearing screen, etc.)
from OpenGL.GLUT import * # OpenGL Utility Toolkit functions (window creation, event handling like keyboard/mouse, main loop)
from OpenGL.GLU import * # OpenGL Utility Library functions (like gluOrtho2D for setting up 2D projection)

# --- Constants ---
# Using constants makes the code easier to read and modify.
# Caps lock is used for constant variables.
WINDOW_WIDTH = 800      # Defines the width of the game window in pixels.
WINDOW_HEIGHT = 700     # Defines the height of the game window in pixels.
POINT_SIZE = 2          # Sets the size of the points drawn by GL_POINTS. Adjust for visibility.

# Game States are represented by integers for clarity in managing game flow.
STATE_PLAYING = 1       # Constant representing the active gameplay state.
STATE_PAUSED = 2        # Constant representing the paused state.
STATE_GAMEOVER = 3      # Constant representing the game over state.

# Colors are defined as tuples of (Red, Green, Blue) values between 0.0 and 1.0.
COLOR_WHITE = (1.0, 1.0, 1.0)
COLOR_RED = (1.0, 0.0, 0.0)     # Used for catcher in game over state, exit button.
COLOR_TEAL = (0.0, 0.8, 0.8)    # Used for restart button.
COLOR_AMBER = (1.0, 0.75, 0.0)  # Used for pause/play button.
COLOR_BLACK = (0.0, 0.0, 0.0)
BRIGHT_COLORS = [               # A list of predefined bright colors for the diamonds.
    (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
    (1.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0),
    (1.0, 0.5, 0.0), (0.5, 0.0, 1.0), (0.0, 1.0, 0.5)
]

# --- Global Variables ---
# Global variables store the game's state that needs to be accessed and modified
# by multiple functions (like callbacks and update logic).
# Caps loc is not used for variables, as they are not constants.

# Game State Management
game_state = STATE_PLAYING  # Tracks the current state (playing, paused, game over). Initialized to playing.
score = 0                   # Stores the player's current score.
last_frame_time = 0.0       # Stores the timestamp of the last frame, used for delta time calculation.

# Catcher Properties
catcher_x = WINDOW_WIDTH // 2 # Initial horizontal position (center of the window). `//` ensures integer division.
catcher_height = 20           # The vertical height of the catcher shape.
desired_bottom_margin = 10    # Space between the catcher's bottom edge and the window bottom.
# Calculates the catcher's center Y-coordinate so its bottom edge is at the desired margin.
catcher_y = desired_bottom_margin + catcher_height / 2.0
catcher_width = 100           # The width of the *top* edge of the trapezium catcher.
catcher_bottom_ratio = 0.7    # Factor determining the bottom width relative to the top width.
catcher_color = COLOR_WHITE   # Initial color of the catcher. Changes to red on game over.
catcher_speed = 400.0         # Speed at which the catcher moves horizontally (pixels per second - used conceptually here).

# Diamond Properties
diamond_x = 0                 # Current horizontal position of the diamond (initialized but set in spawn_diamond).
diamond_y = 0                 # Current vertical position of the diamond (initialized but set in spawn_diamond).
diamond_size = 25             # Approximate size (used for drawing and collision box).
diamond_color = random.choice(BRIGHT_COLORS) # Initial color chosen randomly from the list.
diamond_velocity_y = 120.0    # Initial downward speed (pixels per second).
diamond_acceleration = 6.0    # Rate at which the diamond's speed increases (pixels per second squared).

# Button Properties (using dictionaries to store clickable area rectangle properties)
button_size_w = 50            # Width of the clickable button area.
button_size_h = 40            # Height of the clickable button area.
button_margin = 20            # Spacing from window edges and potentially between buttons.
button_y_pos = WINDOW_HEIGHT - button_size_h - 15 # Y-coordinate of the bottom edge of the buttons.

# Dictionary defining the clickable rectangle for the restart button (x, y, width, height).
restart_button_rect = {'x': button_margin, 'y': button_y_pos, 'w': button_size_w, 'h': button_size_h}
# Dictionary for the pause/play button, centered horizontally.
pause_button_rect = {'x': WINDOW_WIDTH // 2 - button_size_w // 2, 'y': button_y_pos, 'w': button_size_w, 'h': button_size_h}
# Dictionary for the exit button, positioned near the right edge.
exit_button_rect = {'x': WINDOW_WIDTH - button_size_w - button_margin, 'y': button_y_pos, 'w': button_size_w, 'h': button_size_h}


# --- Midpoint Line Algorithm Implementation ---
# This section implements the core drawing requirement of the assignment.

def draw_point(x, y):
    """Draws a single point at integer coordinates (x, y)."""
    glBegin(GL_POINTS) # Specifies that we are drawing individual points. This is the ONLY primitive allowed by the assignment.
    # glVertex2i specifies a 2D vertex with integer coordinates.
    # round() ensures that calculated coordinates (which might be float) are rounded
    # to the nearest integer pixel coordinate before drawing. int() converts the result to integer type.
    glVertex2i(int(round(x)), int(round(y)))
    glEnd() # Marks the end of defining vertices for the current primitive (GL_POINTS).

def find_zone(x1, y1, x2, y2):
    """Determines the zone (0-7 octants) of a line segment."""
    dx = x2 - x1 # Change in x.
    dy = y2 - y1 # Change in y.
    # Handles the edge case where the start and end points are the same.
    if dx == 0 and dy == 0: return 0

    # Compares the absolute changes in x and y to determine if the slope's magnitude is < 1 or >= 1.
    if abs(dx) >= abs(dy): # Slope magnitude <= 1 (Zones 0, 3, 4, 7)
        if dx >= 0 and dy >= 0: return 0 # Positive dx, Positive dy -> Zone 0
        elif dx < 0 and dy >= 0: return 3 # Negative dx, Positive dy -> Zone 3
        elif dx < 0 and dy < 0: return 4 # Negative dx, Negative dy -> Zone 4
        else: return 7                   # Positive dx, Negative dy -> Zone 7
    else: # Slope magnitude > 1 (Zones 1, 2, 5, 6)
        if dx >= 0 and dy >= 0: return 1 # Positive dx, Positive dy -> Zone 1
        elif dx < 0 and dy >= 0: return 2 # Negative dx, Positive dy -> Zone 2
        elif dx < 0 and dy < 0: return 5 # Negative dx, Negative dy -> Zone 5
        else: return 6                   # Positive dx, Negative dy -> Zone 6

def convert_to_zone0(x, y, zone):
    """Converts a point (x, y) from a given zone to equivalent Zone 0 coordinates."""
    # This function applies transformations (swapping coordinates, changing signs)
    # based on the original zone, so the Midpoint algorithm for Zone 0 can be used.
    if zone == 0: return x, y
    elif zone == 1: return y, x      # Swap
    elif zone == 2: return -y, x     # Swap, Negate new X
    elif zone == 3: return -x, y     # Negate X
    elif zone == 4: return -x, -y    # Negate X, Y
    elif zone == 5: return -y, -x    # Swap, Negate new X, Y
    elif zone == 6: return y, -x     # Swap, Negate new Y
    elif zone == 7: return x, -y     # Negate Y
    else:
        print(f"Error: Invalid zone {zone} in convert_to_zone0")
        return x, y # Should not happen

def convert_from_zone0(x_z0, y_z0, zone):
    """Converts a point (x_z0, y_z0) from Zone 0 back to its original zone."""
    # This applies the inverse transformations of convert_to_zone0.
    # Using the corrected conversions from above:
    if zone == 0: return x_z0, y_z0
    elif zone == 1: return y_z0, x_z0     # Swap back
    elif zone == 2: return y_z0, -x_z0    # Swap back, Negate new Y (original x)
    elif zone == 3: return -x_z0, y_z0    # Negate x back
    elif zone == 4: return -x_z0, -y_z0   # Negate x, y back
    elif zone == 5: return -y_z0, -x_z0   # Swap back, Negate both
    elif zone == 6: return -y_z0, x_z0    # Swap back, Negate new X (original y)
    elif zone == 7: return x_z0, -y_z0    # Negate y back
    else:
        print(f"Error: Invalid zone {zone} in convert_from_zone0")
        return x_z0, y_z0

def midpoint_line_zone0(x1, y1, x2, y2, zone):
    """Draws a line using Midpoint Algorithm assuming it's been converted TO Zone 0."""
    # This implements the core Bresenham's Midpoint algorithm for lines with slope 0 <= m <= 1.
    dx = x2 - x1       # Change in x (in Zone 0 coordinates).
    dy = y2 - y1       # Change in y (in Zone 0 coordinates).
    d = 2 * dy - dx    # Initial decision parameter 'd'.
    incE = 2 * dy      # Increment if 'East' pixel is chosen (d doesn't change enough).
    incNE = 2 * (dy - dx) # Increment if 'North-East' pixel is chosen (d changes significantly).

    x = x1             # Start at the first point's Zone 0 coordinates.
    y = y1

    # Draw the first point after converting it back to its original zone.
    original_x, original_y = convert_from_zone0(x, y, zone)
    draw_point(original_x, original_y)

    # Loop from the starting x to the ending x (Zone 0 ensures x increases).
    while x < x2:
        # Check the decision parameter to decide the next pixel.
        if d > 0:        # Midpoint is above the line -> Choose NE pixel.
            d += incNE   # Update decision parameter for NE move.
            y += 1       # Increment y.
        else:            # Midpoint is below or on the line -> Choose E pixel.
            d += incE    # Update decision parameter for E move.
        x += 1           # Always increment x in Zone 0.

        # Convert the calculated Zone 0 point (x, y) back to its original zone before drawing.
        original_x, original_y = convert_from_zone0(x, y, zone)
        draw_point(original_x, original_y) # Draw the actual pixel on screen.

def draw_line_midpoint(x1, y1, x2, y2):
    """Draws a line between any (x1, y1) and (x2, y2) using the Midpoint Algorithm."""
    # Rounds inputs to avoid potential floating point inaccuracies in zone finding/conversion.
    x1, y1, x2, y2 = map(round, [x1, y1, x2, y2])

    # Handle perfectly vertical lines: Midpoint algorithm relies on dx != 0 for zone 0.
    if x1 == x2:
        y_start, y_end = min(y1, y2), max(y1, y2) # Ensure drawing from min y to max y.
        for y in range(y_start, y_end + 1): # Loop through y values.
            draw_point(x1, y)              # Draw each point vertically.
        return # Exit the function early.
    # Handle perfectly horizontal lines: Can be drawn simply.
    if y1 == y2:
        x_start, x_end = min(x1, x2), max(x1, x2) # Ensure drawing from min x to max x.
        for x in range(x_start, x_end + 1): # Loop through x values.
            draw_point(x, y1)              # Draw each point horizontally.
        return # Exit the function early.

    # 1. Determine the zone the line lies in.
    zone = find_zone(x1, y1, x2, y2)

    # 2. Convert the endpoints to their equivalent coordinates in Zone 0.
    x1_z0, y1_z0 = convert_to_zone0(x1, y1, zone)
    x2_z0, y2_z0 = convert_to_zone0(x2, y2, zone)

    # 3. The Zone 0 algorithm assumes drawing from left (smaller x) to right (larger x).
    #    If the converted points are not in this order, swap them.
    if x1_z0 > x2_z0:
        x1_z0, x2_z0 = x2_z0, x1_z0 # Swap x coordinates.
        y1_z0, y2_z0 = y2_z0, y1_z0 # Swap corresponding y coordinates.

    # 4. Call the specialized Zone 0 drawing function with the converted coordinates
    #    and pass the original zone so points can be converted back before plotting.
    midpoint_line_zone0(x1_z0, y1_z0, x2_z0, y2_z0, zone)

# --- Drawing Functions (using Midpoint Line) ---
# These functions define how to draw game objects using the `draw_line_midpoint` function.

def draw_catcher(cx, cy, top_width, height, bottom_ratio, color):
    """Draws the catcher as an upside-down trapezium using midpoint lines."""
    # Set the current drawing color for OpenGL. Affects subsequent draw_point calls.
    glColor3f(color[0], color[1], color[2]) # Takes Red, Green, Blue floats (0.0-1.0).

    # Calculate half dimensions for easier coordinate calculation around the center (cx, cy).
    half_h = height / 2.0
    half_top_w = top_width / 2.0
    bottom_width = top_width * bottom_ratio # Calculate the bottom width based on the ratio.
    half_bottom_w = bottom_width / 2.0

    # Define the 4 corner points relative to the center (cx, cy).
    p1 = (cx - half_top_w, cy + half_h)     # Top Left vertex.
    p2 = (cx + half_top_w, cy + half_h)     # Top Right vertex.
    p3 = (cx + half_bottom_w, cy - half_h) # Bottom Right vertex.
    p4 = (cx - half_bottom_w, cy - half_h) # Bottom Left vertex.

    # Draw the four line segments connecting the vertices using the midpoint algorithm.
    draw_line_midpoint(p1[0], p1[1], p2[0], p2[1]) # Top edge.
    draw_line_midpoint(p2[0], p2[1], p3[0], p3[1]) # Right slanted edge.
    draw_line_midpoint(p3[0], p3[1], p4[0], p4[1]) # Bottom edge.
    draw_line_midpoint(p4[0], p4[1], p1[0], p1[1]) # Left slanted edge.

def draw_diamond(cx, cy, size, color):
    """Draws a diamond shape using midpoint lines."""
    glColor3f(color[0], color[1], color[2]) # Set the drawing color for the diamond.
    half_s = size // 2 # Calculate half size for coordinate calculation.

    # Define the 4 vertices of the diamond relative to its center (cx, cy).
    top = (cx, cy + half_s)      # Top vertex.
    bottom = (cx, cy - half_s)   # Bottom vertex.
    left = (cx - half_s, cy)     # Left vertex.
    right = (cx + half_s, cy)    # Right vertex.

    # Draw the 4 line segments connecting the vertices.
    draw_line_midpoint(top[0], top[1], right[0], right[1])
    draw_line_midpoint(right[0], right[1], bottom[0], bottom[1])
    draw_line_midpoint(bottom[0], bottom[1], left[0], left[1])
    draw_line_midpoint(left[0], left[1], top[0], top[1])

def draw_buttons():
    """Draws the three control buttons with their icons using midpoint lines."""
    # --- Restart Button (Left Arrow) ---
    glColor3f(COLOR_TEAL[0], COLOR_TEAL[1], COLOR_TEAL[2]) # Set color for restart button icon.
    # Get the button's bounding box coordinates and dimensions.
    bx, by, bw, bh = restart_button_rect.values()
    # Calculate coordinates for the arrow lines, scaled to fit within the button's bounds (bw, bh).
    arrow_tip_x = bx + bw * 0.3
    arrow_mid_y = by + bh * 0.5
    arrow_base_x = bx + bw * 0.7
    arrow_wing_y1 = by + bh * 0.25
    arrow_wing_y2 = by + bh * 0.75
    # Draw the two lines forming the arrow shape.
    draw_line_midpoint(arrow_base_x, arrow_wing_y1, arrow_tip_x, arrow_mid_y)
    draw_line_midpoint(arrow_tip_x, arrow_mid_y, arrow_base_x, arrow_wing_y2)

    # --- Pause/Play Button (Triangle/Two Bars) ---
    glColor3f(COLOR_AMBER[0], COLOR_AMBER[1], COLOR_AMBER[2]) # Set color for pause/play icon.
    bx, by, bw, bh = pause_button_rect.values() # Get button bounds.
    # Check the game state to determine which icon to draw.
    if game_state == STATE_PAUSED:
        # Draw Play icon (Triangle pointing right), scaled to fit button bounds.
        play_tip_x = bx + bw * 0.75
        play_mid_y = by + bh * 0.5
        play_base_x = bx + bw * 0.25
        play_base_y1 = by + bh * 0.2
        play_base_y2 = by + bh * 0.8
        draw_line_midpoint(play_base_x, play_base_y1, play_tip_x, play_mid_y)
        draw_line_midpoint(play_tip_x, play_mid_y, play_base_x, play_base_y2)
        draw_line_midpoint(play_base_x, play_base_y2, play_base_x, play_base_y1)
    else: # Game state is PLAYING or GAMEOVER (show pause icon)
        # Draw Pause icon (Two vertical bars), scaled to fit button bounds.
        bar_width = bw * 0.2
        gap = bw * 0.2
        bar_height_factor = 0.6 # Make bars shorter than button height.
        bar_y_start = by + bh * (1 - bar_height_factor) / 2
        bar_y_end = by + bh * (1 + bar_height_factor) / 2
        # Calculate horizontal positions for the two bars.
        x1 = bx + (bw - 2 * bar_width - gap) / 2 # Start of first bar's conceptual area.
        x2 = x1 + bar_width + gap             # Start of second bar's conceptual area.
        # Draw the center line of each bar. (Could draw rectangles for thicker bars).
        draw_line_midpoint(x1 + bar_width*0.5, bar_y_start, x1 + bar_width*0.5, bar_y_end) # Left bar center.
        draw_line_midpoint(x2 + bar_width*0.5, bar_y_start, x2 + bar_width*0.5, bar_y_end) # Right bar center.

    # --- Exit Button (Cross 'X') ---
    glColor3f(COLOR_RED[0], COLOR_RED[1], COLOR_RED[2]) # Set color for exit icon.
    bx, by, bw, bh = exit_button_rect.values() # Get button bounds.
    # Calculate margins to draw the cross within the button bounds.
    margin_x = bw * 0.25
    margin_y = bh * 0.25
    # Draw the two diagonal lines forming the cross shape.
    draw_line_midpoint(bx + margin_x, by + margin_y, bx + bw - margin_x, by + bh - margin_y) # Top-left to bottom-right.
    draw_line_midpoint(bx + bw - margin_x, by + margin_y, bx + margin_x, by + bh - margin_y) # Top-right to bottom-left.

# --- Game Logic Functions ---
# These functions handle the rules and state changes of the game.

def reset_game():
    """Resets the game state, score, speed, catcher color, and spawns a new diamond."""
    # `global` keyword is needed to modify variables defined outside this function's scope.
    global score, game_state, catcher_color, diamond_velocity_y, last_frame_time
    print("Starting Over") # Console feedback.
    score = 0                  # Reset score to zero.
    game_state = STATE_PLAYING # Set game state back to playing.
    catcher_color = COLOR_WHITE# Restore catcher color.
    diamond_velocity_y = 120.0 # Reset diamond's initial falling speed.
    spawn_diamond()            # Create a new diamond to start falling.
    last_frame_time = time.time() # Reset the timer for delta time calculation.

def spawn_diamond():
    """Places a new diamond at a random horizontal position near the top."""
    global diamond_x, diamond_y, diamond_color # Allow modification of these globals.
    # Set horizontal position randomly within window bounds, avoiding edges.
    diamond_x = random.randint(diamond_size // 2, WINDOW_WIDTH - diamond_size // 2)
    # Set vertical position near the top edge.
    top_margin = 30
    diamond_y = WINDOW_HEIGHT - top_margin - diamond_size // 2
    # Choose a random color for the new diamond.
    diamond_color = random.choice(BRIGHT_COLORS)

def check_collision():
    """Checks for collision between the diamond and the catcher using AABB."""
    # Define the Axis-Aligned Bounding Box (AABB) for the catcher.
    # The box uses the catcher's center, top width, and height for simplicity.
    # Collision might feel slightly off at the slanted edges, but AABB is simple.
    catcher_box = {
        'x': catcher_x - catcher_width // 2, # Left edge.
        'y': catcher_y - catcher_height // 2, # Bottom edge.
        'width': catcher_width,              # Full top width.
        'height': catcher_height             # Full height.
    }
    # Define the AABB for the diamond.
    diamond_box = {
        'x': diamond_x - diamond_size // 2,  # Left edge.
        'y': diamond_y - diamond_size // 2,  # Bottom edge.
        'width': diamond_size,
        'height': diamond_size
    }

    # Perform the AABB collision check logic.
    # Returns True if the boxes overlap, False otherwise.
    collided = (catcher_box['x'] < diamond_box['x'] + diamond_box['width'] and
                catcher_box['x'] + catcher_box['width'] > diamond_box['x'] and
                catcher_box['y'] < diamond_box['y'] + diamond_box['height'] and
                catcher_box['y'] + catcher_box['height'] > diamond_box['y'])
    return collided

def update(value):
    """Updates game state (movement, collision, etc.) - called periodically by glutTimerFunc."""
    # Need global access to modify game state variables.
    global game_state, score, catcher_color, diamond_y, diamond_velocity_y, last_frame_time

    # --- Delta Time Calculation ---
    current_time = time.time() # Get the current system time.
    # Calculate time elapsed since the last call to update().
    delta_t = current_time - last_frame_time
    # Clamp delta_t: Prevents huge jumps in movement if the game pauses or lags significantly.
    # Limits the maximum time step considered to 0.1 seconds (100ms).
    delta_t = min(delta_t, 0.1)
    last_frame_time = current_time # Store current time for the next frame's calculation.

    # --- Game Logic Update (only if playing) ---
    if game_state == STATE_PLAYING:
        # --- Diamond Movement ---
        # Increase velocity based on constant acceleration and elapsed time (v = u + at).
        diamond_velocity_y += diamond_acceleration * delta_t
        # Update position based on new velocity and elapsed time (s = vt).
        diamond_y -= diamond_velocity_y * delta_t # Subtract because y decreases downwards.

        # --- Check for Catch or Miss ---
        # Check if the diamond is vertically close to the catcher AND if they collide horizontally/vertically.
        # `diamond_y < catcher_y + catcher_height * 0.8` checks if the diamond is roughly at catcher level or below.
        if diamond_y < catcher_y + catcher_height * 0.8 and check_collision():
            score += 1              # Increment score.
            print(f"Score: {score}") # Print score to console.
            # Optional: Increase difficulty further upon catch.
            # diamond_acceleration += 1.0
            spawn_diamond()         # Spawn a new diamond.
        # Check if diamond has hit the ground (y < its bottom edge touching 0).
        elif diamond_y < (0 + diamond_size // 2):
            print(f"Game Over! Final Score: {score}") # Game over message.
            game_state = STATE_GAMEOVER           # Change game state.
            catcher_color = COLOR_RED             # Change catcher color.
            # Effectively remove the diamond by placing it off-screen.
            diamond_y = WINDOW_HEIGHT * 2

    # --- Request Redraw ---
    # Tell GLUT that the display needs to be updated in the next cycle.
    # This will trigger a call to the 'display' function.
    glutPostRedisplay()

    # --- Reschedule Update ---
    # Ask GLUT to call this 'update' function again after 16 milliseconds.
    # value=0 is just a parameter that can be passed (not used here).
    # This creates the animation loop (aiming for ~60 frames per second).
    glutTimerFunc(16, update, 0)

# --- OpenGL Callbacks ---
# These functions are registered with GLUT and are called automatically
# in response to specific events (like drawing, resizing, input).

def display():
    """OpenGL display callback. This function does the actual drawing."""
    # Clear the screen (color buffer) and depth buffer (though depth isn't heavily used in 2D).
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # Reset the model-view matrix (transformations) for this frame.
    glLoadIdentity()

    # --- Draw all game elements ---
    draw_buttons() # Draw the static buttons first.
    # Only draw the diamond if the game is not over.
    if game_state != STATE_GAMEOVER:
         # Pass coordinates rounded to integers for drawing consistency.
         draw_diamond(int(round(diamond_x)), int(round(diamond_y)), diamond_size, diamond_color)
    # Draw the catcher, passing all necessary parameters.
    draw_catcher(int(round(catcher_x)), int(round(catcher_y)), catcher_width, catcher_height, catcher_bottom_ratio, catcher_color)

    # Swap the front (visible) and back (drawing) buffers. Required for smooth animation
    # when using double buffering (GLUT_DOUBLE).
    glutSwapBuffers()

def reshape(w, h):
    """OpenGL reshape callback. Called when the window is resized."""
    # Update global window dimensions if needed by other logic.
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = w
    WINDOW_HEIGHT = h
    # Tell OpenGL the area of the window it should render to (usually the whole window).
    glViewport(0, 0, w, h)
    # Switch to the Projection matrix stack to set up the camera/view.
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity() # Reset the projection matrix.
    # Set up a 2D orthographic projection. Maps world coordinates directly to screen coordinates.
    # (0, w) maps to the horizontal axis, (0, h) maps to the vertical axis. (0,0) is bottom-left.
    gluOrtho2D(0, w, 0, h)
    # Switch back to the ModelView matrix stack for drawing transformations.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity() # Reset the model-view matrix.

    # --- Recalculate button positions based on new window size ---
    # This ensures buttons stay correctly positioned (e.g., centered, near edges) after resize.
    global restart_button_rect, pause_button_rect, exit_button_rect, button_y_pos
    button_y_pos = WINDOW_HEIGHT - button_size_h - 15 # Recalculate Y.
    # Update X, Y coordinates in the button rectangle dictionaries.
    restart_button_rect['x'] = button_margin
    restart_button_rect['y'] = button_y_pos
    pause_button_rect['x'] = WINDOW_WIDTH // 2 - button_size_w // 2
    pause_button_rect['y'] = button_y_pos
    exit_button_rect['x'] = WINDOW_WIDTH - button_size_w - button_margin
    exit_button_rect['y'] = button_y_pos


def keyboard(key, x, y):
    """OpenGL keyboard callback for regular printable keys (e.g., 'a', '1', space)."""
    # `key` is the byte representation of the key pressed.
    # `x`, `y` are the mouse coordinates when the key was pressed.
    # This function is currently empty but could be used for other controls.
    pass

def specialKeys(key, x, y):
    """OpenGL keyboard callback for special keys (arrows, F-keys, Home, etc.)."""
    global catcher_x # Need to modify the catcher's global position.

    # Only allow catcher movement if the game is in the playing state.
    if game_state == STATE_PLAYING:
        # Simple movement: Move a fixed distance per key press.
        # For smoother, frame-rate independent movement, calculate based on delta_t in the update() loop.
        move_dist = 25 # Distance to move the catcher per arrow key press.

        # Check which special key was pressed.
        if key == GLUT_KEY_LEFT: # Left arrow key code.
            catcher_x -= move_dist # Move left.
            # Boundary check: Prevent catcher from moving off the left edge.
            # Check against half the top width as the position `catcher_x` is the center.
            if catcher_x < catcher_width / 2.0:
                catcher_x = catcher_width / 2.0
        elif key == GLUT_KEY_RIGHT: # Right arrow key code.
            catcher_x += move_dist # Move right.
            # Boundary check: Prevent catcher from moving off the right edge.
            if catcher_x > WINDOW_WIDTH - catcher_width / 2.0:
                catcher_x = WINDOW_WIDTH - catcher_width / 2.0
        # No need to call glutPostRedisplay() here, the update timer loop handles redraws.

def mouse(button, state, x, y):
    """OpenGL mouse callback. Called when a mouse button is pressed or released."""
    # `button` indicates which button (GLUT_LEFT_BUTTON, GLUT_MIDDLE_BUTTON, GLUT_RIGHT_BUTTON).
    # `state` indicates if pressed (GLUT_DOWN) or released (GLUT_UP).
    # `x`, `y` are the mouse coordinates (origin top-left in GLUT).
    global game_state, last_frame_time # Need access to modify game state and timer.

    # Process only left mouse button clicks when the button is pressed down.
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Convert GLUT's mouse y (origin top-left) to OpenGL's coordinate system y (origin bottom-left).
        gl_y = WINDOW_HEIGHT - y

        # --- Check which button was clicked ---
        # Check if the click coordinates (x, gl_y) fall within the bounding box of each button.

        # Check Restart Button
        br = restart_button_rect
        if br['x'] <= x <= br['x'] + br['w'] and br['y'] <= gl_y <= br['y'] + br['h']:
            reset_game() # Call the reset function if clicked.

        # Check Pause/Play Button
        bp = pause_button_rect
        if bp['x'] <= x <= bp['x'] + bp['w'] and bp['y'] <= gl_y <= bp['y'] + bp['h']:
            # Toggle between playing and paused states.
            if game_state == STATE_PLAYING:
                game_state = STATE_PAUSED
                print("Game Paused")
            elif game_state == STATE_PAUSED:
                game_state = STATE_PLAYING
                # IMPORTANT: Reset last_frame_time when unpausing to prevent a large
                # time jump (delta_t) causing the diamond to leap forward.
                last_frame_time = time.time()
                print("Game Resumed")

        # Check Exit Button
        be = exit_button_rect
        if be['x'] <= x <= be['x'] + be['w'] and be['y'] <= gl_y <= be['y'] + be['h']:
            print(f"Goodbye! Final Score: {score}") # Print final message.
            # Tell GLUT to exit the main event loop, effectively closing the application.
            # This is preferred over sys.exit() as it allows GLUT to clean up properly.
            glutLeaveMainLoop()
        # A redraw is implicitly requested by the update loop's glutPostRedisplay().

# --- Initialization ---
def init():
    """Initialize OpenGL context settings needed for the game."""
    # Set the background clear color (R, G, B, Alpha). Used by glClear(). Dark gray here.
    glClearColor(0.1, 0.1, 0.1, 1.0)
    # Set the size for points drawn using GL_POINTS primitive.
    glPointSize(POINT_SIZE)

# --- Main Execution Block ---
# This code runs only when the script is executed directly (not imported as a module).
if __name__ == "__main__":
    # --- GLUT Setup ---
    glutInit() # Initialize the GLUT library.
    # Set the initial display mode:
    # GLUT_DOUBLE: Use double buffering for smooth animation.
    # GLUT_RGB: Use RGB color model.
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    # Set the initial window size using the defined constants.
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    # Set the initial window position on the screen (e.g., 100 pixels from top-left).
    glutInitWindowPosition(100, 100)
    # Create the window with the specified title (title must be bytes).
    glutCreateWindow(b"Catch the Diamonds! - Midpoint Line v2")

    # --- OpenGL Initialization ---
    init() # Call the function to set up OpenGL states (clear color, point size).

    # --- Register Callback Functions ---
    # Tell GLUT which functions to call for different events.
    glutDisplayFunc(display)     # Called when the window needs to be redrawn.
    glutReshapeFunc(reshape)     # Called when the window is resized.
    glutKeyboardFunc(keyboard)   # Called for regular key presses.
    glutSpecialFunc(specialKeys) # Called for special key presses (arrows).
    glutMouseFunc(mouse)       # Called for mouse button events.
    # Use glutTimerFunc for the animation loop instead of glutIdleFunc for better control
    # and integration with delta time. Start the timer immediately (0ms delay).
    glutTimerFunc(0, update, 0)

    # --- Initial Game Setup ---
    spawn_diamond()            # Spawn the first diamond.
    last_frame_time = time.time() # Initialize the frame timer.

    # --- Start GLUT Main Loop ---
    # This function starts the GLUT event processing loop. It listens for events
    # (like input, timers, redraw requests) and calls the registered callback functions.
    # The program stays in this loop until glutLeaveMainLoop() is called or the window is closed.
    glutMainLoop()
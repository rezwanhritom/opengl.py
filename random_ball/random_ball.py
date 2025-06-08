from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

points = []          # List to store points: [x, y, dx, dy, color, is_blinking, blink_start]
point_speed = 0.001  # Base speed
current_speed = point_speed  # Track current speed for new points
is_frozen = False    # Freeze state
is_blinking = False  # Blink state

def generate_random_color():
    return [random.random() for _ in range(3)]  # Random RGB values

def generate_random_direction():
    angle = random.choice([45, 135, 225, 315])  # Random diagonal angles
    rad = math.radians(angle)
    return math.cos(rad) * current_speed, math.sin(rad) * current_speed  # Use current_speed instead of point_speed

def mouse(button, state, x, y):
    global points, is_blinking
    if state != GLUT_DOWN:
        return

    gl_x = (2.0 * x / glutGet(GLUT_WINDOW_WIDTH) - 1.0)
    gl_y = (1.0 - 2.0 * y / glutGet(GLUT_WINDOW_HEIGHT))

    if button == GLUT_RIGHT_BUTTON:
        dx, dy = generate_random_direction()
        color = generate_random_color()
        points.append([gl_x, gl_y, dx, dy, color, is_blinking, time.time()])
    
    elif button == GLUT_LEFT_BUTTON: 
        is_blinking = not is_blinking
        for point in points:
            point[5] = is_blinking 
            if is_blinking:
                point[6] = time.time()

def keyboard_special(key, x, y):
    global current_speed
    if is_frozen:
        return

    if key == GLUT_KEY_UP:
        current_speed *= 1.2
        for point in points:
            point[2] *= 1.2
            point[3] *= 1.2
    elif key == GLUT_KEY_DOWN:
        current_speed *= 0.8
        for point in points:
            point[2] *= 0.8
            point[3] *= 0.8

def keyboard(key, x, y):
    global is_frozen
    if key == b' ':
        is_frozen = not is_frozen

def update_points():
    if is_frozen:
        return
    current_time = time.time()
    for point in points:  # Update position for all points
        point[0] += point[2]
        point[1] += point[3]
        # Bounce from screen edges
        if abs(point[0]) > 1.0:
            point[2] *= -1  # Reverse x direction
            point[0] = max(min(point[0], 1.0), -1.0)  # Keep within bounds
        if abs(point[1]) > 1.0:
            point[3] *= -1  # Reverse y direction
            point[1] = max(min(point[1], 1.0), -1.0)  # Keep within bounds

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    glPointSize(5.0)  # Draw points
    glBegin(GL_POINTS)
    current_time = time.time()
    for point in points:  # Handle blinking with 1-second transition
        if point[5]:  # If point should blink
            blink_time = (current_time - point[6]) % 2.0  # 2-second cycle
            if blink_time < 1.0:  # Show point for 1 second
                glColor3f(*point[4])
                glVertex2f(point[0], point[1])
        else:  # If not blinking, always show
            glColor3f(*point[4])
            glVertex2f(point[0], point[1])
    glEnd()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(800, 800)
glutCreateWindow(b"Amazing Box")

glutDisplayFunc(display)
glutIdleFunc(lambda: (update_points(), glutPostRedisplay()))
glutMouseFunc(mouse)
glutKeyboardFunc(keyboard)
glutSpecialFunc(keyboard_special)
gluOrtho2D(-1, 1, -1, 1)

glutMainLoop()
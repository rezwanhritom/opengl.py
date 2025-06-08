from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

rain_drops = []
rain_angle = 0
bg_color = 0.0 
transition_speed = 0.02

# Initializes raindrops
for _ in range(100):
    rain_drops.append([
        random.uniform(-2, 2),  # x position
        random.uniform(0, 4),   # y position
        0.02                    # speed
    ])
    
def draw_house():
    # House base
    glBegin(GL_TRIANGLES)
    glColor3f(0.96, 0.87, 0.70)
    glVertex2f(-0.5, -0.5)
    glVertex2f(0.5, -0.5)
    glVertex2f(0.5, 0.5)
    glVertex2f(-0.5, -0.5)
    glVertex2f(-0.5, 0.5)
    glVertex2f(0.5, 0.5)
    glEnd()

    glBegin(GL_LINES)  # House border
    glColor3f(0.2, 0.2, 0.2)
    glVertex2f(-0.5, -0.5)
    glVertex2f(0.5, -0.5)
    glVertex2f(0.5, -0.5)
    glVertex2f(0.5, 0.5)
    glVertex2f(0.5, 0.5)
    glVertex2f(-0.5, 0.5)
    glVertex2f(-0.5, 0.5)
    glVertex2f(-0.5, -0.5)
    glEnd()

    # Roof
    glBegin(GL_TRIANGLES)
    glColor3f(0.4, 0.4, 0.4)
    glVertex2f(-0.6, 0.5)
    glVertex2f(0.6, 0.5)
    glVertex2f(0.0, 1.0)
    glEnd()

    glBegin(GL_LINES)  # Roof border
    glColor3f(0.2, 0.2, 0.2)
    glVertex2f(-0.6, 0.5)
    glVertex2f(0.6, 0.5)
    glVertex2f(0.6, 0.5)
    glVertex2f(0.0, 1.0)
    glVertex2f(0.0, 1.0)
    glVertex2f(-0.6, 0.5)
    glEnd()

    # Door
    glBegin(GL_TRIANGLES)
    glColor3f(0.4, 0.2, 0.0)
    glVertex2f(-0.1, -0.5)
    glVertex2f(0.1, -0.5)
    glVertex2f(0.1, -0.1)
    glVertex2f(-0.1, -0.5)
    glVertex2f(-0.1, -0.1)
    glVertex2f(0.1, -0.1)
    glEnd()

    glBegin(GL_LINES)  # Door border
    glColor3f(0.2, 0.1, 0.0)  
    glVertex2f(-0.1, -0.5)
    glVertex2f(0.1, -0.5)
    glVertex2f(0.1, -0.5)
    glVertex2f(0.1, -0.1)
    glVertex2f(0.1, -0.1)
    glVertex2f(-0.1, -0.1)
    glVertex2f(-0.1, -0.1)
    glVertex2f(-0.1, -0.5)
    glEnd()
    
    glPointSize(5.0)  # Door handle
    glBegin(GL_POINTS)
    glColor3f(0.8, 0.8, 0.0)
    glVertex2f(0.07, -0.3)
    glEnd()

    # Function to draw a window
    def draw_window(position):
        glBegin(GL_TRIANGLES)
        glColor3f(0.8, 0.9, 1.0)
        glVertex2f(position - 0.075, 0.0)
        glVertex2f(position + 0.075, 0.0)
        glVertex2f(position + 0.075, 0.2)
        glVertex2f(position - 0.075, 0.0)
        glVertex2f(position - 0.075, 0.2)
        glVertex2f(position + 0.075, 0.2)
        glEnd()

        glBegin(GL_LINES)
        glColor3f(0.2, 0.2, 0.2)  #Border of Windows
        glVertex2f(position - 0.075, 0.0)
        glVertex2f(position + 0.075, 0.0)
        glVertex2f(position + 0.075, 0.0)
        glVertex2f(position + 0.075, 0.2)
        glVertex2f(position + 0.075, 0.2)
        glVertex2f(position - 0.075, 0.2)
        glVertex2f(position - 0.075, 0.2)
        glVertex2f(position - 0.075, 0.0)
        glVertex2f(position, 0.0)  # Window's cross
        glVertex2f(position, 0.2)
        glVertex2f(position - 0.075, 0.1)
        glVertex2f(position + 0.075, 0.1)
        glEnd()

    draw_window(-0.325)  # Left window
    draw_window(0.325)   # Right window

def draw_rain():
    glBegin(GL_LINES)
    glColor3f(0.7, 0.7, 1.0)

    for drop in rain_drops:
        x, y = drop[0], drop[1]  # Get current raindrop position
        angle_rad = math.radians(rain_angle)  # Calculate rain angle in radians for diagonal fall
        glVertex2f(x, y)  # Starting point of raindrop
        glVertex2f(x + 0.1 * math.sin(angle_rad), y - 0.1)  # End point with angle offset - creates slanted rain effect
    glEnd()

def update_rain():
    for drop in rain_drops:
        angle_rad = math.radians(rain_angle)  # Convert angle to radians for calculation

        drop[1] -= drop[2]  # Move raindrop down by its speed
        drop[0] += drop[2] * math.sin(angle_rad)  # Move raindrop sideways based on angle
        
        if drop[1] < -2:
            drop[1] = 4
            drop[0] = random.uniform(-2, 2)

def keyboard(key, x, y):
    global rain_angle, bg_color
    
    if key == GLUT_KEY_LEFT:  # Gradually shifts rain to left
        rain_angle = max(rain_angle - 1, -45)
    elif key == GLUT_KEY_RIGHT:  # Gradually shifts rain to right
        rain_angle = min(rain_angle + 1, 45)
    elif key == b'd':  # Gradually changes background to day
        bg_color = min(bg_color + transition_speed, 1.0)
    elif key == b'n':  # Gradually changes background to night
        bg_color = max(bg_color - transition_speed, 0.0)
    glutPostRedisplay()

def display():
    glClearColor(bg_color, bg_color, bg_color, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    draw_house()
    draw_rain()
    update_rain()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Simple House with Rainfall")
gluOrtho2D(-2, 2, -2, 2)

glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutSpecialFunc(keyboard)
glutIdleFunc(display)
glutMainLoop()
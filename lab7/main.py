import math
import glfw
import numpy as np
from OpenGL.GL import *
from math import cos, sin
from PIL import Image

alpha = 45
beta = 45
size = 0.7
fill = True
position_y = 1.0
velocity_y = 0.0
acceleration_y = -9.8
time_step = 0.016
texture_id = 0
use_texture = False
light0_enabled = False
light1_enabled = False
torus_display_list = None

vertices = []
normals = []
tex_coords = []
indices = []


def load_texture(file):
    image = Image.open(file)
    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    image_data = np.array(list(image.getdata()), np.uint8)

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    return texture_id


def setup_texture_properties():
    glEnable(GL_TEXTURE_2D)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)


def initialize_lights():

    glLightfv(GL_LIGHT0, GL_POSITION, [-2.0, 0.0, 0.0, 0.0])
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [1.0, 0.0, 0.0])
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 45.0)
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 2.0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 0.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 0.0])
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.05)

    glLightfv(GL_LIGHT1, GL_POSITION, [2.0, 0.0, 0.0, 0.0])
    glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, [-1.0, 0.0, 0.0])
    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 45.0)
    glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 2.0)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.5, 0.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.5, 0.5, 0.5, 0.0])
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.1)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.05)


def setup_material():
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.7, 0.7, 0.7, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)


def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)

    if light0_enabled:
        glEnable(GL_LIGHT0)
    else:
        glDisable(GL_LIGHT0)

    if light1_enabled:
        glEnable(GL_LIGHT1)
    else:
        glDisable(GL_LIGHT1)


def main():
    global texture_id, torus_display_list
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "LAB 6", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    texture_id = load_texture("C:\\Users\\vvlad\\Downloads\\7.2.jpg")
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    initialize_lights()

    # Оптимизация - отсечение невидимых граней
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # Оптимизация - массив вершин
    create_torus(size, size / 3, 40, 25)

    # Оптимизация - дисплейный список
    torus_display_list = glGenLists(1)
    glNewList(torus_display_list, GL_COMPILE)
    draw_torus()
    glEndList()
    # Исключил локальные источники света

    while not glfw.window_should_close(window):
        display(window)

    glfw.destroy_window(window)
    glfw.terminate()


def projection():
    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)

    rotate_y = np.array([
        [cos(alpha_rad), 0, sin(alpha_rad), 0],
        [0, 1, 0, 0],
        [-sin(alpha_rad), 0, cos(alpha_rad), 0],
        [0, 0, 0, 1]
    ])

    rotate_x = np.array([
        [1, 0, 0, 0],
        [0, cos(beta_rad), -sin(beta_rad), 0],
        [0, sin(beta_rad), cos(beta_rad), 0],
        [0, 0, 0, 1]
    ])

    glMultMatrixf(rotate_x)
    glMultMatrixf(rotate_y)


def create_torus(R, r, N, n):
    global vertices, normals, tex_coords, indices
    for i in range(N):
        for j in range(n):
            theta = (2 * math.pi / N) * i
            phi = (2 * math.pi / n) * j
            theta_next = (2 * math.pi / N) * (i + 1)
            phi_next = (2 * math.pi / n) * (j + 1)

            x0 = (R + r * cos(phi)) * cos(theta)
            y0 = (R + r * cos(phi)) * sin(theta)
            z0 = r * sin(phi)

            x1 = (R + r * cos(phi)) * cos(theta_next)
            y1 = (R + r * cos(phi)) * sin(theta_next)
            z1 = r * sin(phi)

            x2 = (R + r * cos(phi_next)) * cos(theta_next)
            y2 = (R + r * cos(phi_next)) * sin(theta_next)
            z2 = r * sin(phi_next)

            x3 = (R + r * cos(phi_next)) * cos(theta)
            y3 = (R + r * cos(phi_next)) * sin(theta)
            z3 = r * sin(phi_next)

            s0 = i / N
            t0 = j / n
            s1 = (i + 1) / N
            t1 = (j + 1) / n

            vertices.extend([(x0, y0, z0), (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)])
            tex_coords.extend([(s0, t0), (s1, t0), (s1, t1), (s0, t1)])
            normals.extend([(x0, y0, z0), (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)])

            idx = len(vertices) - 4
            indices.extend([idx, idx + 1, idx + 2, idx, idx + 2, idx + 3])


def draw_torus():
    global vertices, normals, tex_coords, indices

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    glVertexPointer(3, GL_FLOAT, 0, np.array(vertices, dtype=np.float32))
    glNormalPointer(GL_FLOAT, 0, np.array(normals, dtype=np.float32))
    glTexCoordPointer(2, GL_FLOAT, 0, np.array(tex_coords, dtype=np.float32))

    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, np.array(indices, dtype=np.uint32))

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)


def display(window):
    global position_y, velocity_y, acceleration_y, use_texture, light0_enabled, light1_enabled, texture_id, torus_display_list

    velocity_y += acceleration_y * time_step
    position_y += velocity_y * time_step
    if position_y <= 0:
        position_y = -position_y
        velocity_y = -velocity_y

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if use_texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
    else:
        glDisable(GL_TEXTURE_2D)

    setup_lighting()
    setup_material()

    glTranslatef(0, position_y, 0)
    projection()

    # Применение дисплейного списка
    glCallList(torus_display_list)

    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    global alpha, beta, fill, use_texture, light0_enabled, light1_enabled
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_RIGHT:
            alpha += 0.6
        elif key == glfw.KEY_LEFT:
            alpha -= 0.6
        elif key == glfw.KEY_UP:
            beta -= 0.6
        elif key == glfw.KEY_DOWN:
            beta += 0.6
        elif key == glfw.KEY_F:
            fill = not fill
            if fill:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        elif key == glfw.KEY_T:
            use_texture = not use_texture
        elif key == glfw.KEY_L:
            light0_enabled = not light0_enabled
        elif key == glfw.KEY_P:
            light1_enabled = not light1_enabled


def scroll_callback(window, xoffset, yoffset):
    global size

    if xoffset > 0:
        size -= yoffset / 10
    else:
        size += yoffset / 10


if __name__ == "__main__":
    main()

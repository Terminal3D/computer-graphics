import glfw
from OpenGL.GL import *

angle = 180.0
posx = 0.0
posy = 0.0
size = 0.0


def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab1", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    while not glfw.window_should_close(window):
        display(window)

    glfw.destroy_window(window)
    glfw.terminate()


def display(window):
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glPushMatrix()
    glRotatef(angle, 0, 0, 1)
    glBegin(GL_QUAD_STRIP)
    glColor3f(0.929, 0.714, 0.031)
    glVertex2f(posx + size + 0.5, posy + size + 0.5)
    glColor3f(0.424, 0.031, 0.929)
    glVertex2f(posx - size + -0.5, posy + size + 0.5)
    glColor3f(0.424, 0.031, 0.929)
    glVertex2f(posx - size + -0.5, posy - size + -0.5)
    glColor3f(0.98, 0.625, 0.12)
    glVertex2f(posx + size + 0.5, posy - size + -0.5)
    glEnd()
    glPopMatrix()
    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    global posx, posy
    global angle
    if action == glfw.PRESS:
        if key == glfw.KEY_RIGHT:
            angle += -3
        if key == glfw.KEY_LEFT:
            angle += 3
        if key == glfw.KEY_UP:
            posy += 0.1
        if key == glfw.KEY_DOWN:
            posy += -0.1


def scroll_callback(window, xoffset, yoffset):
    global size
    if xoffset > 0:
        size -= yoffset / 10
    else:
        size += yoffset / 10


if __name__ == '__main__':
    main()

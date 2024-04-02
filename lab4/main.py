from OpenGL.GL import *
import glfw
from collections import deque
import numpy as np

size = 400  # Размер окна и рабочей области
pixels = [255] * (size * size * 3)  # Белый фон
points = []  # Список точек многоугольника


def setPixel(x, y, r, g, b):
    if 0 <= x < size and 0 <= y < size:
        position = (x + y * size) * 3
        pixels[position] = r
        pixels[position + 1] = g
        pixels[position + 2] = b


def bresenham2(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1
    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x2:
            setPixel(x, y, 255, 0, 0)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y2:
            setPixel(x, y, 255, 0, 0)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    setPixel(x, y, 255, 0, 0)


def mouse_button_callback(window, button, action, mods):
    global points, size
    if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_LEFT:
        x, y = glfw.get_cursor_pos(window)
        y = size - y
        points.append((int(x), int(y)))

        redraw_polygon()


def redraw_polygon():
    global pixels, points, size
    pixels = [255] * (size * size * 3)

    for i in range(1, len(points)):
        bresenham2(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1])

    if len(points) > 2:
        bresenham2(points[-1][0], points[-1][1], points[0][0], points[0][1])


def apply_post_filter(N):
    global pixels, size
    filtered_pixels = pixels.copy()

    radius = N // 2

    for y in range(size):
        for x in range(size):
            sum_r = sum_g = sum_b = 0
            count = 0

            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size:
                        index = (ny * size + nx) * 3
                        sum_r += pixels[index]
                        sum_g += pixels[index + 1]
                        sum_b += pixels[index + 2]
                        count += 1

            avg_r = int(sum_r / count)
            avg_g = int(sum_g / count)
            avg_b = int(sum_b / count)

            index = (y * size + x) * 3
            filtered_pixels[index] = avg_r
            filtered_pixels[index + 1] = avg_g
            filtered_pixels[index + 2] = avg_b

    pixels = filtered_pixels


def key_callback(window, key, scancode, action, mods):
    global pixels, points
    if action == glfw.PRESS:
        if key == glfw.KEY_ENTER:
            if len(points) > 2:
                bresenham2(points[-1][0], points[-1][1], points[0][0], points[0][1])
                seed_point = find_seed_point()
                if seed_point:
                    flood_fill(*seed_point, [255, 255, 255], [255, 0, 0])

                apply_post_filter(N=3)
        elif key == glfw.KEY_BACKSPACE:
            pixels = [255 for _ in range(size * size * 3)]
            points.clear()

    display(window)


def find_seed_point():
    if len(points) < 3: return None
    min_x = min(points, key=lambda x: x[0])[0]
    max_x = max(points, key=lambda x: x[0])[0]
    min_y = min(points, key=lambda x: x[1])[1]
    max_y = max(points, key=lambda x: x[1])[1]
    seed_x = (min_x + max_x) // 2
    seed_y = (min_y + max_y) // 2
    return seed_x, seed_y


def flood_fill(x, y, target_color, replacement_color):
    queue = deque([(x, y)])
    while queue:
        x, y = queue.popleft()
        current_pos = (x + y * size) * 3
        if x < 0 or x >= size or y < 0 or y >= size:
            continue
        if (pixels[current_pos] == target_color[0] and pixels[current_pos + 1] == target_color[1] and
                pixels[current_pos + 2] == target_color[2]):
            setPixel(x, y, *replacement_color)
            queue.append((x + 1, y))
            queue.append((x - 1, y))
            queue.append((x, y + 1))
            queue.append((x, y - 1))


def display(window):
    glClear(GL_COLOR_BUFFER_BIT)
    glDrawPixels(size, size, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    glfw.swap_buffers(window)
    glfw.poll_events()


def main():
    if not glfw.init():
        return
    window = glfw.create_window(size, size, "Lab4", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    glClearColor(1.0, 1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):
        display(window)

    glfw.terminate()


if __name__ == "__main__":
    main()

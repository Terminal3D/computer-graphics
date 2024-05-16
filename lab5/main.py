from collections import namedtuple

from OpenGL.GL import *
import glfw

size = 400

polygons = [[]]
current_polygon = 0
intersections = []
fill_polygons = False
Vertex = namedtuple('Vertex', ['coords', 'type', 'entry_exit'])
draw_dots = False
subject_vertices_list = []
clip_vertices_list = []
toClip = []


def line_intersection(p1, p2, p3, p4):
    A1 = p2[1] - p1[1]
    B1 = p1[0] - p2[0]
    C1 = A1 * p1[0] + B1 * p1[1]

    A2 = p4[1] - p3[1]
    B2 = p3[0] - p4[0]
    C2 = A2 * p3[0] + B2 * p3[1]

    determinant = A1 * B2 - A2 * B1

    if determinant == 0:
        return None

    x = (C1 * B2 - C2 * B1) / determinant
    y = (A1 * C2 - A2 * C1) / determinant

    if (min(p1[0], p2[0]) <= x <= max(p1[0], p2[0]) and
            min(p3[0], p4[0]) <= x <= max(p3[0], p4[0]) and
            min(p1[1], p2[1]) <= y <= max(p1[1], p2[1]) and
            min(p3[1], p4[1]) <= y <= max(p3[1], p4[1])):
        return x, y
    else:
        return None


def sort_vertices_and_intersections(clip_polygon, subject_polygon):
    vertices_list = []
    entry = True

    for i in range(len(subject_polygon)):
        p1 = subject_polygon[i]
        p2 = subject_polygon[(i + 1) % len(subject_polygon)]

        vertices_list.append(Vertex(coords=p1, type='vertex', entry_exit=None))

        segment_intersections = []
        for j in range(len(clip_polygon)):
            clip_p1 = clip_polygon[j]
            clip_p2 = clip_polygon[(j + 1) % len(clip_polygon)]

            intersection = line_intersection(p1, p2, clip_p1, clip_p2)
            if intersection:
                dist = ((intersection[0] - p1[0]) ** 2 + (intersection[1] - p1[1]) ** 2) ** 0.5
                segment_intersections.append((intersection, dist))

        segment_intersections.sort(key=lambda x: x[1])

        for inter, _ in segment_intersections:
            entry_exit_type = 'enter' if entry else 'exit'
            vertices_list.append(Vertex(coords=inter, type='intersection', entry_exit=entry_exit_type))
            entry = not entry

    vertices_list.append(Vertex(coords=subject_polygon[-1], type='vertex', entry_exit=None))
    return vertices_list


def weiler_atherton(subject_vertices, clip_vertices):
    toClip = []
    clipped = []
    entry_vertex_index = -1
    entry_points = set()

    # for i, vertex in enumerate(subject_vertices):
    #     if vertex.entry_exit == 'enter':
    #         entry_points.add(i)

    # while len(entry_points) != 0:
    #     i = entry_points.pop()
    i = 0
    while i < len(subject_vertices):
        vertex = subject_vertices[i]
        if vertex.entry_exit == 'enter':
            # if entry_points.__contains__(i):
            #     entry_points.remove(i)
            if entry_vertex_index == -1:
                entry_vertex_index = i
            current_vertex = vertex
            while current_vertex.entry_exit != 'exit':
                clipped.append(current_vertex)
                i += 1
                current_vertex = subject_vertices[i]
            entry_vertex = subject_vertices[entry_vertex_index]
            exit_vertex = current_vertex
            entry_index = next((i for i, v in enumerate(clip_vertices) if v.coords == entry_vertex.coords and abs(
                v.coords[0] - entry_vertex.coords[0]) < 0.0001 and abs(
                v.coords[1] - entry_vertex.coords[1]) < 0.0001),
                               None)
            exit_index = next((i for i, v in enumerate(clip_vertices) if
                               v.coords == exit_vertex.coords and abs(
                                   v.coords[0] - exit_vertex.coords[0]) < 0.0001 and abs(
                                   v.coords[1] - exit_vertex.coords[1]) < 0.0001), None)
            # if entry_index < exit_index:
            #     offset = -1
            # else:
            #     offset = 1
            offset = 1
            clipped.append(exit_vertex)
            exit_index += offset
            current_vertex = clip_vertices[exit_index]
            while current_vertex.type != 'intersection':
                clipped.append(current_vertex)
                exit_index += offset
                exit_index %= len(clip_vertices)
                current_vertex = clip_vertices[exit_index]

            if exit_index % len(clip_vertices) == entry_index:
                toClip.append(clipped.copy())
                clipped = []
                entry_vertex_index = -1
            else:
                i = next((i for i, v in enumerate(subject_vertices) if v.coords == current_vertex.coords and abs(
                    v.coords[0] - current_vertex.coords[0]) < 0.0001 and abs(
                    v.coords[1] - current_vertex.coords[1]) < 0.0001),
                         None)
        else:
            i += 1

    return toClip


# def perform_clipping(subject_vertices, clip_vertices):
#     toClip = []
#     clipped = []
#     entry_vertex = None
#
#     for vertex in subject_vertices:
#         if vertex.type == 'vertex' or vertex.entry_exit == 'enter':
#             if vertex.entry_exit == 'enter':
#                 clipped = [vertex]
#                 entry_vertex = vertex
#             elif clipped:
#                 clipped.append(vertex)
#         elif vertex.entry_exit == 'exit' and entry_vertex:
#             clipped.append(vertex)
#             entry_index = next((i for i, v in enumerate(clip_vertices) if v.coords == entry_vertex.coords and abs(
#                 v.coords[0] - entry_vertex.coords[0]) < 0.0001 and abs(v.coords[1] - entry_vertex.coords[1]) < 0.0001),
#                                None)
#             exit_index = next((i for i, v in enumerate(clip_vertices) if
#                                v.coords == vertex.coords and abs(v.coords[0] - vertex.coords[0]) < 0.0001 and abs(
#                                    v.coords[1] - vertex.coords[1]) < 0.0001), None)
#
#             if entry_index is not None and exit_index is not None:
#                 if entry_index < exit_index:
#                     for i in range(entry_index, exit_index + 1):
#                         clipped.append(clip_vertices[i])
#                 else:
#                     for i in range(entry_index, exit_index - 1, -1):
#                         clipped.append(clip_vertices[i])
#
#             toClip.append(clipped)
#             clipped = []
#             entry_vertex = None
#
#     return toClip


def mouse_button_callback(window, button, action, mods):
    global polygons, current_polygon
    if action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        x = (x / size) * 2 - 1
        y = -((y / size) * 2 - 1)

        if button == glfw.MOUSE_BUTTON_LEFT and len(polygons) < 3:
            polygons[current_polygon].append((x, y))


def key_callback(window, key, scancode, action, mods):
    global polygons, current_polygon, fill_polygons, draw_dots, subject_vertices_list, clip_vertices_list, toClip
    if action == glfw.PRESS:
        if key == glfw.KEY_D:
            if len(polygons[current_polygon]) > 2 and len(polygons) < 4:
                current_polygon += 1
                polygons.append([])
        elif key == glfw.KEY_F:
            fill_polygons = not fill_polygons
        elif key == glfw.KEY_C:
            subject_vertices_list = sort_vertices_and_intersections(polygons[0], polygons[1])
            clip_vertices_list = sort_vertices_and_intersections(polygons[1], polygons[0])
            toClip = weiler_atherton(subject_vertices_list, clip_vertices_list)
            draw_dots = True


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    mode = GL_POLYGON if fill_polygons else GL_LINE_LOOP

    for i, polygon in enumerate(polygons):
        if i % 2 == 0:
            glColor3f(1, 0, 0)
        else:
            glColor3f(0, 0, 1)

        glBegin(mode)
        for vertex in polygon:
            glVertex2f(*vertex)
        glEnd()

    glColor3f(0, 1, 0)
    for i, polygon in enumerate(toClip):
        glBegin(GL_LINE_LOOP)
        for vertex in polygon:
            glVertex2f(*vertex.coords)
        glEnd()

    glfw.swap_buffers(window)
    glfw.poll_events()


def main():
    global window
    if not glfw.init():
        return

    window = glfw.create_window(size, size, "Lab5", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_key_callback(window, key_callback)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):
        display()

    glfw.terminate()


if __name__ == "__main__":
    main()

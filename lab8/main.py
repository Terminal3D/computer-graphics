import math
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from math import cos, sin
from PIL import Image

# Shaders source code
vertex_shader_source = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 texcoord;

out vec3 FragPos;
out vec3 Normal;
out vec2 Texcoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    Texcoord = texcoord;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

fragment_shader_source = """
#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 Texcoord;

uniform sampler2D texture1;
uniform bool useTexture;

uniform vec3 light0Pos;
uniform vec3 light1Pos;
uniform bool light0Enabled;
uniform bool light1Enabled;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;

void main()
{
    vec3 ambient = 0.1 * lightColor;

    vec3 norm = normalize(Normal);
    vec3 lightDir0 = normalize(light0Pos - FragPos);
    vec3 lightDir1 = normalize(light1Pos - FragPos);

    float diff0 = max(dot(norm, lightDir0), 0.0);
    float diff1 = max(dot(norm, lightDir1), 0.0);

    vec3 diffuse = vec3(0.0);
    if (light0Enabled)
        diffuse += diff0 * lightColor;
    if (light1Enabled)
        diffuse += diff1 * lightColor;

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir0 = reflect(-lightDir0, norm);
    vec3 reflectDir1 = reflect(-lightDir1, norm);

    float spec0 = pow(max(dot(viewDir, reflectDir0), 0.0), 32);
    float spec1 = pow(max(dot(viewDir, reflectDir1), 0.0), 32);

    vec3 specular = vec3(0.0);
    if (light0Enabled)
        specular += spec0 * lightColor;
    if (light1Enabled)
        specular += spec1 * lightColor;

    vec3 result = (ambient + diffuse + specular) * objectColor;
    if (useTexture)
        FragColor = texture(texture1, Texcoord) * vec4(result, 1.0);
    else
        FragColor = vec4(result, 1.0);
}
"""

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

def create_shader_program():
    vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
    shader_program = compileProgram(vertex_shader, fragment_shader)
    return shader_program

def setup_lighting(shader_program):
    glUniform3f(glGetUniformLocation(shader_program, "light0Pos"), -2.0, 0.0, 0.0)
    glUniform3f(glGetUniformLocation(shader_program, "light1Pos"), 2.0, 0.0, 0.0)
    glUniform1i(glGetUniformLocation(shader_program, "light0Enabled"), light0_enabled)
    glUniform1i(glGetUniformLocation(shader_program, "light1Enabled"), light1_enabled)

def main():
    global texture_id, shader_program, VAO
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

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    shader_program = create_shader_program()

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    create_torus(size, size / 3, 40, 25)

    VBOs = glGenBuffers(3)

    glBindBuffer(GL_ARRAY_BUFFER, VBOs[0])
    glBufferData(GL_ARRAY_BUFFER, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, VBOs[1])
    glBufferData(GL_ARRAY_BUFFER, np.array(normals, dtype=np.float32), GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, VBOs[2])
    glBufferData(GL_ARRAY_BUFFER, np.array(tex_coords, dtype=np.float32), GL_STATIC_DRAW)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)

    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(indices, dtype=np.uint32), GL_STATIC_DRAW)

    glBindVertexArray(0)

    while not glfw.window_should_close(window):
        display(window)

    glfw.destroy_window(window)
    glfw.terminate()

def projection(shader_program):
    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)

    model = np.identity(4, dtype=np.float32)
    model = np.dot(model, np.array([
        [cos(alpha_rad), 0, sin(alpha_rad), 0],
        [0, 1, 0, 0],
        [-sin(alpha_rad), 0, cos(alpha_rad), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32))
    model = np.dot(model, np.array([
        [1, 0, 0, 0],
        [0, cos(beta_rad), -sin(beta_rad), 0],
        [0, sin(beta_rad), cos(beta_rad), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32))

    view = np.identity(4, dtype=np.float32)
    projection = np.identity(4, dtype=np.float32)

    glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, model)
    glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, view)
    glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, projection)

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

def display(window):
    global position_y, velocity_y, acceleration_y, use_texture, light0_enabled, light1_enabled, texture_id, shader_program, VAO

    velocity_y += acceleration_y * time_step
    position_y += velocity_y * time_step
    if position_y <= 0:
        position_y = -position_y
        velocity_y = -velocity_y

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glUseProgram(shader_program)

    projection(shader_program)

    glUniform1i(glGetUniformLocation(shader_program, "useTexture"), use_texture)
    glUniform3f(glGetUniformLocation(shader_program, "viewPos"), 0.0, 0.0, 3.0)
    glUniform3f(glGetUniformLocation(shader_program, "lightColor"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(shader_program, "objectColor"), 0.6, 0.6, 0.6)

    setup_lighting(shader_program)

    if use_texture:
        glBindTexture(GL_TEXTURE_2D, texture_id)

    glBindVertexArray(VAO)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

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

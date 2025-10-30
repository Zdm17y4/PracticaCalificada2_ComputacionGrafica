from glApp2.PyOGApp import *
from glApp2.Utils import *
from glApp2.LoadMesh import *

vertex_shader = r'''
#version 330 core

in vec3 position;
in vec3 vertex_color;
in vec3 vertex_normal;

uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;

out vec3 frag_color;
out vec3 frag_normal;
out vec3 frag_pos;
out vec3 light_pos;

void main()
{
    // Posición de la luz - movida más arriba para mejores reflejos metálicos
    vec3 light_position_world = vec3(view_mat[3][0], view_mat[3][1] + 3.0, view_mat[3][2] - 2.0);
    light_pos = vec3(inverse(model_mat) * vec4(light_position_world, 1.0));

    gl_Position = projection_mat * inverse(view_mat) * model_mat * vec4(position, 1.0);

    frag_normal = mat3(transpose(inverse(model_mat))) * vertex_normal;
    frag_pos = vec3(model_mat * vec4(position, 1.0));
    frag_color = vertex_color;
}
'''

fragment_shader = r'''
#version 330 core

in vec3 frag_color;
in vec3 frag_normal;
in vec3 frag_pos;
in vec3 light_pos;

out vec4 final_color;

uniform vec3 view_pos;

void main()
{
    // === Configuración para metal ===
    vec3 light_color = vec3(1.0, 1.0, 1.0);  // Se usa una luz blanca para simular el brillo metalico
    float ambient_strength = 0.1;            // Luz ambiente en cero
    float specular_strength = 1.2;           // Luz especular alta para mejorar el aspecto metalico
    int shininess = 64;                     // Brillo para un reflejo mas notorio

    // === Componentes de Blinn-Phong para metal ===
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);

    // 1. Luz ambiental (mínima en metales)
    vec3 ambient = ambient_strength * light_color;

    // 2. Luz difusa (reducida en metales)
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color * 1.5;  // Difusa muy atenuada

    // 3. Luz especular BLINN (muy fuerte en metales)
    vec3 view_dir = normalize(view_pos - frag_pos);
    vec3 halfway_dir = normalize(light_dir + view_dir);
    float spec = pow(max(dot(norm, halfway_dir), 0.0), shininess);
    vec3 specular = specular_strength * spec * light_color;

    // === Color metálico (plateado) ===
    vec3 metal_color = vec3(1.0, 1.0, 1.0);

    // === Mezcla METÁLICA ===
    // Los metales tienen: poco ambiente + poca difusa + MUCHO especular
    vec3 result = (ambient*0.1 + diffuse * 0.25) * metal_color + specular * 0.8;
    
    final_color = vec4(result, 1.0);
}
'''

class ShaderObjects(PyOGApp):

    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.sphere = None

    def initialise(self):
        self.program_id = create_program(vertex_shader, fragment_shader)
        model_path = os.path.join(os.path.dirname(__file__), "models", "sphere.obj")
        self.sphere = LoadMesh(model_path, self.program_id,
                                location=pygame.Vector3(0, 0, -2),
                                scale=pygame.Vector3(0.5, 0.5, 0.5),
                                move_rotation=Rotation(0, pygame.Vector3(0, 1, 0)))
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        glEnable(GL_DEPTH_TEST)

    def camera_init(self):
        pass

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()
        self.sphere.draw()

ShaderObjects().mainloop()
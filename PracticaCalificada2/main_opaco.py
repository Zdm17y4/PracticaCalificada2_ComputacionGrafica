from glApp1.PyOGApp import *
from glApp1.Utils import *
from glApp1.LoadMesh import *

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
    // Posición de la luz = posición de la cámara (como antes)
    light_pos = vec3(inverse(model_mat) * 
                     vec4(view_mat[3][0], view_mat[3][1], view_mat[3][2], 1.0));

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

void main()
{
    // === Configuración de la luz ===
    vec3 light_color = vec3(1.0, 0.8, 0.1);  // Luz amarilla naranjosa
    float ambient_strength = 0.1;            // Luz ambiente muy baja
    //No se usa una luz especular, ya que no se quiere que la luz rebote para tener un material opaco

    // === Componentes del modelo Lambertiano ===
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);

    //  componente ambiental
    vec3 ambient = ambient_strength * light_color;

    // componente difusa
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color;

    // === Resultado final ===
    vec3 result = (ambient + diffuse) * frag_color;
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
                            location=pygame.Vector3(0,0,-5),
                            scale=pygame.Vector3(1.0,1.0,1.0),
                            move_rotation=Rotation(1, pygame.Vector3(0,1,0)))
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        glEnable(GL_DEPTH_TEST)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()
        self.sphere.draw()

ShaderObjects().mainloop()


#version 330 core

in vec3 vertexColor;

out vec4 FragColor;

uniform vec4 uColor;

void main()
{
    FragColor = vec4(vertexColor, 1.0) * uColor;
}

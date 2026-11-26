#version 330 core

in vec3 vColor;
in vec3 vNormal;
in vec3 vFragPos;

uniform vec4 uColor;
uniform vec3 uLightDir;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform vec3 uFogColor;
uniform float uFogDensity;
uniform vec3 uCameraPos;

out vec4 FragColor;

void main()
{
    vec3 baseColor = vColor * uColor.rgb;
    vec3 norm = normalize(vNormal);
    if (length(vNormal) < 0.01) {
        norm = vec3(0.0, 1.0, 0.0);
    }

    vec3 lightDir = normalize(-uLightDir);
    float diff = max(dot(norm, lightDir), 0.0);

    // Napfény csillogás (Blinn-Phong)
    vec3 viewDir = normalize(uCameraPos - vFragPos);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfwayDir), 0.0), 32.0) * 0.25;

    // Fényerő: ha a vertex szín nagyon élénk (pl. neon/ablak/lámpa), kap egy kis önvilágítást
    float emissive = step(2.6, vColor.r + vColor.g + vColor.b) * 0.65;

    vec3 lighting = uAmbientColor + (diff * uLightColor) + (spec * uLightColor) + vec3(emissive);
    vec3 litColor = baseColor * lighting;

    // Procedurális felületi részletesség textúrák nélkül
    float grain = fract(sin(dot(floor(vFragPos.xz * 4.0), vec2(12.9898, 78.233))) * 43758.5453);
    litColor *= (0.96 + 0.08 * grain);

    // Atmoszférikus köd
    float dist = length(uCameraPos - vFragPos);
    float fogFactor = 1.0 - exp(-pow(dist * uFogDensity, 2.0));
    fogFactor = clamp(fogFactor, 0.0, 1.0);

    vec3 finalColor = mix(litColor, uFogColor, fogFactor);
    FragColor = vec4(finalColor, uColor.a);
}
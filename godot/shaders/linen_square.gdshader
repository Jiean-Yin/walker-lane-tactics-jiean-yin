shader_type spatial;

group_uniforms surface;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable;
uniform vec4 tint : source_color = vec4(1.0);
uniform float uv_scale : hint_range(0.5, 8.0, 0.05) = 3.65;

group_uniforms relief;
uniform sampler2D roughness_tex : filter_linear_mipmap, repeat_enable;
uniform float roughness_scale : hint_range(0.0, 1.0) = 1.0;
uniform sampler2D normal_tex : hint_normal, filter_linear_mipmap, repeat_enable;
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;

group_uniforms;

void fragment() {
	vec2 scaled_uv = UV * uv_scale;
	ALBEDO = texture(albedo_tex, scaled_uv).rgb * tint.rgb;
	ROUGHNESS = texture(roughness_tex, scaled_uv).r * roughness_scale;
	NORMAL_MAP = texture(normal_tex, scaled_uv).rgb;
	NORMAL_MAP_DEPTH = normal_strength;
}

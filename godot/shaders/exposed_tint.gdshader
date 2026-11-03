shader_type canvas_item;

uniform float exposed_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 exposed_color : source_color = vec4(0.878, 0.271, 0.227, 1.0);

void fragment() {
	COLOR.rgb = mix(COLOR.rgb, exposed_color.rgb, exposed_amount * 0.7);
}

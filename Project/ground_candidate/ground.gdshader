shader_type canvas_item;
uniform sampler2D soil_tex : source_color,filter_linear,repeat_enable;
uniform sampler2D grass_tex : source_color,filter_linear,repeat_enable;
uniform sampler2D continuous_data : filter_linear,repeat_disable;
uniform vec2 camera_origin=vec2(2112,1664);
varying vec2 world;
varying vec4 tint;
void vertex(){world=VERTEX+camera_origin;tint=COLOR;}
void fragment(){
 float code=tint.r*255.0;
 if(tint.g+tint.b>0.001 || (abs(code-16.0)>0.1 && abs(code-48.0)>0.1)){COLOR=texture(TEXTURE,UV)*tint;}
 else{float w=code>40.0?1.0:texture(continuous_data,(world-vec2(2208,1728)+vec2(.5))/vec2(961,705)).r;w=smoothstep(.35,.65,w);COLOR=vec4(mix(texture(grass_tex,world/384.0).rgb,texture(soil_tex,world/384.0).rgb,w),1.0);}
}

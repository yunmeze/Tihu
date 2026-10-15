shader_type canvas_item;
render_mode unshaded, blend_mix;
varying vec2 logical_position;
uniform vec4 tint : source_color = vec4(.035,.045,.055,1.0);
uniform bool active0=false;
uniform sampler2D atlas0:filter_linear,repeat_disable;
uniform vec2 size0;
uniform vec4 region0;
uniform vec2 bx0;uniform vec2 by0;uniform vec2 bo0;
uniform vec2 px0;uniform vec2 py0;uniform vec2 po0;
uniform vec4 bounds0;
uniform float blur0;uniform float opacity0;
float sample0(vec2 q){
 vec2 p=px0*q.x+py0*q.y+po0;
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,region0.zw)))return 0.;
 return textureLod(atlas0,(region0.xy+clamp(p,vec2(.5),region0.zw-vec2(.5)))/size0,0.).a;
}
float caster0(vec2 v){
 if(!active0)return 0.;
 vec2 q=bx0*v.x+by0*v.y+bo0;
 if(any(lessThan(q,bounds0.xy))||any(greaterThanEqual(q,bounds0.xy+bounds0.zw)))return 0.;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*sample0(q+vec2(float(x),float(y))*blur0);}
 return clamp(a/16.,0.,1.)*clamp(opacity0,0.,.42);
}
uniform bool active1=false;
uniform sampler2D atlas1:filter_linear,repeat_disable;
uniform vec2 size1;
uniform vec4 region1;
uniform vec2 bx1;uniform vec2 by1;uniform vec2 bo1;
uniform vec2 px1;uniform vec2 py1;uniform vec2 po1;
uniform vec4 bounds1;
uniform float blur1;uniform float opacity1;
float sample1(vec2 q){
 vec2 p=px1*q.x+py1*q.y+po1;
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,region1.zw)))return 0.;
 return textureLod(atlas1,(region1.xy+clamp(p,vec2(.5),region1.zw-vec2(.5)))/size1,0.).a;
}
float caster1(vec2 v){
 if(!active1)return 0.;
 vec2 q=bx1*v.x+by1*v.y+bo1;
 if(any(lessThan(q,bounds1.xy))||any(greaterThanEqual(q,bounds1.xy+bounds1.zw)))return 0.;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*sample1(q+vec2(float(x),float(y))*blur1);}
 return clamp(a/16.,0.,1.)*clamp(opacity1,0.,.42);
}
uniform bool active2=false;
uniform sampler2D atlas2:filter_linear,repeat_disable;
uniform vec2 size2;
uniform vec4 region2;
uniform vec2 bx2;uniform vec2 by2;uniform vec2 bo2;
uniform vec2 px2;uniform vec2 py2;uniform vec2 po2;
uniform vec4 bounds2;
uniform float blur2;uniform float opacity2;
float sample2(vec2 q){
 vec2 p=px2*q.x+py2*q.y+po2;
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,region2.zw)))return 0.;
 return textureLod(atlas2,(region2.xy+clamp(p,vec2(.5),region2.zw-vec2(.5)))/size2,0.).a;
}
float caster2(vec2 v){
 if(!active2)return 0.;
 vec2 q=bx2*v.x+by2*v.y+bo2;
 if(any(lessThan(q,bounds2.xy))||any(greaterThanEqual(q,bounds2.xy+bounds2.zw)))return 0.;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*sample2(q+vec2(float(x),float(y))*blur2);}
 return clamp(a/16.,0.,1.)*clamp(opacity2,0.,.42);
}
uniform bool active3=false;
uniform sampler2D atlas3:filter_linear,repeat_disable;
uniform vec2 size3;
uniform vec4 region3;
uniform vec2 bx3;uniform vec2 by3;uniform vec2 bo3;
uniform vec2 px3;uniform vec2 py3;uniform vec2 po3;
uniform vec4 bounds3;
uniform float blur3;uniform float opacity3;
float sample3(vec2 q){
 vec2 p=px3*q.x+py3*q.y+po3;
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,region3.zw)))return 0.;
 return textureLod(atlas3,(region3.xy+clamp(p,vec2(.5),region3.zw-vec2(.5)))/size3,0.).a;
}
float caster3(vec2 v){
 if(!active3)return 0.;
 vec2 q=bx3*v.x+by3*v.y+bo3;
 if(any(lessThan(q,bounds3.xy))||any(greaterThanEqual(q,bounds3.xy+bounds3.zw)))return 0.;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*sample3(q+vec2(float(x),float(y))*blur3);}
 return clamp(a/16.,0.,1.)*clamp(opacity3,0.,.42);
}
void vertex(){logical_position=VERTEX;}
void fragment(){float a=max(max(caster0(logical_position),caster1(logical_position)),max(caster2(logical_position),caster3(logical_position)));COLOR=vec4(tint.rgb,a);}

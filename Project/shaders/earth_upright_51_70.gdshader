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
uniform bool active4=false;
uniform sampler2D atlas4:filter_linear,repeat_disable;
uniform vec2 size4;
uniform vec4 region4;
uniform vec2 bx4;uniform vec2 by4;uniform vec2 bo4;
uniform vec2 px4;uniform vec2 py4;uniform vec2 po4;
uniform vec4 bounds4;
uniform float blur4;uniform float opacity4;
float sample4(vec2 q){
 vec2 p=px4*q.x+py4*q.y+po4;
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,region4.zw)))return 0.;
 return textureLod(atlas4,(region4.xy+clamp(p,vec2(.5),region4.zw-vec2(.5)))/size4,0.).a;
}
float caster4(vec2 v){
 if(!active4)return 0.;
 vec2 q=bx4*v.x+by4*v.y+bo4;
 if(any(lessThan(q,bounds4.xy))||any(greaterThanEqual(q,bounds4.xy+bounds4.zw)))return 0.;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*sample4(q+vec2(float(x),float(y))*blur4);}
 return clamp(a/16.,0.,1.)*clamp(opacity4,0.,.42);
}
uniform bool s_contact_active=false;
uniform sampler2D s_body:filter_linear,repeat_disable;
uniform vec2 s_origin;
uniform float s_phase=0.;
vec2 s_inverse(vec2 q){
 float t=1.55*q.x-1.2*q.y;
 float f=-2.0625+4.125*clamp((t+39.46875)/4.,0.,1.);
 float y;
 float q1=88.234375+1.55*f;
 if(q.y>=99.234375)y=(132.234375-q.y)/.55;
 else if(q.y>q1)y=(q.y-132.234375+4.65*f)/(-.55+.0775*f);
 else y=(132.234375+1.55*f-q.y)/.55;
 return vec2((t+1.2*y)/1.55,y);
}
float s_sample(vec2 q){
 vec2 p=s_inverse(q)*4.;
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,vec2(512.))))return 0.;
 return textureLod(s_body,(vec2(s_phase*512.,0.)+clamp(p,vec2(.5),vec2(511.5)))/vec2(2048.,512.),0.).a;
}
float s_caster(vec2 v){
 if(!s_contact_active)return 0.;
 vec2 q=v-s_origin;
 // Frozen complete four-phase alpha/filter/read-error union AABB.
 if(any(lessThan(q,vec2(26.5,79.)))||any(greaterThanEqual(q,vec2(130.5,127.))))return 0.;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*s_sample(q+vec2(float(x),float(y))*.8);}
 return clamp(a/16.,0.,1.)*.25;
}
void vertex(){logical_position=VERTEX;}
uniform bool s_walk_active=false;
uniform sampler2D s_walk_body:filter_linear,repeat_disable;
uniform vec2 s_walk_origin;
float s_walk_read(vec2 logical_p){
 vec2 p=logical_p*4.;
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,vec2(512.))))return 0.;
 return textureLod(s_walk_body,clamp(p,vec2(.5),vec2(511.5))/vec2(512.),0.).a;
}
float s_walk_sample(vec2 q){
 // Both source half-planes fold onto q.y>=b; never choose just one inverse.
 if(q.y<85.3125)return 0.;
 float upper_y=(132.234375-q.y)/.55;
 vec2 upper=vec2(q.x+1.2*upper_y-102.375,upper_y);
 // Original full-alpha samples, then per-tap owner union. Never sum opacity.
 return max(s_walk_read(upper),s_walk_read(q));
}
float s_walk_caster(vec2 v){
 if(!s_walk_active)return 0.;
 vec2 q=v-s_walk_origin;
 if(any(lessThan(q,vec2(5.5,83.5)))||any(greaterThanEqual(q,vec2(175.5,130.))))return 0.;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*s_walk_sample(q+vec2(float(x),float(y))*.8);}
 return clamp(a/16.,0.,1.)*.25;
}
uniform bool tree_pilot_active=false;
uniform sampler2D tree_pilot_body:filter_linear,repeat_disable;
uniform sampler2D tree_pilot_receiver:filter_nearest,repeat_disable;
uniform vec2 tree_pilot_camera;
float tree_pilot_sample(vec2 q){
 float sy=(2059.95-q.y)/.55;
 vec2 p=vec2(q.x+1.2*sy-1594.8,sy);
 if(any(lessThan(p,vec2(0.)))||any(greaterThanEqual(p,vec2(1162.,1353.))))return 0.;
 return textureLod(tree_pilot_body,clamp(p,vec2(.5),vec2(1161.5,1352.5))/vec2(1162.,1353.),0.).a;
}
float tree_pilot_caster(vec2 v){
 if(!tree_pilot_active)return 0.;
 vec2 world=v-tree_pilot_camera;
 vec2 maskp=(world-vec2(2368.,2238.))*2.;
 if(any(lessThan(maskp,vec2(0.)))||any(greaterThanEqual(maskp,vec2(1208.,388.))))return 0.;
 float allowed=textureLod(tree_pilot_receiver,(floor(maskp)+vec2(.5))/vec2(1208.,388.),0.).r;
 if(allowed<.5)return 0.;
 vec2 q=(world-vec2(2359.5555555555557,1958.6666666666667))*4.5;
 float a=0.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){float w=(x==0?2.:1.)*(y==0?2.:1.);a+=w*tree_pilot_sample(q+vec2(float(x),float(y))*3.6);}
 return clamp(a/16.,0.,1.)*.25;
}
void fragment(){float a=max(max((s_contact_active?s_caster(logical_position):caster0(logical_position)),caster1(logical_position)),max(caster2(logical_position),caster3(logical_position)));a=max(a,caster4(logical_position));a=max(a,s_walk_caster(logical_position));a=max(a,tree_pilot_caster(logical_position));COLOR=vec4(tint.rgb,a);}

import bpy, math
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.frame_start=1; scene.frame_end=288; scene.render.fps=24
scene.render.resolution_x=720; scene.render.resolution_y=1280; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'; scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath='/tmp/kids-vehicle-3d.mp4'
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except Exception: scene.render.engine='BLENDER_EEVEE'

# ---------- helpers ----------
def mat(name,color,metal=0.0,rough=.25):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=(*color,1)
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*color,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    return m

def rc(name,loc,scale,material,bevel=.2):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    md=o.modifiers.new('soft','BEVEL'); md.width=bevel; md.segments=6; bpy.ops.object.shade_smooth(); o.data.materials.append(material); return o

def sph(name,loc,scale,material,segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=16,location=loc); o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); bpy.ops.object.shade_smooth(); o.data.materials.append(material); return o

def cyl(name,loc,radius,depth,material,rot=(math.pi/2,0,0),verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=name; bpy.ops.object.shade_smooth(); o.data.materials.append(material); return o

def look_at(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def key(o,f,loc=None,rot=None,scale=None):
    if loc is not None: o.location=loc; o.keyframe_insert('location',frame=f)
    if rot is not None: o.rotation_euler=rot; o.keyframe_insert('rotation_euler',frame=f)
    if scale is not None: o.scale=scale; o.keyframe_insert('scale',frame=f)
def bezier(o):
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation='BEZIER'

# ---------- materials ----------
BLUE=mat('BeepBlue',(0.015,.27,.95),.08,.16); RED=mat('ReddyRed',(.98,.025,.025),.10,.17)
YEL=mat('DumpyYellow',(1,.63,.02),.05,.20); GREEN=mat('TractoGreen',(.06,.58,.08),.04,.22)
BLACK=mat('Black',(.01,.012,.018),0,.38); WHITE=mat('White',(.98,.99,1),0,.13)
CHROME=mat('Chrome',(.72,.78,.88),.72,.12); GLASS=mat('Glass',(.10,.56,.94),.18,.10)
MUD=mat('Mud',(.19,.05,.015),0,.62); ROAD=mat('Road',(.14,.16,.19),0,.78); GRASS=mat('Grass',(.17,.62,.10),0,.82)
ORANGE=mat('TowOrange',(1,.23,.015),.06,.18); DARK=mat('Mouth',(.03,.012,.012),0,.30)
LRED=mat('LightRed',(1,.03,.03),.04,.13); LBLUE=mat('LightBlue',(.03,.55,1),.04,.13)

# ---------- world ----------
rc('ground',(0,0,-.92),(11,11,.5),GRASS,.05); rc('road',(0,0,-.28),(10,3.2,.14),ROAD,.05)
for x in (-6,-2,2,6):
    rc('edgeA'+str(x),(x,-2.68,-.10),(.8,.055,.024),WHITE,.015); rc('edgeB'+str(x),(x,2.68,-.10),(.8,.055,.024),WHITE,.015)
sph('mud',(-1.45,.45,-.07),(2.3,1.6,.20),MUD,28)
for i,(x,y,s) in enumerate([(-6.5,4,1),(-4.8,4.5,.8),(6,4,1),(7.5,4.6,.78),(-7,-4,.72),(6.8,-3.9,.9)]):
    cyl('trunk'+str(i),(x,y,.45),.16*s,1.7*s,MUD,(0,0,0),16); sph('tree'+str(i),(x,y,1.7*s),(.78*s,.78*s,1.0*s),GREEN,20)

# ---------- polished character vehicle ----------
def vehicle(name,color,x,y,z,kind='car',s=1.0):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root); root.location=(x,y,z); root.scale=(s,s,s)
    # rounder lower shell
    body=rc(name+'_body',(0,0,.66),(1.22,.78,.38),color,.30); body.parent=root
    nose=rc(name+'_nose',(.88,0,.82),(.52,.69,.25),color,.25); nose.parent=root
    cab=rc(name+'_cab',(.02,0,1.24),(.70,.68,.53),color,.30); cab.parent=root
    # large windshield with integrated eyes
    glass=rc(name+'_glass',(.72,0,1.37),(.05,.57,.34),GLASS,.09); glass.parent=root
    eyes=[]; pupils=[]
    for yy in (-.23,.23):
        e=sph(name+'_eye'+str(yy),(.79,yy,1.43),(.045,.145,.158),WHITE,22); e.parent=root; eyes.append(e)
        p=sph(name+'_pupil'+str(yy),(.835,yy,1.43),(.025,.060,.073),BLACK,18); p.parent=root; pupils.append(p)
        sh=sph(name+'_shine'+str(yy),(.855,yy-.022,1.475),(.010,.018,.022),WHITE,12); sh.parent=root
    # eyebrows for expression
    brows=[]
    for yy in (-.23,.23):
        b=rc(name+'_brow'+str(yy),(.845,yy,1.61),(.018,.13,.022),BLACK,.02); b.parent=root; brows.append(b)
    mouth=sph(name+'_mouth',(1.31,0,.83),(.045,.245,.070),DARK,20); mouth.parent=root
    bumper=rc(name+'_bumper',(1.38,0,.53),(.085,.62,.08),CHROME,.06); bumper.parent=root
    for yy in (-.53,.53):
        h=sph(name+'_lamp'+str(yy),(1.34,yy,.78),(.075,.09,.085),WHITE,16); h.parent=root
    wheels=[]
    for xx in (-.67,.69):
        for yy in (-.79,.79):
            w=cyl(name+'_wheel',(xx,yy,.34),.34,.25,BLACK,(math.pi/2,0,0),24); w.parent=root; wheels.append(w)
            hub=cyl(name+'_hub',(xx,yy,.34),.16,.266,CHROME,(math.pi/2,0,0),20); hub.parent=root
    if kind=='rescue':
        rear=rc(name+'_rear',(-.77,0,1.07),(.80,.75,.58),color,.21); rear.parent=root
        roof=rc(name+'_roof',(-.12,0,1.77),(.66,.62,.09),color,.08); roof.parent=root
        for yy,m in [(-.21,LRED),(.21,LBLUE)]:
            l=rc(name+'_light'+str(yy),(.12,yy,1.92),(.18,.14,.075),m,.04); l.parent=root
        st=rc(name+'_stripe',(-.72,-.76,1.04),(.60,.02,.06),WHITE,.015); st.parent=root
    elif kind=='dump':
        bed=rc(name+'_bed',(-.72,0,1.16),(.92,.77,.40),color,.16); bed.parent=root; bed.rotation_euler[1]=math.radians(-7)
    elif kind=='tractor':
        hd=rc(name+'_tracthood',(.58,0,.91),(.70,.58,.27),color,.17); hd.parent=root
    root['wheels']=[w.name for w in wheels]; root['pupils']=[p.name for p in pupils]; root['brows']=[b.name for b in brows]; root['mouth']=mouth.name
    return root

beep=vehicle('Beep',BLUE,-5.2,.48,.08,'car',1.0); reddy=vehicle('Reddy',RED,6.4,-.78,.08,'rescue',1.14)
dumpy=vehicle('Dumpy',YEL,4.8,2.35,.05,'dump',.78); tracto=vehicle('Tracto',GREEN,6.2,3.05,.05,'tractor',.76)

# ---------- story animation ----------
# Beep drive + suspension bounce
key(beep,1,(-5.2,.48,.08)); key(beep,28,(-3.55,.48,.13)); key(beep,55,(-1.55,.48,.08)); key(beep,80,(-1.42,.48,-.10)); key(beep,112,(-1.42,.48,-.16))
for f,y,z,r in [(86,.36,-.12,-.05),(92,.60,-.17,.05),(98,.34,-.13,-.04),(104,.58,-.17,.04),(110,.45,-.16,0)]:
    key(beep,f,(-1.42,y,z),(0,r,0))
# Reddy arrival
key(reddy,68,(6.4,-.78,.08)); key(reddy,115,(3.5,-.78,.12)); key(reddy,144,(1.65,-.78,.08)); key(reddy,164,(1.65,-.78,.08)); key(reddy,232,(5.0,-.78,.08))
key(beep,164,(-1.42,.48,-.16)); key(beep,232,(2.05,.48,.10))
# celebration
for f,z in [(238,.10),(248,.32),(258,.10),(268,.29),(280,.10)]: key(beep,f,(2.05,.48,z))
for f,z in [(238,.08),(248,.24),(258,.08),(268,.21),(280,.08)]: key(reddy,f,(5.0,-.78,z))
bezier(beep); bezier(reddy)

# wheel spin
for root in (beep,reddy):
    for wn in root['wheels']:
        w=bpy.data.objects[wn]; w.rotation_euler=(math.pi/2,0,0); w.keyframe_insert('rotation_euler',frame=1)
        w.rotation_euler=(math.pi/2,0,math.radians(1800)); w.keyframe_insert('rotation_euler',frame=232)

# facial expression animation - Beep scared then relieved
for pn in beep['pupils']:
    p=bpy.data.objects[pn]; p.scale=(1,1,1); p.keyframe_insert('scale',frame=60); p.scale=(1.25,1.25,1.25); p.keyframe_insert('scale',frame=88); p.scale=(1,1,1); p.keyframe_insert('scale',frame=235)
for bn in beep['brows']:
    b=bpy.data.objects[bn]; b.rotation_euler=(0,0,0); b.keyframe_insert('rotation_euler',frame=60); b.rotation_euler=(math.radians(18),0,0); b.keyframe_insert('rotation_euler',frame=90); b.rotation_euler=(0,0,0); b.keyframe_insert('rotation_euler',frame=235)
m=bpy.data.objects[beep['mouth']]; m.scale=(1,1,1); m.keyframe_insert('scale',frame=60); m.scale=(1,1.25,1.35); m.keyframe_insert('scale',frame=90); m.scale=(1,1,1); m.keyframe_insert('scale',frame=235)

# tow rope + hook clarity
hook=rc('TowHook',(1.37,-.32,.58),(.08,.10,.08),CHROME,.04); hook.scale=(.01,.01,.01); hook.keyframe_insert('scale',frame=145); hook.scale=(1,1,1); hook.keyframe_insert('scale',frame=160); hook.scale=(.01,.01,.01); hook.keyframe_insert('scale',frame=238)
rope=cyl('TowRope',(.15,-.14,.62),.045,3.55,ORANGE,(0,math.pi/2,0),16); rope.rotation_euler[0]=math.radians(-10)
rope.scale=(1,1,.001); rope.keyframe_insert('scale',frame=146); rope.scale=(1,1,1); rope.keyframe_insert('scale',frame=160)
rope.location=(.08,-.14,.62); rope.keyframe_insert('location',frame=164); rope.location=(3.50,-.14,.62); rope.keyframe_insert('location',frame=232); rope.scale=(1,1,.001); rope.keyframe_insert('scale',frame=238)

# richer mud splash
for i in range(18):
    ang=(i/18.0)*math.tau; rad=.25+.20*(i%4); sx=-1.42+math.cos(ang)*rad; sy=.48+math.sin(ang)*rad*.65
    o=sph('splash'+str(i),(sx,sy,.03),(.06+.012*(i%3),.06+.012*(i%3),.10+.02*(i%4)),MUD,14)
    o.scale=(.01,.01,.01); o.keyframe_insert('scale',frame=72); o.scale=(1,1,1); o.keyframe_insert('scale',frame=84+i%5)
    o.location.z=.48+.10*(i%5); o.keyframe_insert('location',frame=91+i%5); o.scale=(.01,.01,.01); o.keyframe_insert('scale',frame=112)

# ---------- cinematic camera ----------
bpy.ops.object.camera_add(location=(8.5,-15.0,6.6)); cam=bpy.context.object; scene.camera=cam; cam.data.lens=58
look_at(cam,(-2.0,.25,.95)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(5.9,-10.6,4.7); look_at(cam,(-1.38,.45,1.05)); cam.keyframe_insert('location',frame=88); cam.keyframe_insert('rotation_euler',frame=88)
cam.location=(7.8,-13.5,5.8); look_at(cam,(.15,-.05,1.05)); cam.keyframe_insert('location',frame=150); cam.keyframe_insert('rotation_euler',frame=150)
cam.location=(6.4,-11.9,5.0); look_at(cam,(1.0,-.05,.95)); cam.keyframe_insert('location',frame=188); cam.keyframe_insert('rotation_euler',frame=188)
cam.location=(9.0,-15.4,6.5); look_at(cam,(2.3,-.05,1.0)); cam.keyframe_insert('location',frame=232); cam.keyframe_insert('rotation_euler',frame=232)
cam.location=(9.5,-16.1,7.1); look_at(cam,(2.9,-.05,1.0)); cam.keyframe_insert('location',frame=288); cam.keyframe_insert('rotation_euler',frame=288)

# ---------- lights ----------
bpy.ops.object.light_add(type='SUN',location=(0,0,8)); sun=bpy.context.object; sun.data.energy=2.3; sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-32))
bpy.ops.object.light_add(type='AREA',location=(1.5,-5.5,7.5)); keyl=bpy.context.object; keyl.data.energy=1350; keyl.data.shape='DISK'; keyl.data.size=8; look_at(keyl,(0,0,1))
bpy.ops.object.light_add(type='AREA',location=(-4,4,4.8)); fill=bpy.context.object; fill.data.energy=760; fill.data.size=7; look_at(fill,(-1,0,1))
bpy.ops.object.light_add(type='AREA',location=(4,4,6)); rim=bpy.context.object; rim.data.energy=560; rim.data.size=5; look_at(rim,(2,0,1))
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.24,.52,1.0,1); bg.inputs['Strength'].default_value=.74
try: scene.view_settings.look='AgX - Medium High Contrast'
except Exception: pass

bpy.ops.wm.save_as_mainfile(filepath='/tmp/kids_vehicle_scene.blend')
bpy.ops.render.render(animation=True)
print(scene.render.filepath)

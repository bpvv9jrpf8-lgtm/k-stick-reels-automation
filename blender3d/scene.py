import bpy, math, os
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene=bpy.context.scene
scene.frame_start=1
scene.frame_end=288
scene.render.fps=24
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4'
scene.render.ffmpeg.codec='H264'
scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath='/tmp/kids-vehicle-3d.mp4'
try:
    scene.render.engine='BLENDER_EEVEE_NEXT'
except:
    scene.render.engine='BLENDER_EEVEE'
scene.render.film_transparent=False
scene.world.color=(0.10,0.25,0.55)

# Helpers
def mat(name,color,metal=0.0,rough=.32):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Metallic'].default_value=metal
    bsdf.inputs['Roughness'].default_value=rough
    return m

def rounded_cube(name,loc,scale,material,bevel=.18):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=o.modifiers.new('soft','BEVEL'); mod.width=bevel; mod.segments=5
    bpy.ops.object.shade_smooth(); o.data.materials.append(material)
    return o

def sphere(name,loc,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=18, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.shade_smooth(); o.data.materials.append(material)
    return o

def cyl(name,loc,radius,depth,material,rot=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; bpy.ops.object.shade_smooth(); o.data.materials.append(material)
    return o

def look_at(obj,target):
    direction=Vector(target)-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

def key(obj,frame,loc=None,rot=None,scale=None):
    if loc is not None: obj.location=loc; obj.keyframe_insert('location',frame=frame)
    if rot is not None: obj.rotation_euler=rot; obj.keyframe_insert('rotation_euler',frame=frame)
    if scale is not None: obj.scale=scale; obj.keyframe_insert('scale',frame=frame)

def add_smile(parent,xoff,front_x,z,material):
    # simple curved smile using torus segment substitute: flattened dark oval
    m=sphere('smile',(front_x,-.02,z),(.34,.10,.10),material); m.parent=parent; return m

# Materials
blue=mat('Blue',(0.03,0.32,0.95),0.08,.22)
red=mat('Red',(0.95,0.03,0.03),0.10,.22)
yellow=mat('Yellow',(1.0,.62,.02),0.05,.25)
green=mat('Green',(.08,.55,.08),0.04,.27)
black=mat('Black',(.02,.025,.03),0.0,.38)
white=mat('White',(.97,.98,1),0,.18)
chrome=mat('Chrome',(.65,.70,.76),.75,.16)
brown=mat('Mud',(.20,.07,.02),0,.72)
roadm=mat('Road',(.29,.22,.16),0,.78)
grass=mat('Grass',(.20,.58,.11),0,.85)
window=mat('Window',(.25,.72,.95),.15,.12)
orange=mat('Orange',(1,.28,.03),.05,.25)

# Environment
rounded_cube('ground',(0,0,-.85),(10,10,.5),grass,.05)
rounded_cube('road',(0,0,-.28),(9,3.0,.14),roadm,.04)
sphere('mudpatch',(-1.3,0,-.10),(2.0,2.0,.18),brown)
for i in range(8):
    sphere(f'rock{i}',(-2.2+i*.58,1.4+((i%2)*.35),-.02),(.16+.04*(i%3),)*3,brown)
# trees
for x,y,s in [(-6,3,1.2),(-4,4,.9),(5,3,1.1),(7,4,.9),(-7,-3,.8),(6,-3,1.0)]:
    cyl('trunk',(x,y,.35),.18*s,1.8*s,brown,rot=(0,0,0))
    sphere('leaf',(x,y,1.8*s),(.85*s,.85*s,1.1*s),green)

# Vehicle constructor: facing +X
def vehicle(name,color_mat,x,y,z,kind='car',scale=1.0):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root); root.location=(x,y,z)
    body=rounded_cube(name+'_body',(0,0,.65),(1.25,.82,.42),color_mat,.22); body.parent=root
    cab=rounded_cube(name+'_cab',(.25,0,1.25),(.72,.72,.52),color_mat,.20); cab.parent=root
    windshield=rounded_cube(name+'_glass',(.84,-.01,1.33),(.06,.56,.31),window,.08); windshield.parent=root
    # face on front (+X)
    for yy in (-.27,.27):
        eye=sphere(name+'_eye',(1.34,yy,1.34),(.16,.14,.18),white); eye.parent=root
        pupil=sphere(name+'_pupil',(1.48,yy,1.34),(.075,.07,.085),black); pupil.parent=root
    smile=sphere(name+'_smile',(1.42,0,1.02),(.07,.27,.08),black); smile.parent=root
    # bumper
    bumper=rounded_cube(name+'_bumper',(1.35,0,.55),(.10,.68,.10),chrome,.06); bumper.parent=root
    wheels=[]
    for xx in (-.68,.75):
        for yy in (-.78,.78):
            w=cyl(name+'_wheel',(xx,yy,.36),.34,.24,black,rot=(math.pi/2,0,0)); w.parent=root; wheels.append(w)
            hub=cyl(name+'_hub',(xx,yy,.36),.16,.255,chrome,rot=(math.pi/2,0,0)); hub.parent=root
    if kind=='rescue':
        box=rounded_cube(name+'_rear',(-.72,0,1.08),(.82,.78,.62),red,.15); box.parent=root
        light1=rounded_cube(name+'_lightR',(.18,-.18,1.88),(.28,.18,.09),red,.04); light1.parent=root
        light2=rounded_cube(name+'_lightB',(.18,.18,1.88),(.28,.18,.09),blue,.04); light2.parent=root
    if kind=='dump':
        bed=rounded_cube(name+'_bed',(-.72,0,1.20),(.94,.78,.48),yellow,.12); bed.parent=root; bed.rotation_euler[1]=math.radians(-8)
    if kind=='tractor':
        hood=rounded_cube(name+'_hood',(.72,0,.90),(.70,.62,.28),green,.12); hood.parent=root
    root['wheels']=[w.name for w in wheels]
    root.scale=(scale,scale,scale)
    return root

beep=vehicle('Beep',blue,-5.0,0,.08,'car',1.0)
reddy=vehicle('Reddy',red,6.0,-.2,.08,'rescue',1.18)
dumpy=vehicle('Dumpy',yellow,3.6,2.35,.02,'dump',.88)
tracto=vehicle('Tracto',green,5.0,3.0,.02,'tractor',.83)

# Animate Beep driving in then stuck
key(beep,1,(-5,0,.08)); key(beep,58,(-1.45,0,.08)); key(beep,82,(-1.35,0,-.10)); key(beep,110,(-1.35,0,-.16))
# wobble struggling
for f,yy,zz in [(88,-.10,-.12),(94,.12,-.17),(100,-.08,-.13),(106,.08,-.17)]: key(beep,f,(-1.35,yy,zz))
# Reddy arrives
key(reddy,70,(6,-.2,.08)); key(reddy,145,(1.7,-.2,.08))
# Tow and pull both out
key(beep,164,(-1.35,0,-.16)); key(beep,230,(2.15,0,.10)); key(reddy,164,(1.7,-.2,.08)); key(reddy,230,(4.75,-.2,.08))
# celebration bounce
for f,z in [(238,.10),(248,.32),(258,.10),(268,.28),(280,.10)]: key(beep,f,(2.15,0,z))
for f,z in [(238,.08),(248,.23),(258,.08),(268,.20),(280,.08)]: key(reddy,f,(4.75,-.2,z))

# Wheel rotation
for root in (beep,reddy):
    for wn in root['wheels']:
        w=bpy.data.objects[wn]
        w.rotation_euler=(math.pi/2,0,0); w.keyframe_insert('rotation_euler',frame=1)
        w.rotation_euler=(math.pi/2,0,math.radians(1440)); w.keyframe_insert('rotation_euler',frame=230)

# Tow rope cylinder between vehicles - initially hidden with tiny scale
rope=cyl('TowRope',(0.2,-.1,.62),.055,3.2,orange,rot=(0,math.pi/2,0))
rope.scale=(1,1,.001); rope.keyframe_insert('scale',frame=145)
rope.scale=(1,1,1); rope.keyframe_insert('scale',frame=160)
rope.location=(.15,-.1,.62); rope.keyframe_insert('location',frame=164)
rope.location=(3.45,-.1,.62); rope.keyframe_insert('location',frame=230)

# Mud splash blobs animated up/down near Beep
for i in range(10):
    o=sphere('splash'+str(i),(-1.35+(i%5-.2)*.18, (-1)**i*.55, .1),(.10,.10,.16),brown)
    o.scale=(.01,.01,.01); o.keyframe_insert('scale',frame=74)
    o.scale=(1,1,1); o.keyframe_insert('scale',frame=88+i%3)
    o.location.z=.7+.12*(i%4); o.keyframe_insert('location',frame=92+i%3)
    o.scale=(.01,.01,.01); o.keyframe_insert('scale',frame=108)

# Camera
bpy.ops.object.camera_add(location=(9,-16,8.5))
cam=bpy.context.object; look_at(cam,(0.8,0,1.0)); scene.camera=cam
cam.data.lens=48
cam.keyframe_insert('location',frame=1)
cam.location=(7.8,-14.2,7.2); look_at(cam,(-.4,0,1.0)); cam.keyframe_insert('location',frame=105); cam.keyframe_insert('rotation_euler',frame=105)
cam.location=(8.8,-15.5,8.0); look_at(cam,(1.3,0,1.0)); cam.keyframe_insert('location',frame=230); cam.keyframe_insert('rotation_euler',frame=230)

# Lights
bpy.ops.object.light_add(type='SUN', location=(0,0,8)); sun=bpy.context.object; sun.data.energy=3.0; sun.rotation_euler=(math.radians(25),math.radians(-25),math.radians(-30))
bpy.ops.object.light_add(type='AREA', location=(2,-5,7)); area=bpy.context.object; area.data.energy=1000; area.data.shape='DISK'; area.data.size=8; look_at(area,(0,0,1))
bpy.ops.object.light_add(type='AREA', location=(-4,3,4)); fill=bpy.context.object; fill.data.energy=650; fill.data.size=6; look_at(fill,(-1,0,1))

# World sky nodes
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(0.28,0.58,1.0,1)
bg.inputs['Strength'].default_value=.65

# Color management
scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' else scene.view_settings.look

# Render
bpy.ops.wm.save_as_mainfile(filepath='/tmp/kids_vehicle_scene.blend')
bpy.ops.render.render(animation=True)
print(scene.render.filepath)

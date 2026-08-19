import bpy, math
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
except Exception:
    scene.render.engine='BLENDER_EEVEE'

# ---------- helpers ----------
def mat(name,color,metal=0.0,rough=.28):
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

def sphere(name,loc,scale,material,segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=16, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.shade_smooth(); o.data.materials.append(material)
    return o

def cyl(name,loc,radius,depth,material,rot=(math.pi/2,0,0),verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; bpy.ops.object.shade_smooth(); o.data.materials.append(material)
    return o

def look_at(obj,target):
    direction=Vector(target)-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

def key(obj,frame,loc=None,rot=None,scale=None):
    if loc is not None:
        obj.location=loc; obj.keyframe_insert('location',frame=frame)
    if rot is not None:
        obj.rotation_euler=rot; obj.keyframe_insert('rotation_euler',frame=frame)
    if scale is not None:
        obj.scale=scale; obj.keyframe_insert('scale',frame=frame)

def set_interp(obj):
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation='BEZIER'

# ---------- materials ----------
blue=mat('BeepBlue',(0.02,0.28,0.92),0.06,.20)
red=mat('ReddyRed',(0.95,0.025,0.025),0.08,.20)
yellow=mat('DumpyYellow',(1.0,.60,.02),0.04,.23)
green=mat('TractoGreen',(.06,.52,.08),0.03,.25)
black=mat('TireBlack',(.015,.018,.025),0.0,.42)
white=mat('EyeWhite',(.98,.99,1),0,.16)
chrome=mat('Chrome',(.70,.76,.84),.68,.14)
window=mat('Windshield',(.16,.58,.92),.10,.15)
roadm=mat('Road',(.16,.18,.21),0,.72)
grass=mat('Grass',(.18,.61,.10),0,.80)
brown=mat('Mud',(.18,.055,.018),0,.72)
orange=mat('TowOrange',(1,.25,.02),.03,.22)
lightblue=mat('LightBlue',(.04,.55,1.0),.05,.16)
softred=mat('LightRed',(1.0,.05,.05),.05,.16)
cream=mat('Smile',(.035,.02,.02),0,.32)

# ---------- environment ----------
rounded_cube('ground',(0,0,-.92),(11,11,.50),grass,.05)
rounded_cube('road',(0,0,-.28),(10,3.25,.14),roadm,.05)
# road edge stripes
for x in (-6,-2,2,6):
    rounded_cube('stripe'+str(x),(x,-2.72,-.10),(.85,.06,.025),white,.02)
    rounded_cube('stripe2'+str(x),(x,2.72,-.10),(.85,.06,.025),white,.02)
# glossy mud basin
sphere('mudpatch',(-1.45,.35,-.08),(2.25,1.72,.20),brown)
for i,(dx,dy,s) in enumerate([(-1.8,1.2,.18),(-1.3,1.45,.13),(-.8,1.20,.16),(-1.9,-.8,.12),(-.9,-1.0,.15)]):
    sphere('mudrock'+str(i),(dx,dy,.00),(s,s,s),brown,16)
# trees
for i,(x,y,s) in enumerate([(-6.5,3.8,1.05),(-4.8,4.5,.82),(5.8,4.1,1.0),(7.4,4.5,.78),(-7,-3.8,.72),(6.7,-3.7,.9)]):
    cyl('trunk'+str(i),(x,y,.45),.16*s,1.7*s,brown,rot=(0,0,0),verts=16)
    sphere('leaf'+str(i),(x,y,1.75*s),(.78*s,.78*s,1.0*s),green,20)

# ---------- vehicle builder ----------
def vehicle(name,color_mat,x,y,z,kind='car',scale=1.0):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root); root.location=(x,y,z)

    # rounded toy proportions: lower body + raised cabin
    body=rounded_cube(name+'_body',(0,0,.68),(1.28,.80,.42),color_mat,.24); body.parent=root
    hood=rounded_cube(name+'_hood',(.86,0,.84),(.52,.72,.26),color_mat,.20); hood.parent=root
    cab=rounded_cube(name+'_cab',(.05,0,1.28),(.72,.70,.55),color_mat,.25); cab.parent=root

    # windshield front panel
    glass=rounded_cube(name+'_glass',(.73,0,1.38),(.055,.56,.34),window,.07); glass.parent=root

    # expressive eyes embedded directly on windshield plane
    for yy in (-.24,.24):
        eye=sphere(name+'_eye'+str(yy),(.805,yy,1.43),(.055,.145,.155),white,20); eye.parent=root
        pupil=sphere(name+'_pupil'+str(yy),(.862,yy,1.43),(.028,.062,.072),black,16); pupil.parent=root
        shine=sphere(name+'_shine'+str(yy),(.887,yy-.025,1.47),(.012,.020,.024),white,12); shine.parent=root

    # friendly bumper-mouth; small enough not to read like a nose
    mouth=sphere(name+'_mouth',(1.34,0,.82),(.055,.26,.075),cream,20); mouth.parent=root
    bumper=rounded_cube(name+'_bumper',(1.39,0,.54),(.09,.64,.09),chrome,.06); bumper.parent=root
    # headlights
    for yy in (-.55,.55):
        h=sphere(name+'_headlight'+str(yy),(1.34,yy,.79),(.08,.10,.09),white,16); h.parent=root

    wheels=[]
    for xx in (-.70,.72):
        for yy in (-.79,.79):
            w=cyl(name+'_wheel',(xx,yy,.36),.35,.25,black,rot=(math.pi/2,0,0),verts=24); w.parent=root; wheels.append(w)
            hub=cyl(name+'_hub',(xx,yy,.36),.16,.265,chrome,rot=(math.pi/2,0,0),verts=20); hub.parent=root

    if kind=='rescue':
        rear=rounded_cube(name+'_rear',(-.78,0,1.10),(.80,.76,.60),color_mat,.18); rear.parent=root
        roof=rounded_cube(name+'_roof',(-.12,0,1.78),(.68,.64,.10),color_mat,.08); roof.parent=root
        l1=rounded_cube(name+'_lightR',(.10,-.22,1.94),(.20,.16,.08),softred,.04); l1.parent=root
        l2=rounded_cube(name+'_lightB',(.10,.22,1.94),(.20,.16,.08),lightblue,.04); l2.parent=root
        # silver rescue side stripe
        stripe=rounded_cube(name+'_stripe',(-.72,-.77,1.08),(.62,.025,.07),white,.02); stripe.parent=root
    elif kind=='dump':
        bed=rounded_cube(name+'_bed',(-.72,0,1.18),(.94,.78,.43),color_mat,.14); bed.parent=root; bed.rotation_euler[1]=math.radians(-6)
    elif kind=='tractor':
        hood2=rounded_cube(name+'_tractorhood',(.62,0,.92),(.72,.60,.28),color_mat,.15); hood2.parent=root

    root['wheels']=[w.name for w in wheels]
    root.scale=(scale,scale,scale)
    return root

# ---------- cast / staging ----------
beep=vehicle('Beep',blue,-5.2,.45,.08,'car',1.0)
reddy=vehicle('Reddy',red,6.3,-.75,.08,'rescue',1.14)
dumpy=vehicle('Dumpy',yellow,4.8,2.35,.05,'dump',.78)
tracto=vehicle('Tracto',green,6.2,3.05,.05,'tractor',.76)

# Beep happily drives in, then sinks and wiggles
key(beep,1,(-5.2,.45,.08))
key(beep,55,(-1.55,.45,.08))
key(beep,80,(-1.42,.45,-.10))
key(beep,112,(-1.42,.45,-.16))
for f,y,z in [(88,.30,-.12),(94,.60,-.17),(100,.32,-.13),(106,.58,-.17)]:
    key(beep,f,(-1.42,y,z))

# Reddy approaches in a separate lane, pauses behind Beep, then tows
key(reddy,68,(6.3,-.75,.08))
key(reddy,142,(1.55,-.75,.08))
key(reddy,164,(1.55,-.75,.08))
key(reddy,232,(5.0,-.75,.08))
key(beep,164,(-1.42,.45,-.16))
key(beep,232,(2.02,.45,.10))

# celebration bounce without overlap
for f,z in [(238,.10),(248,.32),(258,.10),(268,.28),(280,.10)]: key(beep,f,(2.02,.45,z))
for f,z in [(238,.08),(248,.24),(258,.08),(268,.21),(280,.08)]: key(reddy,f,(5.0,-.75,z))

for obj in (beep,reddy): set_interp(obj)

# wheel rotation
for root in (beep,reddy):
    for wn in root['wheels']:
        w=bpy.data.objects[wn]
        w.rotation_euler=(math.pi/2,0,0); w.keyframe_insert('rotation_euler',frame=1)
        w.rotation_euler=(math.pi/2,0,math.radians(1440)); w.keyframe_insert('rotation_euler',frame=232)

# tow rope shown only during towing, angled between lanes
rope=cyl('TowRope',(.10,-.15,.62),.045,3.5,orange,rot=(0,math.pi/2,0),verts=16)
rope.rotation_euler[0]=math.radians(-10)
rope.scale=(1,1,.001); rope.keyframe_insert('scale',frame=146)
rope.scale=(1,1,1); rope.keyframe_insert('scale',frame=160)
rope.location=(.05,-.15,.62); rope.keyframe_insert('location',frame=164)
rope.location=(3.48,-.15,.62); rope.keyframe_insert('location',frame=232)
rope.scale=(1,1,1); rope.keyframe_insert('scale',frame=232)
rope.scale=(1,1,.001); rope.keyframe_insert('scale',frame=238)

# mud splash particles around Beep
for i in range(12):
    sx=-1.42+(i%4-1.5)*.20; sy=.45+((-1)**i)*(.30+.06*(i%3))
    o=sphere('splash'+str(i),(sx,sy,.05),(.08,.08,.13),brown,14)
    o.scale=(.01,.01,.01); o.keyframe_insert('scale',frame=72)
    o.scale=(1,1,1); o.keyframe_insert('scale',frame=86+i%4)
    o.location.z=.55+.10*(i%4); o.keyframe_insert('location',frame=92+i%4)
    o.scale=(.01,.01,.01); o.keyframe_insert('scale',frame=110)

# ---------- camera ----------
bpy.ops.object.camera_add(location=(8.4,-15.2,6.9))
cam=bpy.context.object; scene.camera=cam; cam.data.lens=54
look_at(cam,(-1.2,.15,.95))
cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
# tighter mud reaction shot
cam.location=(6.5,-12.4,5.6); look_at(cam,(-1.25,.25,.95)); cam.keyframe_insert('location',frame=88); cam.keyframe_insert('rotation_euler',frame=88)
# widen for Reddy arrival without covering Beep
cam.location=(8.2,-14.8,6.4); look_at(cam,(.3,-.05,1.0)); cam.keyframe_insert('location',frame=150); cam.keyframe_insert('rotation_euler',frame=150)
# follow tow to the right
cam.location=(9.2,-15.6,6.8); look_at(cam,(2.25,-.05,1.0)); cam.keyframe_insert('location',frame=232); cam.keyframe_insert('rotation_euler',frame=232)
# celebration frame
cam.location=(9.6,-16.4,7.4); look_at(cam,(2.9,-.05,1.0)); cam.keyframe_insert('location',frame=288); cam.keyframe_insert('rotation_euler',frame=288)

# ---------- lighting ----------
bpy.ops.object.light_add(type='SUN', location=(0,0,8)); sun=bpy.context.object
sun.data.energy=2.4; sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-32))
bpy.ops.object.light_add(type='AREA', location=(1.5,-5.5,7.5)); area=bpy.context.object
area.data.energy=1250; area.data.shape='DISK'; area.data.size=8; look_at(area,(0,0,1))
bpy.ops.object.light_add(type='AREA', location=(-4,4,4.8)); fill=bpy.context.object
fill.data.energy=700; fill.data.size=7; look_at(fill,(-1,0,1))
bpy.ops.object.light_add(type='AREA', location=(4,4,6)); rim=bpy.context.object
rim.data.energy=500; rim.data.size=5; look_at(rim,(2,0,1))

scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(0.26,0.55,1.0,1)
bg.inputs['Strength'].default_value=.72
try:
    scene.view_settings.look='AgX - Medium High Contrast'
except Exception:
    pass

bpy.ops.wm.save_as_mainfile(filepath='/tmp/kids_vehicle_scene.blend')
bpy.ops.render.render(animation=True)
print(scene.render.filepath)

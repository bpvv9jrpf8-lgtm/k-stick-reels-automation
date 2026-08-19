import bpy, math, os
from mathutils import Vector

# True modeled-asset motion test using Kenney Car Kit (CC0) geometry.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.frame_start=1; scene.frame_end=72; scene.render.fps=24
scene.render.resolution_x=540; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'; scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath='/tmp/kids-vehicle-kenney-motion.mp4'
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except: scene.render.engine='BLENDER_EEVEE'

# helpers
def mat(name,c,metal=0,rough=.22,emit=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*c,1)
    b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if emit:
        try: b.inputs['Emission Color'].default_value=(*c,1); b.inputs['Emission Strength'].default_value=emit
        except: pass
    return m

def sphere(name,loc,scale,ma,seg=28):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=18, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def rounded_box(name,loc,scale,ma,bevel=.08):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    md=o.modifiers.new('round','BEVEL'); md.width=bevel; md.segments=6; bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def curve(name,pts,ma,bevel=.018):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=bevel; cu.bevel_resolution=4
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(ma); return o

def key(o,f,loc=None,rot=None,sc=None):
    if loc is not None: o.location=loc; o.keyframe_insert('location',frame=f)
    if rot is not None: o.rotation_euler=rot; o.keyframe_insert('rotation_euler',frame=f)
    if sc is not None: o.scale=sc; o.keyframe_insert('scale',frame=f)

def smooth(o):
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for p in fc.keyframe_points: p.interpolation='BEZIER'

def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()

WHITE=mat('EyeWhite',(.99,.995,1),0,.08); BLACK=mat('FaceBlack',(.008,.01,.015),0,.30)
GLASS=mat('FaceGlass',(.04,.32,.72),.05,.10); BLUE=mat('BeepAccent',(.02,.25,.96),.10,.12)
RED=mat('ReddyAccent',(.96,.02,.02),.12,.12); ROAD=mat('Road',(.12,.14,.17),0,.72)
GRASS=mat('Grass',(.16,.60,.11),0,.78); MUD=mat('Mud',(.18,.06,.018),0,.48)

# Import and normalize a modeled asset.
def import_vehicle(path,name,target_length=2.65):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    objs=[o for o in bpy.data.objects if o not in before]
    meshes=[o for o in objs if o.type=='MESH']
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root)
    for o in objs:
        if o.parent is None: o.parent=root
    # world-space bounds before scaling
    corners=[]
    for o in meshes:
        for c in o.bound_box: corners.append(o.matrix_world @ Vector(c))
    mn=Vector((min(v.x for v in corners),min(v.y for v in corners),min(v.z for v in corners)))
    mx=Vector((max(v.x for v in corners),max(v.y for v in corners),max(v.z for v in corners)))
    size=mx-mn
    long=max(size.x,size.y)
    s=target_length/max(long,1e-5); root.scale=(s,s,s)
    # center around origin, place bottom near z=0
    center=(mn+mx)*.5
    for o in objs:
        if o.parent==root: o.location -= center
    # after centering use visual z lift
    root.location.z=.42
    print(name,'size',tuple(round(v,3) for v in size),'objects',[o.name for o in meshes])
    return root, meshes, size

base='car-kit/Models/GLB format'
beep, beep_meshes, beep_size=import_vehicle(os.path.join(base,'sedan.glb'),'Beep',2.55)
reddy, reddy_meshes, reddy_size=import_vehicle(os.path.join(base,'firetruck.glb'),'Reddy',3.15)

# Car-kit vehicles are modeled lengthwise on X. If imported orientation differs, visual QA will catch it.
# Add glossy character face elements slightly ahead of the +X front, parented to each vehicle.
def add_face(root,is_rescue=False):
    fx=1.37 if not is_rescue else 1.64
    z=1.12 if not is_rescue else 1.34
    width=.46 if not is_rescue else .54
    panel=rounded_box(root.name+'_facepanel',(fx,0,z),(.045,width,.26),GLASS,.06); panel.parent=root
    pupils=[]
    for yy in (-width*.43,width*.43):
        e=sphere(root.name+'_eye'+str(yy),(fx+.065,yy,z+.03),(.045,.12,.14),WHITE,24); e.parent=root
        p=sphere(root.name+'_pupil'+str(yy),(fx+.105,yy,z+.02),(.024,.048,.064),BLACK,18); p.parent=root; pupils.append(p)
        sh=sphere(root.name+'_shine'+str(yy),(fx+.123,yy-.018,z+.065),(.009,.014,.017),WHITE,12); sh.parent=root
    smile=curve(root.name+'_smile',[(fx+.09,-.18,z-.24),(fx+.12,0,z-.29),(fx+.09,.18,z-.24)],BLACK,.018); smile.parent=root
    root['pupils']=[p.name for p in pupils]
    return root

add_face(beep,False); add_face(reddy,True)
beep.location=(-3.3,.28,.40); reddy.location=(4.9,-.66,.40)

# environment
rounded_box('ground',(0,0,-.92),(9,9,.45),GRASS,.04); rounded_box('road',(0,0,-.28),(8.6,3.0,.14),ROAD,.04)
sphere('mudpool',(-.45,.28,-.09),(1.55,1.10,.15),MUD,32)
for x in (-5,-1.7,1.6,4.9): rounded_box('mark'+str(x),(x,-2.55,-.09),(.65,.045,.018),WHITE,.014)

# 3-second story motion
key(beep,1,(-3.3,.28,.40)); key(beep,26,(-1.15,.28,.46)); key(beep,38,(-.48,.28,.26)); key(beep,52,(-.48,.28,.22)); key(beep,72,(-.48,.28,.28))
key(reddy,1,(4.9,-.66,.40)); key(reddy,35,(4.9,-.66,.40)); key(reddy,64,(2.18,-.66,.42)); key(reddy,72,(2.18,-.66,.42))
# subtle body reaction
key(beep,38,rot=(0,math.radians(-3),math.radians(2))); key(beep,48,rot=(0,math.radians(2),math.radians(-2))); key(beep,60,rot=(0,0,0));
for pn in beep['pupils']:
    p=bpy.data.objects[pn]; key(p,1,sc=(1,1,1)); key(p,38,sc=(1.45,1.45,1.45)); key(p,66,sc=(1.08,1.08,1.08)); key(p,72,sc=(1,1,1))

# splash particles
for i in range(14):
    a=i/14*math.tau; x=-.48+math.cos(a)*(.18+.05*(i%4)); y=.28+math.sin(a)*(.14+.04*(i%3))
    d=sphere('muddrop'+str(i),(x,y,-.02),(.035,.035,.065),MUD,10)
    key(d,28,sc=(.01,.01,.01)); key(d,36,sc=(1,1,1)); key(d,44,loc=(x,y,.34+.07*(i%4))); key(d,54,sc=(.01,.01,.01))

smooth(beep); smooth(reddy)

# camera
bpy.ops.object.camera_add(location=(8.7,-15.3,5.9)); cam=bpy.context.object; scene.camera=cam; cam.data.lens=58
look_at(cam,(-.3,-.02,.92)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(7.5,-12.7,5.0); look_at(cam,(.1,-.05,.98)); cam.keyframe_insert('location',frame=40); cam.keyframe_insert('rotation_euler',frame=40)
cam.location=(8.2,-13.6,5.2); look_at(cam,(.65,-.08,1.0)); cam.keyframe_insert('location',frame=72); cam.keyframe_insert('rotation_euler',frame=72)
try: cam.data.dof.use_dof=True; cam.data.dof.focus_object=beep; cam.data.dof.aperture_fstop=5.6
except: pass

# lighting
bpy.ops.object.light_add(type='SUN',location=(0,0,8)); sun=bpy.context.object; sun.data.energy=2.0; sun.rotation_euler=(math.radians(24),math.radians(-26),math.radians(-30))
for loc,en,size,target in [((1,-5,7),1250,7,(0,0,1)),((-4,4,5),720,6,(-.5,0,1)),((5,3,6),560,5,(2,0,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=en; l.data.size=size; look_at(l,target)
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.22,.52,.95,1); bg.inputs['Strength'].default_value=.70
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass

bpy.ops.wm.save_as_mainfile(filepath='/tmp/kids_vehicle_kenney_asset_test.blend')
bpy.ops.render.render(animation=True)
print(scene.render.filepath)

import bpy, math
from mathutils import Vector

# 3-second visual-lock motion test. No voice, no upload, no long render.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.frame_start=1; scene.frame_end=72; scene.render.fps=24
scene.render.resolution_x=540; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'; scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath='/tmp/kids-vehicle-premium-motion.mp4'
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except: scene.render.engine='BLENDER_EEVEE'

# ---------- helpers ----------
def mat(name,c,metal=0.0,rough=.22,emit=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*c,1)
    b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if emit>0:
        try:
            b.inputs['Emission Color'].default_value=(*c,1); b.inputs['Emission Strength'].default_value=emit
        except: pass
    return m

def rounded_box(name,loc,scale,ma,bevel=.16):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bev=o.modifiers.new('soft_edges','BEVEL'); bev.width=bevel; bev.segments=8
    bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def sphere(name,loc,scale,ma,seg=36):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=24, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def cyl(name,loc,r,depth,ma,rot=(math.pi/2,0,0),verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def curve(name,pts,ma,bevel=.025):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=bevel; cu.bevel_resolution=5
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(ma); return o

def key(o,f,loc=None,rot=None,sc=None):
    if loc is not None: o.location=loc; o.keyframe_insert('location',frame=f)
    if rot is not None: o.rotation_euler=rot; o.keyframe_insert('rotation_euler',frame=f)
    if sc is not None: o.scale=sc; o.keyframe_insert('scale',frame=f)

def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()

def smooth_anim(o):
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for p in fc.keyframe_points: p.interpolation='BEZIER'

# ---------- palette ----------
BLUE=mat('BeepBlue',(0.025,.26,.96),.10,.12)
RED=mat('ReddyRed',(.96,.018,.018),.12,.13)
BLACK=mat('TireBlack',(.008,.010,.014),0,.30)
WHITE=mat('EyeWhite',(.99,.995,1),0,.08)
GLASS=mat('Glass',(.055,.38,.74),.10,.09)
CHROME=mat('Chrome',(.72,.80,.92),.78,.09)
ROAD=mat('Road',(.12,.14,.17),0,.68)
GRASS=mat('Grass',(.18,.61,.11),0,.72)
MUD=mat('Mud',(.17,.055,.018),0,.47)
YELLOW=mat('LampYellow',(1,.68,.05),.04,.10,1.5)
LBLUE=mat('LightBlue',(.02,.45,1),.04,.08,1.0)
LRED=mat('LightRed',(1,.02,.02),.04,.08,1.0)

# ---------- reusable character asset ----------
def make_vehicle(name,color,kind='car'):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root)

    # Distinct rounded body panels rather than one generic blob.
    body=rounded_box(name+'_body',(0,0,.74),(1.24,.78,.42),color,.28); body.parent=root
    nose=rounded_box(name+'_nose',(.92,0,.79),(.48,.70,.30),color,.23); nose.parent=root
    lower=rounded_box(name+'_lower',(.18,0,.47),(1.18,.76,.18),color,.20); lower.parent=root
    cabin=rounded_box(name+'_cabin',(-.20,0,1.24),(.68,.67,.53),color,.30); cabin.parent=root

    # Windshield face panel with thick expressive eye forms.
    windshield=rounded_box(name+'_windshield',(.49,0,1.33),(.07,.57,.31),GLASS,.12); windshield.parent=root
    pupils=[]; eyes=[]
    for yy in (-.235,.235):
        e=sphere(name+'_eye'+str(yy),(.575,yy,1.38),(.050,.155,.175),WHITE,28); e.parent=root; eyes.append(e)
        p=sphere(name+'_pupil'+str(yy),(.622,yy,1.365),(.026,.060,.077),BLACK,22); p.parent=root; pupils.append(p)
        shine=sphere(name+'_shine'+str(yy),(.640,yy-.025,1.410),(.010,.018,.022),WHITE,14); shine.parent=root

    smile=curve(name+'_smile',[(1.39,-.20,.76),(1.44,0,.70),(1.39,.20,.76)],BLACK,.024); smile.parent=root
    bumper=rounded_box(name+'_bumper',(1.37,0,.48),(.07,.59,.065),CHROME,.055); bumper.parent=root
    grille=rounded_box(name+'_grille',(1.385,0,.62),(.038,.30,.09),BLACK,.035); grille.parent=root
    for yy in (-.49,.49):
        lamp=sphere(name+'_lamp'+str(yy),(1.34,yy,.77),(.066,.080,.074),YELLOW,18); lamp.parent=root

    wheels=[]
    for xx in (-.66,.70):
        for yy in (-.80,.80):
            tire=cyl(name+'_wheel_'+str(xx)+'_'+str(yy),(xx,yy,.35),.34,.25,BLACK,(math.pi/2,0,0),36); tire.parent=root; wheels.append(tire)
            hub=cyl(name+'_hub_'+str(xx)+'_'+str(yy),(xx,yy,.35),.145,.27,CHROME,(math.pi/2,0,0),28); hub.parent=root
            ring=cyl(name+'_ring_'+str(xx)+'_'+str(yy),(xx,yy,.35),.235,.273,BLACK,(math.pi/2,0,0),32); ring.parent=root

    if kind=='rescue':
        rear=rounded_box(name+'_rear',(-.88,0,1.03),(.74,.70,.56),color,.27); rear.parent=root
        roof=rounded_box(name+'_roof',(-.15,0,1.79),(.64,.55,.07),color,.07); roof.parent=root
        lr=rounded_box(name+'_lightR',(.00,-.19,1.92),(.16,.12,.07),LRED,.035); lr.parent=root
        lb=rounded_box(name+'_lightB',(.00,.19,1.92),(.16,.12,.07),LBLUE,.035); lb.parent=root
        rail1=cyl(name+'_rail1',(-.80,-.31,1.67),.022,1.18,CHROME,(0,math.pi/2,0),16); rail1.parent=root
        rail2=cyl(name+'_rail2',(-.80,.31,1.67),.022,1.18,CHROME,(0,math.pi/2,0),16); rail2.parent=root
        for xx in (-1.17,-.90,-.63,-.36):
            rung=cyl(name+'_rung'+str(xx),(xx,0,1.67),.018,.62,CHROME,(math.pi/2,0,0),14); rung.parent=root

    root['wheels']=[w.name for w in wheels]; root['pupils']=[p.name for p in pupils]
    return root

beep=make_vehicle('Beep',BLUE,'car'); reddy=make_vehicle('Reddy',RED,'rescue')
beep.location=(-3.7,.25,.02); reddy.location=(4.7,-.60,.02)

# ---------- minimal environment ----------
rounded_box('ground',(0,0,-.92),(9,9,.45),GRASS,.04)
rounded_box('road',(0,0,-.28),(8.5,3.0,.14),ROAD,.04)
sphere('mudpool',(-.55,.28,-.10),(1.65,1.15,.16),MUD,36)
for x in (-5.2,-1.5,2.2,5.9): rounded_box('mark'+str(x),(x,-2.55,-.09),(.70,.045,.018),WHITE,.015)

# ---------- 3-second motion ----------
# Beep drives, sinks slightly, reacts; Reddy rolls in and stops to help.
key(beep,1,(-3.7,.25,.02)); key(beep,18,(-1.55,.25,.10)); key(beep,34,(-.60,.25,-.10)); key(beep,48,(-.60,.25,-.14)); key(beep,72,(-.60,.25,-.10))
key(reddy,1,(4.7,-.60,.02)); key(reddy,30,(4.7,-.60,.02)); key(reddy,58,(1.95,-.60,.08)); key(reddy,72,(1.95,-.60,.08))
for f,z in [(1,.02),(10,.10),(18,.02),(26,.09),(34,-.10),(42,-.14),(50,-.09),(58,-.14),(66,-.10),(72,-.10)]:
    key(beep,f,(beep.location.x if f==72 else (-3.7 + min(f,34)/34*3.1),.25,z))
# overwrite the important poses after bounce helper
key(beep,34,(-.60,.25,-.10)); key(beep,48,(-.60,.25,-.14)); key(beep,72,(-.60,.25,-.10))

# Pupils widen as Beep notices the mud, then relax when Reddy arrives.
for pn in beep['pupils']:
    p=bpy.data.objects[pn]; key(p,1,sc=(1,1,1)); key(p,34,sc=(1.42,1.42,1.42)); key(p,60,sc=(1.15,1.15,1.15)); key(p,72,sc=(1,1,1))

# Wheel rotation + subtle suspension body movement.
for root in (beep,reddy):
    for wn in root['wheels']:
        w=bpy.data.objects[wn]; w.rotation_euler=(math.pi/2,0,0); w.keyframe_insert('rotation_euler',frame=1)
        w.rotation_euler=(math.pi/2,0,math.radians(720)); w.keyframe_insert('rotation_euler',frame=72)

# Mud splashes around Beep.
for i in range(12):
    a=(i/12)*math.tau; x=-.60+math.cos(a)*(.20+.07*(i%3)); y=.25+math.sin(a)*(.16+.05*(i%4))
    d=sphere('splash'+str(i),(x,y,-.02),(.04,.04,.07),MUD,12)
    key(d,22,sc=(.01,.01,.01)); key(d,31,sc=(1,1,1)); key(d,42,loc=(x,y,.35+.06*(i%4))); key(d,52,sc=(.01,.01,.01))

for o in (beep,reddy): smooth_anim(o)

# ---------- camera / lighting ----------
bpy.ops.object.camera_add(location=(8.4,-14.8,5.6)); cam=bpy.context.object; scene.camera=cam; cam.data.lens=58
look_at(cam,(-.4,.0,.92)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(7.4,-12.4,4.9); look_at(cam,(-.10,.0,.98)); cam.keyframe_insert('location',frame=38); cam.keyframe_insert('rotation_euler',frame=38)
cam.location=(8.0,-13.3,5.1); look_at(cam,(.55,-.05,1.0)); cam.keyframe_insert('location',frame=72); cam.keyframe_insert('rotation_euler',frame=72)
try:
    cam.data.dof.use_dof=True; cam.data.dof.focus_object=beep; cam.data.dof.aperture_fstop=5.0
except: pass

bpy.ops.object.light_add(type='SUN',location=(0,0,8)); sun=bpy.context.object; sun.data.energy=2.0; sun.rotation_euler=(math.radians(22),math.radians(-24),math.radians(-30))
for loc,en,size,target in [((1,-5,7),1200,7,(0,0,1)),((-4,4,5),700,6,(-.5,0,1)),((5,3,6),550,5,(2,0,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=en; l.data.size=size; look_at(l,target)
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.22,.52,.95,1); bg.inputs['Strength'].default_value=.70
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass

bpy.ops.wm.save_as_mainfile(filepath='/tmp/kids_vehicle_premium_asset_test.blend')
bpy.ops.render.render(animation=True)
print(scene.render.filepath)

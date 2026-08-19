import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.frame_start=1; scene.frame_end=288; scene.render.fps=24
scene.render.resolution_x=720; scene.render.resolution_y=1280; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'; scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath='/tmp/kids-vehicle-3d.mp4'
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except: scene.render.engine='BLENDER_EEVEE'

# ---------- helpers ----------
def mat(name,c,metal=0,rough=.22):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    return m

def sph(name,loc,sc,ma,seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=20, location=loc)
    o=bpy.context.object; o.name=name; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def rc(name,loc,sc,ma,bev=.18):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    md=o.modifiers.new('round','BEVEL'); md.width=bev; md.segments=7; bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def cyl(name,loc,r,depth,ma,rot=(math.pi/2,0,0),verts=28):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def curve_line(name, pts, ma, bevel=.025):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=bevel; cu.bevel_resolution=5
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for bp,co in zip(sp.bezier_points,pts):
        bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(obj); obj.data.materials.append(ma); return obj

def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def key(o,f,loc=None,rot=None,sc=None):
    if loc is not None: o.location=loc; o.keyframe_insert('location',frame=f)
    if rot is not None: o.rotation_euler=rot; o.keyframe_insert('rotation_euler',frame=f)
    if sc is not None: o.scale=sc; o.keyframe_insert('scale',frame=f)

def smooth(o):
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for p in fc.keyframe_points: p.interpolation='BEZIER'

# ---------- materials ----------
BLUE=mat('BeepBlue',(.018,.30,.98),.08,.14); RED=mat('ReddyRed',(.98,.025,.025),.10,.15)
BLACK=mat('Black',(.008,.010,.015),0,.34); WHITE=mat('White',(.985,.995,1),0,.10)
GLASS=mat('Windshield',(.08,.52,.92),.16,.08); CHROME=mat('Chrome',(.76,.82,.92),.72,.10)
GRASS=mat('Grass',(.19,.64,.12),0,.82); ROAD=mat('Road',(.13,.15,.18),0,.76); MUD=mat('Mud',(.20,.055,.015),0,.52)
ORANGE=mat('TowOrange',(1,.24,.01),.04,.18); YELLOW=mat('DumpyYellow',(1,.68,.02),.03,.18); GREEN=mat('TractoGreen',(.08,.58,.10),.03,.20)
LBLUE=mat('LightBlue',(.02,.55,1),.04,.10); LRED=mat('LightRed',(1,.03,.03),.04,.10)

# ---------- world ----------
rc('ground',(0,0,-.95),(11,11,.48),GRASS,.04); rc('road',(0,0,-.30),(10,3.15,.14),ROAD,.04)
for x in (-6,-2,2,6):
    rc('roadmarkA'+str(x),(x,-2.68,-.10),(.78,.055,.022),WHITE,.015)
    rc('roadmarkB'+str(x),(x,2.68,-.10),(.78,.055,.022),WHITE,.015)
sph('mud',(-1.5,.42,-.08),(2.25,1.55,.20),MUD,36)
for i,(x,y,s) in enumerate([(-6,4,1),(-4.5,4.7,.8),(6,4.2,1),(7.5,4.7,.78),(-7,-4,.7),(6.8,-3.8,.9)]):
    cyl('tr'+str(i),(x,y,.4),.15*s,1.6*s,MUD,(0,0,0),18); sph('leaf'+str(i),(x,y,1.7*s),(.76*s,.76*s,1.02*s),GREEN,24)

# ---------- premium character vehicle ----------
def car(name,color,pos,scale=1,kind='car'):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root); root.location=pos; root.scale=(scale,scale,scale)

    # Compact toy proportions with a clean silhouette.
    body=sph(name+'_body',(0,0,.72),(1.30,.84,.48),color,36); body.parent=root
    hood=sph(name+'_hood',(.88,0,.80),(.66,.73,.32),color,34); hood.parent=root
    cabin=sph(name+'_cabin',(-.05,0,1.28),(.76,.70,.60),color,34); cabin.parent=root

    # Large front windshield so the face reads clearly at phone size.
    glass=rc(name+'_glass',(.68,0,1.40),(.060,.60,.36),GLASS,.11); glass.parent=root
    pupils=[]
    for yy in (-.245,.245):
        e=sph(name+'_eye'+str(yy),(.755,yy,1.445),(.052,.165,.185),WHITE,26); e.parent=root
        p=sph(name+'_pupil'+str(yy),(.810,yy,1.440),(.030,.068,.084),BLACK,20); p.parent=root; pupils.append(p)
        sh=sph(name+'_shine'+str(yy),(.835,yy-.028,1.495),(.012,.021,.026),WHITE,14); sh.parent=root

    # Thin curved smile instead of a blob mouth.
    smile=curve_line(name+'_smile',[(1.405,-.24,.84),(1.445,0,.74),(1.405,.24,.84)],BLACK,.025); smile.parent=root
    bumper=rc(name+'_bumper',(1.43,0,.52),(.08,.62,.075),CHROME,.055); bumper.parent=root
    for yy in (-.54,.54):
        h=sph(name+'_lamp'+str(yy),(1.35,yy,.79),(.075,.095,.090),WHITE,18); h.parent=root

    wheels=[]
    for xx in (-.68,.70):
        for yy in (-.83,.83):
            w=cyl(name+'_wheel',(xx,yy,.34),.36,.26,BLACK,(math.pi/2,0,0),30); w.parent=root; wheels.append(w)
            h=cyl(name+'_hub',(xx,yy,.34),.16,.275,CHROME,(math.pi/2,0,0),24); h.parent=root

    if kind=='rescue':
        rear=sph(name+'_rear',(-.85,0,1.10),(.88,.77,.62),color,32); rear.parent=root
        roof=rc(name+'_roof',(-.16,0,1.84),(.66,.58,.08),color,.07); roof.parent=root
        l1=rc(name+'_lr',(.10,-.21,1.98),(.17,.13,.07),LRED,.035); l1.parent=root
        l2=rc(name+'_lb',(.10,.21,1.98),(.17,.13,.07),LBLUE,.035); l2.parent=root
        # simple ladder silhouette for immediate rescue-truck identity
        for yy in (-.32,.32):
            rail=cyl(name+'_ladderrail'+str(yy),(-.88,yy,1.75),.025,1.20,CHROME,(0,math.pi/2,0),16); rail.parent=root
        for xx in (-1.25,-.95,-.65,-.35):
            rung=cyl(name+'_rung'+str(xx),(xx,0,1.75),.020,.66,CHROME,(math.pi/2,0,0),14); rung.parent=root

    root['wheels']=[w.name for w in wheels]; root['pupils']=[p.name for p in pupils]
    return root

beep=car('Beep',BLUE,(-5.2,.42,.08),1.0,'car')
reddy=car('Reddy',RED,(6.2,-.68,.08),1.03,'rescue')
helper1=car('Dumpy',YELLOW,(5.2,2.30,.05),.62,'car'); helper2=car('Tracto',GREEN,(6.6,3.00,.05),.60,'car')

# ---------- story ----------
key(beep,1,(-5.2,.42,.08)); key(beep,30,(-3.5,.42,.15)); key(beep,56,(-1.55,.42,.08)); key(beep,80,(-1.45,.42,-.10)); key(beep,112,(-1.45,.42,-.17))
for f,y,z,r in [(86,.30,-.12,-.06),(92,.58,-.17,.06),(98,.31,-.13,-.05),(104,.57,-.17,.05),(110,.42,-.17,0)]: key(beep,f,(-1.45,y,z),(0,r,0))
key(reddy,68,(6.2,-.68,.08)); key(reddy,112,(3.8,-.68,.12)); key(reddy,145,(1.90,-.68,.08)); key(reddy,164,(1.90,-.68,.08)); key(reddy,232,(5.0,-.68,.08))
key(beep,164,(-1.45,.42,-.17)); key(beep,232,(2.15,.42,.10))
for f,z in [(238,.10),(248,.34),(258,.10),(268,.30),(280,.10)]: key(beep,f,(2.15,.42,z))
for f,z in [(238,.08),(248,.23),(258,.08),(268,.20),(280,.08)]: key(reddy,f,(5.0,-.68,z))
smooth(beep); smooth(reddy)

# Wheel spin.
for root in (beep,reddy):
    for wn in root['wheels']:
        w=bpy.data.objects[wn]; w.rotation_euler=(math.pi/2,0,0); w.keyframe_insert('rotation_euler',frame=1)
        w.rotation_euler=(math.pi/2,0,math.radians(1900)); w.keyframe_insert('rotation_euler',frame=232)

# Beep reacts: pupils enlarge when stuck, then relax after rescue.
for pn in beep['pupils']:
    p=bpy.data.objects[pn]; key(p,60,sc=(1,1,1)); key(p,88,sc=(1.35,1.35,1.35)); key(p,230,sc=(1,1,1))

# Tow hook and rope.
hook=rc('hook',(1.55,-.18,.58),(.09,.11,.08),CHROME,.04); key(hook,145,sc=(.01,.01,.01)); key(hook,160,sc=(1,1,1)); key(hook,238,sc=(.01,.01,.01))
rope=cyl('rope',(.20,-.11,.61),.043,3.55,ORANGE,(0,math.pi/2,0),18); rope.rotation_euler[0]=math.radians(-8)
key(rope,145,sc=(1,1,.001)); key(rope,160,sc=(1,1,1)); key(rope,164,loc=(.15,-.11,.61)); key(rope,232,loc=(3.58,-.11,.61)); key(rope,238,sc=(1,1,.001))

# Rich but light-weight mud droplets.
for i in range(20):
    a=(i/20)*math.tau; rr=.22+.18*(i%5); x=-1.45+math.cos(a)*rr; y=.42+math.sin(a)*rr*.72
    o=sph('muddrop'+str(i),(x,y,.03),(.055+.01*(i%3),.055+.01*(i%3),.10+.02*(i%4)),MUD,12)
    key(o,72,sc=(.01,.01,.01)); key(o,84+i%5,sc=(1,1,1)); key(o,92+i%5,loc=(x,y,.50+.11*(i%5))); key(o,112,sc=(.01,.01,.01))

# ---------- camera: front three-quarter framing that keeps both faces visible ----------
bpy.ops.object.camera_add(location=(10.5,-17.5,7.2)); cam=bpy.context.object; scene.camera=cam; cam.data.lens=55
look_at(cam,(-2.0,.15,1.0)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(7.1,-12.6,5.1); look_at(cam,(-1.42,.42,1.05)); cam.keyframe_insert('location',frame=88); cam.keyframe_insert('rotation_euler',frame=88)
cam.location=(10.4,-17.0,6.8); look_at(cam,(.25,-.02,1.05)); cam.keyframe_insert('location',frame=150); cam.keyframe_insert('rotation_euler',frame=150)
cam.location=(10.8,-18.0,7.0); look_at(cam,(1.15,-.02,1.00)); cam.keyframe_insert('location',frame=188); cam.keyframe_insert('rotation_euler',frame=188)
cam.location=(11.4,-19.2,7.5); look_at(cam,(2.5,-.03,1.0)); cam.keyframe_insert('location',frame=232); cam.keyframe_insert('rotation_euler',frame=232)
cam.location=(12.0,-20.0,7.8); look_at(cam,(3.0,-.03,1.0)); cam.keyframe_insert('location',frame=288); cam.keyframe_insert('rotation_euler',frame=288)

# ---------- lighting ----------
bpy.ops.object.light_add(type='SUN',location=(0,0,8)); sun=bpy.context.object; sun.data.energy=2.1; sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-32))
for loc,en,size,target in [((1.5,-5.5,7.5),1350,8,(0,0,1)),((-4,4,5),780,7,(-1,0,1)),((5,4,6),580,5,(2,0,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=en; l.data.size=size; look_at(l,target)
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.25,.56,1,1); bg.inputs['Strength'].default_value=.78
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass

bpy.ops.wm.save_as_mainfile(filepath='/tmp/kids_vehicle_scene_v5.blend')
bpy.ops.render.render(animation=True)
print(scene.render.filepath)

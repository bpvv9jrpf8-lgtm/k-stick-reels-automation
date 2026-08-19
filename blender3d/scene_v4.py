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
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*c,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    return m

def sph(name,loc,sc,ma,seg=28):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=18, location=loc)
    o=bpy.context.object; o.name=name; o.scale=sc; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def rc(name,loc,sc,ma,bev=.18):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=sc; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    md=o.modifiers.new('round','BEVEL'); md.width=bev; md.segments=6; bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def cyl(name,loc,r,depth,ma,rot=(math.pi/2,0,0),verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=name; bpy.ops.object.shade_smooth(); o.data.materials.append(ma); return o

def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def key(o,f,loc=None,rot=None,sc=None):
    if loc is not None: o.location=loc; o.keyframe_insert('location',frame=f)
    if rot is not None: o.rotation_euler=rot; o.keyframe_insert('rotation_euler',frame=f)
    if sc is not None: o.scale=sc; o.keyframe_insert('scale',frame=f)

def smooth(o):
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for p in fc.keyframe_points: p.interpolation='BEZIER'

BLUE=mat('blue',(.02,.30,.98),.08,.15); RED=mat('red',(.98,.03,.03),.1,.16); BLACK=mat('black',(.008,.01,.015),0,.34)
WHITE=mat('white',(.98,.99,1),0,.12); GLASS=mat('glass',(.10,.60,.96),.14,.10); CHROME=mat('chrome',(.74,.8,.9),.7,.1)
GRASS=mat('grass',(.18,.62,.12),0,.8); ROAD=mat('road',(.13,.15,.18),0,.76); MUD=mat('mud',(.20,.055,.015),0,.55)
ORANGE=mat('rope',(1,.23,.01),.04,.2); YELLOW=mat('yellow',(1,.68,.02),.03,.2); GREEN=mat('green',(.08,.58,.1),.03,.22)

# ---------- world ----------
rc('ground',(0,0,-.95),(11,11,.48),GRASS,.04); rc('road',(0,0,-.3),(10,3.15,.14),ROAD,.04)
sph('mud',(-1.5,.4,-.08),(2.25,1.55,.22),MUD,32)
for i,(x,y,s) in enumerate([(-6,4,1),(-4.5,4.7,.8),(6,4.2,1),(7.5,4.7,.78),(-7,-4,.7),(6.8,-3.8,.9)]):
    cyl('tr'+str(i),(x,y,.4),.15*s,1.6*s,MUD,(0,0,0),16); sph('leaf'+str(i),(x,y,1.7*s),(.75*s,.75*s,1.0*s),GREEN,20)

# ---------- premium toy car builder ----------
def car(name,color,pos,scale=1,kind='car'):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root); root.location=pos; root.scale=(scale,scale,scale)
    # oval shell makes silhouette less boxy
    body=sph(name+'_body',(0,0,.72),(1.35,.86,.50),color,32); body.parent=root
    hood=sph(name+'_hood',(.86,0,.80),(.72,.76,.34),color,30); hood.parent=root
    cabin=sph(name+'_cabin',(-.02,0,1.28),(.78,.72,.62),color,30); cabin.parent=root
    # curved-look windshield slab
    glass=rc(name+'_glass',(.68,0,1.40),(.055,.56,.33),GLASS,.10); glass.parent=root
    pupils=[]; brows=[]
    for yy in (-.23,.23):
        e=sph(name+'_eye'+str(yy),(.755,yy,1.45),(.05,.15,.17),WHITE,22); e.parent=root
        p=sph(name+'_pupil'+str(yy),(.803,yy,1.45),(.028,.061,.075),BLACK,18); p.parent=root; pupils.append(p)
        sh=sph(name+'_shine'+str(yy),(.826,yy-.025,1.49),(.011,.019,.023),WHITE,12); sh.parent=root
        b=rc(name+'_brow'+str(yy),(.81,yy,1.64),(.018,.13,.021),BLACK,.02); b.parent=root; brows.append(b)
    mouth=sph(name+'_mouth',(1.38,0,.82),(.045,.24,.07),BLACK,20); mouth.parent=root
    bumper=rc(name+'_bumper',(1.42,0,.52),(.08,.62,.075),CHROME,.055); bumper.parent=root
    wheels=[]
    for xx in (-.67,.70):
        for yy in (-.84,.84):
            w=cyl(name+'_wheel',(xx,yy,.34),.36,.26,BLACK,(math.pi/2,0,0),28); w.parent=root; wheels.append(w)
            h=cyl(name+'_hub',(xx,yy,.34),.16,.275,CHROME,(math.pi/2,0,0),22); h.parent=root
    if kind=='rescue':
        rear=sph(name+'_rear',(-.86,0,1.08),(.92,.78,.64),color,28); rear.parent=root
        roof=rc(name+'_roof',(-.12,0,1.84),(.64,.58,.08),color,.07); roof.parent=root
        l1=rc(name+'_lr',(.12,-.2,1.98),(.17,.13,.07),RED,.035); l1.parent=root
        l2=rc(name+'_lb',(.12,.2,1.98),(.17,.13,.07),BLUE,.035); l2.parent=root
    root['wheels']=[w.name for w in wheels]; root['pupils']=[p.name for p in pupils]; root['brows']=[b.name for b in brows]; root['mouth']=mouth.name
    return root

beep=car('Beep',BLUE,(-5.2,.42,.08),1.0,'car'); reddy=car('Reddy',RED,(6.4,-.78,.08),1.13,'rescue')
# background helpers
helper1=car('Dumpy',YELLOW,(5.2,2.25,.05),.70,'car'); helper2=car('Tracto',GREEN,(6.6,3.0,.05),.68,'car')

# ---------- story ----------
key(beep,1,(-5.2,.42,.08)); key(beep,30,(-3.5,.42,.15)); key(beep,56,(-1.55,.42,.08)); key(beep,80,(-1.45,.42,-.10)); key(beep,112,(-1.45,.42,-.17))
for f,y,z,r in [(86,.30,-.12,-.06),(92,.58,-.17,.06),(98,.31,-.13,-.05),(104,.57,-.17,.05),(110,.42,-.17,0)]: key(beep,f,(-1.45,y,z),(0,r,0))
key(reddy,68,(6.4,-.78,.08)); key(reddy,112,(3.7,-.78,.14)); key(reddy,145,(1.65,-.78,.08)); key(reddy,164,(1.65,-.78,.08)); key(reddy,232,(5.0,-.78,.08))
key(beep,164,(-1.45,.42,-.17)); key(beep,232,(2.05,.42,.10))
for f,z in [(238,.10),(248,.34),(258,.10),(268,.30),(280,.10)]: key(beep,f,(2.05,.42,z))
for f,z in [(238,.08),(248,.24),(258,.08),(268,.21),(280,.08)]: key(reddy,f,(5.0,-.78,z))
smooth(beep); smooth(reddy)

# suspension + wheel spin
for root in (beep,reddy):
    for wn in root['wheels']:
        w=bpy.data.objects[wn]; w.rotation_euler=(math.pi/2,0,0); w.keyframe_insert('rotation_euler',frame=1)
        w.rotation_euler=(math.pi/2,0,math.radians(1900)); w.keyframe_insert('rotation_euler',frame=232)

# eye and mouth emotion
for pn in beep['pupils']:
    p=bpy.data.objects[pn]; key(p,60,sc=(1,1,1)); key(p,88,sc=(1.28,1.28,1.28)); key(p,230,sc=(1,1,1))
for bn in beep['brows']:
    b=bpy.data.objects[bn]; key(b,60,rot=(0,0,0)); key(b,90,rot=(math.radians(20),0,0)); key(b,230,rot=(0,0,0))
m=bpy.data.objects[beep['mouth']]; key(m,60,sc=(1,1,1)); key(m,90,sc=(1,1.30,1.45)); key(m,230,sc=(1,.90,.75))

# tow hook + rope
hook=rc('hook',(1.39,-.30,.57),(.09,.11,.08),CHROME,.04); key(hook,145,sc=(.01,.01,.01)); key(hook,160,sc=(1,1,1)); key(hook,238,sc=(.01,.01,.01))
rope=cyl('rope',(.15,-.15,.61),.043,3.55,ORANGE,(0,math.pi/2,0),18); rope.rotation_euler[0]=math.radians(-10)
key(rope,145,sc=(1,1,.001)); key(rope,160,sc=(1,1,1)); key(rope,164,loc=(.08,-.15,.61)); key(rope,232,loc=(3.50,-.15,.61)); key(rope,238,sc=(1,1,.001))

# mud droplets + front splash wave
for i in range(24):
    a=(i/24)*math.tau; rr=.22+.18*(i%5); x=-1.45+math.cos(a)*rr; y=.42+math.sin(a)*rr*.75
    o=sph('muddrop'+str(i),(x,y,.03),(.055+.01*(i%3),.055+.01*(i%3),.10+.02*(i%4)),MUD,12)
    key(o,72,sc=(.01,.01,.01)); key(o,84+i%5,sc=(1,1,1)); key(o,92+i%5,loc=(x,y,.50+.11*(i%5))); key(o,112,sc=(.01,.01,.01))

# ---------- camera ----------
bpy.ops.object.camera_add(location=(8.5,-15,6.5)); cam=bpy.context.object; scene.camera=cam; cam.data.lens=58
look_at(cam,(-2,.2,1)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(5.6,-10.2,4.5); look_at(cam,(-1.42,.4,1.05)); cam.keyframe_insert('location',frame=88); cam.keyframe_insert('rotation_euler',frame=88)
cam.location=(7.7,-13.4,5.7); look_at(cam,(.15,-.05,1.05)); cam.keyframe_insert('location',frame=150); cam.keyframe_insert('rotation_euler',frame=150)
cam.location=(6.0,-11.2,4.7); look_at(cam,(1.0,-.05,.95)); cam.keyframe_insert('location',frame=188); cam.keyframe_insert('rotation_euler',frame=188)
cam.location=(9.0,-15.4,6.5); look_at(cam,(2.3,-.05,1)); cam.keyframe_insert('location',frame=232); cam.keyframe_insert('rotation_euler',frame=232)
cam.location=(9.5,-16.1,7.0); look_at(cam,(2.9,-.05,1)); cam.keyframe_insert('location',frame=288); cam.keyframe_insert('rotation_euler',frame=288)

# ---------- lighting ----------
bpy.ops.object.light_add(type='SUN',location=(0,0,8)); sun=bpy.context.object; sun.data.energy=2.2; sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-32))
for loc,en,size,target in [((1.5,-5.5,7.5),1300,8,(0,0,1)),((-4,4,5),750,7,(-1,0,1)),((5,4,6),550,5,(2,0,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=en; l.data.size=size; look_at(l,target)
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.25,.56,1,1); bg.inputs['Strength'].default_value=.75
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass
bpy.ops.wm.save_as_mainfile(filepath='/tmp/kids_vehicle_scene_v4.blend')
bpy.ops.render.render(animation=True)
print(scene.render.filepath)

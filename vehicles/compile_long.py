import pathlib, subprocess
ROOT=pathlib.Path(__file__).parent
archive=ROOT/'archive'; archive.mkdir(exist_ok=True)
outdir=ROOT/'out'; outdir.mkdir(exist_ok=True)
clips=sorted(archive.glob('*.mp4'))[-6:]
if len(clips)<6:
    raise SystemExit(f'Need 6 archived shorts; found {len(clips)}')
concat=ROOT/'concat.txt'
concat.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in clips)+'\n')
out=outdir/'kids-vehicle-compilation.mp4'
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(out)],check=True)
print(out)

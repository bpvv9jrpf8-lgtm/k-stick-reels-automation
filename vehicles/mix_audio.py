import json, pathlib, subprocess
ROOT=pathlib.Path(__file__).parent
EP=json.loads((ROOT/'episode.json').read_text())
video=ROOT/'silent_vehicle.mp4'
outdir=ROOT/'out'; outdir.mkdir(exist_ok=True)
out=outdir/'kids-vehicle-short.mp4'
inputs=['-i',str(video),'-i',str(ROOT/'sfx/music.wav')]
filters=['[1:a]volume=0.08[music]']
labels=['[music]']
idx=2
for b in EP['beats']:
    for n,sfx in enumerate(b.get('sfx',[])):
        p=ROOT/'sfx'/f'{sfx}.wav'
        if not p.exists():
            continue
        inputs += ['-i',str(p)]
        delay=int((float(b['start'])+0.35+n*0.14)*1000)
        label=f'a{idx}'
        filters.append(f'[{idx}:a]adelay={delay}|{delay},volume=0.55[{label}]')
        labels.append(f'[{label}]')
        idx+=1
filters.append(''.join(labels)+f'amix=inputs={len(labels)}:duration=longest:normalize=0[aout]')
cmd=['ffmpeg','-y',*inputs,'-filter_complex',';'.join(filters),'-map','0:v','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',str(out)]
subprocess.run(cmd,check=True)
print(out)

import json, os, pathlib, requests
from openai import OpenAI

ROOT = pathlib.Path(__file__).parent
AUDIO = ROOT / 'audio'
AUDIO.mkdir(exist_ok=True)

episode = json.loads((ROOT / 'episode.json').read_text())
lines = []
for beat in episode['beats']:
    for d in beat.get('dialogue', []):
        lines.append(d)

ELEVEN_KEY = os.getenv('ELEVENLABS_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

voice_env = {
    'kstick': os.getenv('ELEVENLABS_VOICE_KSTICK'),
    'zippy': os.getenv('ELEVENLABS_VOICE_ZIPPY'),
    'mimi': os.getenv('ELEVENLABS_VOICE_MIMI'),
}
openai_voice = {'kstick':'marin','zippy':'echo','mimi':'coral'}

def elevenlabs_tts(text, speaker, out):
    vid = voice_env.get(speaker)
    if not (ELEVEN_KEY and vid):
        return False
    r = requests.post(
        f'https://api.elevenlabs.io/v1/text-to-speech/{vid}',
        headers={'xi-api-key': ELEVEN_KEY, 'accept':'audio/mpeg', 'content-type':'application/json'},
        json={
            'text': text,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {'stability':0.40, 'similarity_boost':0.78, 'style':0.65, 'use_speaker_boost':True}
        },
        timeout=90,
    )
    if r.ok:
        out.write_bytes(r.content)
        return True
    print('ElevenLabs failed:', r.status_code, r.text[:300])
    return False

def openai_tts(text, speaker, out):
    if not OPENAI_KEY:
        raise RuntimeError('Need ELEVENLABS_API_KEY + voice IDs or OPENAI_API_KEY fallback')
    client = OpenAI(api_key=OPENAI_KEY)
    instructions = {
        'kstick':'Energetic lovable cartoon hero. Bright, emotional, playful, family-friendly.',
        'zippy':'Fast sarcastic prankster. Clever, teasing, expressive cartoon delivery.',
        'mimi':'Calm clever deadpan cartoon voice. Dry timing, composed, subtle confidence.'
    }[speaker]
    with client.audio.speech.with_streaming_response.create(
        model='gpt-4o-mini-tts', voice=openai_voice[speaker], input=text, instructions=instructions
    ) as response:
        response.stream_to_file(out)

for i, line in enumerate(lines):
    out = AUDIO / f'{i:02d}_{line["speaker"]}.mp3'
    if out.exists() and out.stat().st_size > 1000:
        continue
    if not elevenlabs_tts(line['text'], line['speaker'], out):
        openai_tts(line['text'], line['speaker'], out)
    line['audio_file'] = str(out.name)

(ROOT / 'dialogue_audio.json').write_text(json.dumps(lines, indent=2))
print(f'Generated {len(lines)} dialogue clips')

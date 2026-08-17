import fs from 'node:fs/promises';
import path from 'node:path';
import OpenAI from 'openai';
import episode from '../src/data/episode.json' with {type: 'json'};

const client = new OpenAI({apiKey: process.env.OPENAI_API_KEY});

const voices = {
  kstick: {
    voice: 'marin',
    instructions: 'Energetic lovable cartoon hero. Young adult energy, playful, expressive, clear, fast short-form comedy timing.',
  },
  zippy: {
    voice: 'echo',
    instructions: 'Fast sarcastic cartoon prankster. Playful teasing delivery, confident, slightly competitive, very clear.',
  },
  mimi: {
    voice: 'coral',
    instructions: 'Calm clever cartoon character with dry deadpan humor. Relaxed, confident, subtly amused, very clear.',
  },
};

const outDir = path.resolve('public/audio');
await fs.mkdir(outDir, {recursive: true});

for (const line of episode.dialogue) {
  const profile = voices[line.speaker];
  if (!profile) throw new Error(`Unknown speaker: ${line.speaker}`);

  console.log(`Generating ${line.id}: ${line.speaker} -> ${line.text}`);

  const audio = await client.audio.speech.create({
    model: 'gpt-4o-mini-tts',
    voice: profile.voice,
    input: line.text,
    instructions: profile.instructions,
    response_format: 'mp3',
    speed: 1.05,
  });

  const buffer = Buffer.from(await audio.arrayBuffer());
  await fs.writeFile(path.join(outDir, `${line.id}.mp3`), buffer);
}

console.log(`Generated ${episode.dialogue.length} dialogue clips in ${outDir}`);

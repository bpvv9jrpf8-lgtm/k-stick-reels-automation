import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import episode from './data/episode.json';
import {CharacterId, Emotion, Pose, StickCharacter} from './components/StickCharacter';

const FPS = 30;
const sec = (value: number) => Math.round(value * FPS);

const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

const Pizza: React.FC<{x: number; y: number; rotation?: number; scale?: number}> = ({
  x,
  y,
  rotation = 0,
  scale = 1,
}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      width: 150,
      height: 150,
      transform: `translate(-50%, -50%) rotate(${rotation}deg) scale(${scale})`,
      transformOrigin: '50% 50%',
      zIndex: 30,
      filter: 'drop-shadow(0 10px 8px rgba(0,0,0,.18))',
    }}
  >
    <svg viewBox="0 0 160 160" width="160" height="160">
      <path d="M25 25 Q80 5 135 25 L80 145 Z" fill="#ffd35a" stroke="#4b2e16" strokeWidth="8" strokeLinejoin="round" />
      <path d="M25 25 Q80 5 135 25" stroke="#c67b36" strokeWidth="20" strokeLinecap="round" fill="none" />
      <circle cx="65" cy="62" r="14" fill="#d73535" />
      <circle cx="98" cy="82" r="13" fill="#d73535" />
      <circle cx="78" cy="108" r="11" fill="#d73535" />
    </svg>
  </div>
);

const KitchenBackground: React.FC = () => (
  <AbsoluteFill style={{background: 'linear-gradient(180deg,#ffe9c7 0%,#fff7e8 58%,#ecd2ad 58%,#dfbc8c 100%)'}}>
    <div style={{position: 'absolute', left: 75, top: 170, width: 930, height: 560, borderRadius: 34, background: '#f6d9ad', boxShadow: 'inset 0 0 0 8px rgba(92,58,31,.12)'}} />
    <div style={{position: 'absolute', left: 110, top: 220, width: 310, height: 210, borderRadius: 24, background: '#a6d8ff', border: '9px solid #6e4a2b'}}>
      <div style={{position: 'absolute', left: '50%', top: 0, bottom: 0, width: 8, background: '#6e4a2b'}} />
      <div style={{position: 'absolute', top: '50%', left: 0, right: 0, height: 8, background: '#6e4a2b'}} />
    </div>
    <div style={{position: 'absolute', right: 120, top: 220, width: 250, height: 290, borderRadius: 22, background: '#ef5350', border: '9px solid #9b3534'}} />
    <div style={{position: 'absolute', right: 155, top: 265, width: 180, height: 18, borderRadius: 9, background: '#fff6dd'}} />
    <div style={{position: 'absolute', right: 155, top: 330, width: 180, height: 18, borderRadius: 9, background: '#fff6dd'}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 660, height: 210, background: '#bc875c'}} />
    <div style={{position: 'absolute', left: 180, top: 700, width: 720, height: 100, borderRadius: 26, background: '#7b4d2b', boxShadow: '0 16px 0 #5f381f'}} />
    <div style={{position: 'absolute', left: 250, top: 790, width: 38, height: 430, background: '#61391f'}} />
    <div style={{position: 'absolute', right: 250, top: 790, width: 38, height: 430, background: '#61391f'}} />
    <div style={{position: 'absolute', left: 475, top: 726, width: 130, height: 38, borderRadius: 999, background: '#f2f2f2', border: '6px solid #b9b9b9'}} />
  </AbsoluteFill>
);

const Subtitle: React.FC<{speaker: CharacterId; text: string; active: boolean}> = ({speaker, text, active}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!active) return null;
  const pop = spring({frame: frame % fps, fps, config: {damping: 12, stiffness: 180}});
  const accent = speaker === 'kstick' ? '#ef2b2d' : speaker === 'zippy' ? '#1f78ff' : '#f4c430';
  const label = speaker === 'kstick' ? 'K-STICK' : speaker === 'zippy' ? 'ZIPPY' : 'MIMI';
  return (
    <div style={{position: 'absolute', left: 90, right: 90, bottom: 180, display: 'flex', justifyContent: 'center', zIndex: 100, transform: `scale(${0.88 + pop * 0.12})`}}>
      <div style={{background: 'rgba(20,20,20,.90)', borderRadius: 30, padding: '20px 32px 24px', border: `6px solid ${accent}`, boxShadow: '0 14px 32px rgba(0,0,0,.25)', maxWidth: 860, textAlign: 'center'}}>
        <div style={{fontFamily: 'Arial, sans-serif', color: accent, fontWeight: 900, fontSize: 28, letterSpacing: 2, marginBottom: 6}}>{label}</div>
        <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: 'white', fontWeight: 900, fontSize: 58, lineHeight: 1.05, textShadow: '0 4px 0 #000'}}>{text}</div>
      </div>
    </div>
  );
};

const isSpeaking = (speaker: CharacterId, frame: number) =>
  episode.dialogue.some((line) => line.speaker === speaker && frame >= sec(line.start) && frame < sec(line.start + line.duration));

const activeLine = (frame: number) =>
  episode.dialogue.find((line) => frame >= sec(line.start) && frame < sec(line.start + line.duration));

export const KStickComedy: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const hookOut = interpolate(frame, [0, sec(0.2), sec(1.8), sec(2.2)], [0, 1, 1, 0], clamp);
  const hookScale = spring({frame, fps, config: {damping: 11, stiffness: 170}});

  const kEnter = interpolate(frame, [0, sec(1.0)], [-260, 75], clamp);
  const zEnter = interpolate(frame, [0, sec(1.3)], [1110, 700], clamp);
  const mimiEnter = interpolate(frame, [sec(2.8), sec(4.2)], [1110, 710], clamp);

  const duelBounce = frame >= sec(6.4) && frame < sec(10.2) ? Math.sin(frame * 0.55) * 18 : 0;
  const kPoint = frame >= sec(1.7) && frame < sec(4.0);
  const zAngry = frame >= sec(2.0) && frame < sec(5.4);

  const mimiSneakX = interpolate(frame, [sec(6.0), sec(11.5)], [710, 535], clamp);
  const mimiSneakY = interpolate(frame, [sec(6.0), sec(11.5)], [560, 590], clamp);

  const pizzaX = interpolate(frame, [sec(10.8), sec(12.8)], [540, 720], clamp);
  const pizzaY = interpolate(frame, [sec(10.8), sec(12.8)], [735, 660], clamp);
  const pizzaRot = interpolate(frame, [sec(10.8), sec(12.8)], [0, 24], clamp);

  const reveal = spring({frame: frame - sec(13.7), fps, config: {damping: 10, stiffness: 150}});
  const shakeAmount = frame >= sec(15.0) && frame <= sec(15.8) ? Math.sin(frame * 2.4) * 13 : 0;
  const punchZoom = interpolate(frame, [sec(18.8), sec(20.2)], [1, 1.12], clamp);
  const cameraX = frame >= sec(18.8) ? -55 * punchZoom : shakeAmount;
  const cameraY = frame >= sec(18.8) ? -35 * punchZoom : 0;

  const kPose: Pose = frame >= sec(14.0) ? 'shock' : kPoint ? 'point' : frame >= sec(7.4) && frame < sec(10.0) ? 'celebrate' : 'idle';
  const zPose: Pose = frame >= sec(14.0) ? 'shock' : frame >= sec(7.4) && frame < sec(10.0) ? 'celebrate' : 'idle';
  const mimiPose: Pose = frame >= sec(18.5) ? 'celebrate' : frame >= sec(10.8) ? 'talk' : 'idle';

  const kEmotion: Emotion = frame >= sec(14.0) ? 'shocked' : 'happy';
  const zEmotion: Emotion = frame >= sec(14.0) ? 'angry' : zAngry ? 'angry' : 'smug';
  const mimiEmotion: Emotion = frame >= sec(18.5) ? 'deadpan' : 'smug';

  const line = activeLine(frame);

  return (
    <AbsoluteFill style={{background: '#fff4df', overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${cameraX}px, ${cameraY}px) scale(${punchZoom})`, transformOrigin: '50% 55%'}}>
        <KitchenBackground />

        <div style={{position: 'absolute', left: 0, right: 0, top: 70, textAlign: 'center', zIndex: 80, opacity: hookOut, transform: `scale(${0.7 + hookScale * 0.3})`}}>
          <span style={{fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 80, fontWeight: 900, color: '#ffffff', WebkitTextStroke: '7px #111111', paintOrder: 'stroke', letterSpacing: 2}}>{episode.hook}</span>
        </div>

        <StickCharacter
          id="kstick"
          x={kEnter + duelBounce}
          y={570}
          scale={1.05}
          pose={kPose}
          emotion={kEmotion}
          speaking={isSpeaking('kstick', frame)}
          facing="right"
          lean={frame >= sec(14.0) ? -5 : 0}
        />

        <StickCharacter
          id="zippy"
          x={zEnter - duelBounce}
          y={570}
          scale={1.05}
          pose={zPose}
          emotion={zEmotion}
          speaking={isSpeaking('zippy', frame)}
          facing="left"
          lean={frame >= sec(14.0) ? 5 : 0}
        />

        <StickCharacter
          id="mimi"
          x={mimiSneakX}
          y={mimiSneakY}
          scale={0.98}
          pose={mimiPose}
          emotion={mimiEmotion}
          speaking={isSpeaking('mimi', frame)}
          facing={frame >= sec(13.5) ? 'left' : 'right'}
          opacity={interpolate(frame, [sec(2.8), sec(3.5)], [0, 1], clamp)}
        />

        <Pizza x={pizzaX} y={pizzaY} rotation={pizzaRot} scale={frame >= sec(18.8) ? 1 + reveal * 0.12 : 1} />

        {frame >= sec(13.8) && (
          <div style={{position: 'absolute', left: 445, top: 700, width: 190, height: 58, borderRadius: 999, background: '#f3f3f3', border: '7px solid #bbbbbb', zIndex: 22, opacity: interpolate(frame, [sec(13.8), sec(14.1)], [0, 1], clamp)}} />
        )}
      </div>

      {line && <Subtitle speaker={line.speaker as CharacterId} text={line.text} active />}

      {episode.dialogue.map((dialogue) => (
        <Sequence key={dialogue.id} from={sec(dialogue.start)} durationInFrames={sec(dialogue.duration + 0.3)}>
          <Audio src={staticFile(`audio/${dialogue.id}.mp3`)} volume={1.0} />
        </Sequence>
      ))}

      <Sequence from={sec(5.8)} durationInFrames={sec(0.8)}>
        <Audio src={staticFile('sfx/whoosh.wav')} volume={0.24} />
      </Sequence>
      <Sequence from={sec(10.9)} durationInFrames={sec(0.6)}>
        <Audio src={staticFile('sfx/pop.wav')} volume={0.35} />
      </Sequence>
      <Sequence from={sec(14.1)} durationInFrames={sec(0.7)}>
        <Audio src={staticFile('sfx/record.wav')} volume={0.28} />
      </Sequence>
      <Sequence from={sec(18.8)} durationInFrames={sec(0.8)}>
        <Audio src={staticFile('sfx/ding.wav')} volume={0.32} />
      </Sequence>

      <div style={{position: 'absolute', left: 35, top: 35, fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 26, color: 'rgba(0,0,0,.30)', zIndex: 110}}>K-STICK</div>
    </AbsoluteFill>
  );
};

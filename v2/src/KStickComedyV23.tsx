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
const sec = (n: number) => Math.round(n * FPS);
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

const COLORS: Record<CharacterId, string> = {
  kstick: '#ef2b2d',
  zippy: '#1f78ff',
  mimi: '#f4c430',
};

const LABELS: Record<CharacterId, string> = {
  kstick: 'K-STICK',
  zippy: 'ZIPPY',
  mimi: 'MIMI',
};

const Kitchen: React.FC = () => (
  <AbsoluteFill style={{background: 'linear-gradient(180deg,#fff0d4 0%,#fff8ea 62%,#e7c59a 62%,#d9ae79 100%)'}}>
    <div style={{position: 'absolute', left: 55, top: 135, width: 970, height: 720, borderRadius: 44, background: '#f8ddb3', boxShadow: 'inset 0 0 0 9px rgba(91,58,32,.10)'}} />
    <div style={{position: 'absolute', left: 105, top: 210, width: 330, height: 250, borderRadius: 26, background: '#9fd9ff', border: '10px solid #704625', overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: '50%', top: 0, bottom: 0, width: 8, background: '#704625'}} />
      <div style={{position: 'absolute', top: '50%', left: 0, right: 0, height: 8, background: '#704625'}} />
      <div style={{position: 'absolute', left: 18, right: 18, bottom: 22, height: 55, borderRadius: 30, background: '#8fca69'}} />
    </div>
    <div style={{position: 'absolute', right: 115, top: 200, width: 250, height: 360, borderRadius: 28, background: '#ef5a56', border: '10px solid #9f3836', boxShadow: '0 14px 0 rgba(100,50,35,.18)'}}>
      <div style={{position: 'absolute', left: 28, right: 28, top: 110, height: 16, borderRadius: 999, background: '#fff5dc'}} />
      <div style={{position: 'absolute', left: 28, right: 28, top: 210, height: 16, borderRadius: 999, background: '#fff5dc'}} />
    </div>
    <div style={{position: 'absolute', left: 70, right: 70, top: 870, height: 125, borderRadius: 26, background: '#bf7a4b', boxShadow: '0 18px 0 #89522f'}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 1190, bottom: 0, background: 'repeating-linear-gradient(90deg,#dfb47d 0,#dfb47d 110px,#d5a66e 110px,#d5a66e 120px)'}} />

    {/* Back half of the table. Characters render after this, so they stand behind the front apron. */}
    <div style={{position: 'absolute', left: 155, top: 1085, width: 770, height: 115, borderRadius: 30, background: '#7b4a29', boxShadow: '0 18px 0 #5f351c, 0 28px 30px rgba(0,0,0,.18)', zIndex: 8}} />
    <div style={{position: 'absolute', left: 235, top: 1180, width: 45, height: 520, background: '#61381e', zIndex: 7}} />
    <div style={{position: 'absolute', right: 235, top: 1180, width: 45, height: 520, background: '#61381e', zIndex: 7}} />
  </AbsoluteFill>
);

const TableForeground: React.FC = () => (
  <>
    <div style={{position: 'absolute', left: 155, top: 1095, width: 770, height: 112, borderBottomLeftRadius: 28, borderBottomRightRadius: 28, background: '#7b4a29', boxShadow: '0 18px 0 #5f351c', zIndex: 29}} />
    <div style={{position: 'absolute', left: 178, top: 1095, width: 724, height: 16, borderRadius: 999, background: 'rgba(255,255,255,.12)', zIndex: 30}} />
  </>
);

const Plate: React.FC = () => (
  <div style={{position: 'absolute', left: 540, top: 1084, width: 210, height: 66, borderRadius: '50%', transform: 'translate(-50%,-50%)', background: '#fafafa', border: '8px solid #bcbcbc', boxShadow: '0 9px 10px rgba(0,0,0,.16)', zIndex: 33}} />
);

const Pizza: React.FC<{x: number; y: number; scale: number; rotation: number; opacity: number; bite: number}> = ({x, y, scale, rotation, opacity, bite}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 160, height: 160, transform: `translate(-50%,-50%) rotate(${rotation}deg) scale(${scale})`, transformOrigin: '50% 50%', zIndex: 36, opacity, filter: 'drop-shadow(0 11px 8px rgba(0,0,0,.20))'}}>
    <svg viewBox="0 0 160 160" width="160" height="160">
      <defs>
        <mask id="pizza-mask-v23">
          <rect width="160" height="160" fill="white" />
          {bite > 0.18 && <circle cx="112" cy="88" r="22" fill="black" />}
          {bite > 0.52 && <circle cx="96" cy="119" r="20" fill="black" />}
          {bite > 0.82 && <circle cx="70" cy="96" r="18" fill="black" />}
        </mask>
      </defs>
      <g mask="url(#pizza-mask-v23)">
        <path d="M25 25 Q80 5 135 25 L80 145 Z" fill="#ffd35a" stroke="#4b2e16" strokeWidth="8" strokeLinejoin="round" />
        <path d="M25 25 Q80 5 135 25" stroke="#c67b36" strokeWidth="20" strokeLinecap="round" fill="none" />
        <circle cx="65" cy="62" r="14" fill="#d73535" />
        <circle cx="98" cy="82" r="13" fill="#d73535" />
        <circle cx="78" cy="108" r="11" fill="#d73535" />
      </g>
    </svg>
  </div>
);

const Crumbs: React.FC<{x: number; y: number; p: number}> = ({x, y, p}) => {
  if (p <= 0) return null;
  return (
    <>
      {[0, 1, 2, 3, 4].map((i) => {
        const a = -2.15 + i * 0.52;
        const d = 23 + p * (38 + i * 7);
        return <div key={i} style={{position: 'absolute', left: x + Math.cos(a) * d, top: y + Math.sin(a) * d, width: 8 + i * 2, height: 8 + i * 2, borderRadius: '50%', background: i % 2 ? '#ffd35a' : '#d73535', opacity: 1 - p * 0.55, zIndex: 44}} />;
      })}
    </>
  );
};

const Burst: React.FC<{x: number; y: number; p: number; color: string}> = ({x, y, p, color}) => {
  if (p <= 0) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y, zIndex: 70}}>
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => {
        const a = (Math.PI * 2 * i) / 8;
        return <div key={i} style={{position: 'absolute', width: 7, height: 55, borderRadius: 999, background: color, transformOrigin: '50% 100%', transform: `translate(${Math.cos(a) * (75 + p * 40)}px,${Math.sin(a) * (75 + p * 40)}px) rotate(${(a * 180) / Math.PI + 90}deg) scaleY(${0.55 + p * 0.45})`, opacity: Math.min(1, p * 1.7)}} />;
      })}
    </div>
  );
};

const BeatCard: React.FC<{label: string; p: number}> = ({label, p}) => {
  if (!label) return null;
  return (
    <div style={{position: 'absolute', left: '50%', top: 290, transform: `translateX(-50%) scale(${0.68 + p * 0.32}) rotate(${(1 - p) * -5}deg)`, background: '#fff', border: '8px solid #111', borderRadius: 28, padding: '14px 34px 17px', fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 60, fontWeight: 900, boxShadow: '0 13px 0 rgba(0,0,0,.14)', zIndex: 125, opacity: Math.min(1, p * 1.6)}}>{label}</div>
  );
};

const KineticCaption: React.FC<{frame: number}> = ({frame}) => {
  const lines = episode.dialogue.filter((line) => frame >= sec(line.start) && frame < sec(line.start + line.duration));
  if (!lines.length) return null;
  const primary = lines[0];
  const local = Math.max(0, frame - sec(primary.start));
  const duration = Math.max(1, sec(primary.duration));
  const words = primary.text.split(/\s+/);
  const active = Math.min(words.length - 1, Math.floor((local / duration) * words.length));
  const multiple = lines.length > 1;
  const accent = multiple ? '#8a5cff' : COLORS[primary.speaker as CharacterId];
  const label = multiple ? lines.map((l) => LABELS[l.speaker as CharacterId]).join(' + ') : LABELS[primary.speaker as CharacterId];

  return (
    <div style={{position: 'absolute', left: 65, right: 65, bottom: 145, zIndex: 150, display: 'flex', justifyContent: 'center'}}>
      <div style={{maxWidth: 920, background: 'rgba(15,15,18,.93)', border: `6px solid ${accent}`, borderRadius: 32, padding: '17px 27px 23px', boxShadow: '0 18px 40px rgba(0,0,0,.30)'}}>
        <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: accent, fontSize: 24, fontWeight: 900, letterSpacing: 2, textAlign: 'center', marginBottom: 9}}>{label}</div>
        <div style={{display: 'flex', flexWrap: 'wrap', gap: 11, justifyContent: 'center'}}>
          {words.map((word, i) => {
            const hot = i === active;
            return <span key={`${word}-${i}`} style={{fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 54, lineHeight: 1, fontWeight: 900, color: hot ? '#111' : '#fff', background: hot ? accent : 'transparent', borderRadius: 13, padding: hot ? '5px 9px 8px' : '5px 1px 8px', transform: `scale(${hot ? 1.08 : 1})`, textShadow: hot ? 'none' : '0 4px 0 #000'}}>{word}</span>;
          })}
        </div>
      </div>
    </div>
  );
};

const speaking = (id: CharacterId, frame: number) => episode.dialogue.some((line) => line.speaker === id && frame >= sec(line.start) && frame < sec(line.start + line.duration));

const camera = (frame: number) => {
  if (frame < sec(1.3)) return {scale: 1.20, x: 0, y: -90};
  if (frame < sec(3.5)) return {scale: 0.98, x: 0, y: 0};
  if (frame < sec(5.6)) return {scale: 1.01, x: 0, y: -8};
  if (frame < sec(9.0)) return {scale: 1.05, x: 0, y: -28};
  if (frame < sec(13.2)) return {scale: 1.06, x: 0, y: -18};
  if (frame < sec(14.05)) return {scale: 1.13, x: 0, y: -72};
  if (frame < sec(17.6)) return {scale: 0.98, x: 0, y: 0};
  if (frame < sec(20.1)) return {scale: 1.10, x: 45, y: -22};
  return {scale: 0.98, x: 0, y: 0};
};

export const KStickComedyV23: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cam = camera(frame);

  const hookSpring = spring({frame, fps, config: {damping: 10, stiffness: 190}});
  const hookOpacity = interpolate(frame, [sec(0.95), sec(1.35)], [1, 0], clamp);
  const kX = interpolate(frame, [0, sec(0.7)], [-220, 50], clamp);
  const zX = interpolate(frame, [sec(0.25), sec(1.05)], [1090, 720], clamp);

  const mimiOpacity = interpolate(frame, [sec(3.3), sec(3.7)], [0, 1], clamp);
  const mimiX = interpolate(frame, [sec(3.3), sec(5.6), sec(9.0), sec(11.5)], [385, 385, 400, 400], clamp);
  const mimiY = interpolate(frame, [sec(3.3), sec(4.6), sec(5.8), sec(11.5)], [630, 555, 715, 715], clamp);
  const mimiScale = interpolate(frame, [sec(3.3), sec(4.6), sec(5.8)], [0.82, 0.82, 0.92], clamp);

  const rock = frame >= sec(6.75) && frame < sec(7.25);
  const paper = frame >= sec(7.25) && frame < sec(7.75);
  const scissors = frame >= sec(7.75) && frame < sec(8.8);
  const beatLabel = rock ? 'ROCK!' : paper ? 'PAPER!' : scissors ? 'SCISSORS!' : '';
  const beatStart = rock ? sec(6.75) : paper ? sec(7.25) : sec(7.75);
  const beatP = beatLabel ? spring({frame: Math.max(0, frame - beatStart), fps, config: {damping: 10, stiffness: 230}}) : 0;

  const mouthX = mimiX + 155 * mimiScale;
  const mouthY = mimiY + 132 * mimiScale;
  const handX = mimiX + 178 * mimiScale;
  const handY = mimiY + 160 * mimiScale;

  // Keep the pizza visibly in Mimi's hand / beside her mouth instead of covering her face.
  const pizzaX = interpolate(
    frame,
    [0, sec(10.45), sec(11.25), sec(11.75), sec(12.20), sec(12.65), sec(13.05), sec(13.45)],
    [540, 540, handX + 12, mouthX + 46, handX + 14, mouthX + 46, handX + 12, mouthX + 44],
    clamp,
  );
  const pizzaY = interpolate(
    frame,
    [0, sec(10.45), sec(11.25), sec(11.75), sec(12.20), sec(12.65), sec(13.05), sec(13.45)],
    [1048, 1048, handY + 34, mouthY + 34, handY + 38, mouthY + 34, handY + 40, mouthY + 34],
    clamp,
  );
  const pizzaScale = interpolate(
    frame,
    [0, sec(10.45), sec(11.25), sec(11.75), sec(12.20), sec(12.65), sec(13.05), sec(13.45)],
    [0.92, 0.92, 0.42, 0.30, 0.34, 0.25, 0.21, 0.08],
    clamp,
  );
  const pizzaOpacity = interpolate(frame, [sec(13.12), sec(13.48)], [1, 0], clamp);
  const pizzaRotation = interpolate(frame, [sec(10.45), sec(13.45)], [0, 22], clamp);
  const bite = interpolate(frame, [sec(11.65), sec(12.95)], [0, 1], clamp);
  const crumbP = frame >= sec(11.65) && frame < sec(13.5) ? interpolate(frame, [sec(11.65), sec(13.5)], [0, 1], clamp) : 0;

  const reveal = spring({frame: frame - sec(13.3), fps, config: {damping: 10, stiffness: 190}});
  const shock = spring({frame: frame - sec(14.15), fps, config: {damping: 9, stiffness: 210}});
  const punch = spring({frame: frame - sec(18.2), fps, config: {damping: 10, stiffness: 190}});

  let kPose: Pose = 'idle';
  let zPose: Pose = 'idle';
  let mPose: Pose = 'idle';
  if (frame >= sec(0.9) && frame < sec(3.4)) kPose = 'accuse';
  if (frame >= sec(1.55) && frame < sec(3.4)) zPose = 'accuse';
  if (rock) {kPose = 'rock'; zPose = 'rock';}
  if (paper) {kPose = 'paper'; zPose = 'paper';}
  if (scissors) {kPose = 'rock'; zPose = 'scissors';}
  if (frame >= sec(8.8) && frame < sec(13.25)) {kPose = 'celebrate'; zPose = 'accuse';}
  if (frame >= sec(13.25) && frame < sec(17.6)) {kPose = 'shock'; zPose = frame >= sec(15.85) ? 'accuse' : 'shock';}
  if (frame >= sec(17.6)) {kPose = 'facepalm'; zPose = 'accuse';}
  if (frame >= sec(3.3) && frame < sec(5.5)) mPose = 'talk';
  if (frame >= sec(5.5) && frame < sec(10.6)) mPose = 'sneak';
  if (frame >= sec(10.6) && frame < sec(17.8)) mPose = 'eat';
  if (frame >= sec(17.8)) mPose = 'celebrate';

  let kEmotion: Emotion = 'happy';
  let zEmotion: Emotion = 'smug';
  let mEmotion: Emotion = 'deadpan';
  if (frame >= sec(1.0) && frame < sec(3.5)) {kEmotion = 'angry'; zEmotion = 'angry';}
  if (frame >= sec(8.8) && frame < sec(13.2)) {kEmotion = 'laughing'; zEmotion = 'angry';}
  if (frame >= sec(13.2)) {kEmotion = 'shocked'; zEmotion = frame < sec(15.8) ? 'shocked' : 'angry';}
  if (frame >= sec(10.4)) mEmotion = 'smug';
  if (frame >= sec(18.0)) mEmotion = 'deadpan';

  const shake = frame >= sec(14.15) && frame < sec(14.85) ? Math.sin(frame * 2.8) * 8 : 0;
  const cutTimes = [1.3, 3.5, 5.6, 9.0, 13.2, 14.05, 17.6, 20.1];
  const cutFlash = Math.max(...cutTimes.map((t) => interpolate(Math.abs(frame - sec(t)), [0, 2], [0.10, 0], clamp)));

  return (
    <AbsoluteFill style={{background: '#fff4df', overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${cam.x + shake}px,${cam.y}px) scale(${cam.scale})`, transformOrigin: '50% 58%'}}>
        <Kitchen />

        <StickCharacter id="kstick" x={kX} y={685} scale={1.02} pose={kPose} emotion={kEmotion} speaking={speaking('kstick', frame)} facing="right" lean={frame >= sec(14.1) && frame < sec(16.0) ? -5 : 0} squash={frame >= sec(14.1) && frame < sec(14.65) ? 1 : 0} />
        <StickCharacter id="zippy" x={zX} y={685} scale={1.02} pose={zPose} emotion={zEmotion} speaking={speaking('zippy', frame)} facing="left" lean={frame >= sec(14.1) && frame < sec(16.0) ? 5 : 0} squash={frame >= sec(14.1) && frame < sec(14.65) ? 1 : 0} />
        <StickCharacter id="mimi" x={mimiX} y={mimiY} scale={mimiScale + (frame >= sec(18.2) ? punch * 0.025 : 0)} pose={mPose} emotion={mEmotion} speaking={speaking('mimi', frame)} facing={frame < sec(13.8) ? 'right' : 'left'} opacity={mimiOpacity} lean={frame >= sec(5.5) && frame < sec(10.6) ? -4 : 0} />

        {/* Depth pass: cover lower legs so the cast stands behind the table instead of on it. */}
        <TableForeground />
        <Plate />
        <Pizza x={pizzaX} y={pizzaY} scale={pizzaScale} rotation={pizzaRotation} opacity={pizzaOpacity} bite={bite} />
        <Crumbs x={mouthX + 38} y={mouthY + 28} p={crumbP} />

        {frame >= sec(13.25) && frame < sec(14.25) && (
          <div style={{position: 'absolute', left: 540, top: 1000, transform: `translateX(-50%) scale(${0.65 + reveal * 0.35})`, zIndex: 85, fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 56, fontWeight: 900, color: '#fff', WebkitTextStroke: '7px #111', paintOrder: 'stroke'}}>EMPTY?!</div>
        )}

        <Burst x={205} y={770} p={frame >= sec(14.1) && frame < sec(15.7) ? shock : 0} color="#ef2b2d" />
        <Burst x={875} y={770} p={frame >= sec(14.1) && frame < sec(15.7) ? shock : 0} color="#1f78ff" />
        <Burst x={560} y={790} p={frame >= sec(18.2) && frame < sec(19.8) ? punch : 0} color="#f4c430" />
      </div>

      <div style={{position: 'absolute', left: 0, right: 0, top: 72, textAlign: 'center', zIndex: 135, opacity: hookOpacity, transform: `scale(${0.7 + hookSpring * 0.3})`}}>
        <span style={{fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 78, fontWeight: 900, color: '#fff', WebkitTextStroke: '8px #111', paintOrder: 'stroke', letterSpacing: 2, textShadow: '0 12px 0 rgba(0,0,0,.12)'}}>{episode.hook}</span>
      </div>

      <BeatCard label={beatLabel} p={beatP} />
      <KineticCaption frame={frame} />
      <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: cutFlash, pointerEvents: 'none', zIndex: 145}} />

      {episode.dialogue.map((d) => (
        <Sequence key={d.id} from={sec(d.start)} durationInFrames={sec(d.duration + 0.35)}>
          <Audio src={staticFile(`audio/${d.id}.mp3`)} volume={1} />
        </Sequence>
      ))}

      <Sequence from={sec(0.18)} durationInFrames={sec(0.7)}><Audio src={staticFile('sfx/whoosh.wav')} volume={0.28} /></Sequence>
      <Sequence from={sec(3.45)} durationInFrames={sec(0.5)}><Audio src={staticFile('sfx/pop.wav')} volume={0.24} /></Sequence>
      <Sequence from={sec(6.75)} durationInFrames={sec(0.5)}><Audio src={staticFile('sfx/pop.wav')} volume={0.22} /></Sequence>
      <Sequence from={sec(7.25)} durationInFrames={sec(0.5)}><Audio src={staticFile('sfx/pop.wav')} volume={0.22} /></Sequence>
      <Sequence from={sec(7.75)} durationInFrames={sec(0.6)}><Audio src={staticFile('sfx/ding.wav')} volume={0.30} /></Sequence>
      <Sequence from={sec(9.05)} durationInFrames={sec(0.8)}><Audio src={staticFile('sfx/whoosh.wav')} volume={0.16} /></Sequence>
      <Sequence from={sec(11.55)} durationInFrames={sec(0.9)}><Audio src={staticFile('sfx/munch.wav')} volume={0.35} /></Sequence>
      <Sequence from={sec(12.55)} durationInFrames={sec(0.75)}><Audio src={staticFile('sfx/munch.wav')} volume={0.26} /></Sequence>
      <Sequence from={sec(13.32)} durationInFrames={sec(0.8)}><Audio src={staticFile('sfx/record.wav')} volume={0.30} /></Sequence>
      <Sequence from={sec(14.15)} durationInFrames={sec(0.9)}><Audio src={staticFile('sfx/gasp.wav')} volume={0.32} /></Sequence>
      <Sequence from={sec(18.2)} durationInFrames={sec(0.8)}><Audio src={staticFile('sfx/ding.wav')} volume={0.34} /></Sequence>

      <div style={{position: 'absolute', left: 32, top: 28, fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 24, color: 'rgba(0,0,0,.24)', zIndex: 160}}>K-STICK</div>
    </AbsoluteFill>
  );
};

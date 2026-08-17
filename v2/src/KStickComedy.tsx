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

const speakerColor: Record<CharacterId, string> = {
  kstick: '#ef2b2d',
  zippy: '#1f78ff',
  mimi: '#f4c430',
};

const speakerLabel: Record<CharacterId, string> = {
  kstick: 'K-STICK',
  zippy: 'ZIPPY',
  mimi: 'MIMI',
};

const KitchenBackground: React.FC = () => (
  <AbsoluteFill style={{background: 'linear-gradient(180deg,#fff0d4 0%,#fff8ea 62%,#e7c59a 62%,#d9ae79 100%)'}}>
    <div style={{position: 'absolute', left: 55, top: 135, width: 970, height: 720, borderRadius: 44, background: '#f8ddb3', boxShadow: 'inset 0 0 0 9px rgba(91,58,32,.10)'}} />

    <div style={{position: 'absolute', left: 105, top: 210, width: 330, height: 250, borderRadius: 26, background: '#9fd9ff', border: '10px solid #704625', overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: '50%', top: 0, bottom: 0, width: 8, background: '#704625'}} />
      <div style={{position: 'absolute', top: '50%', left: 0, right: 0, height: 8, background: '#704625'}} />
      <div style={{position: 'absolute', left: 18, right: 18, bottom: 22, height: 55, borderRadius: 30, background: '#8fca69'}} />
    </div>

    <div style={{position: 'absolute', right: 115, top: 200, width: 250, height: 360, borderRadius: 28, background: '#ef5a56', border: '10px solid #9f3836', boxShadow: '0 14px 0 rgba(100,50,35,.18)'}}>
      <div style={{position: 'absolute', left: 27, right: 27, top: 105, height: 16, borderRadius: 999, background: '#fff5dc'}} />
      <div style={{position: 'absolute', left: 27, right: 27, top: 205, height: 16, borderRadius: 999, background: '#fff5dc'}} />
    </div>

    <div style={{position: 'absolute', left: 70, right: 70, top: 870, height: 125, borderRadius: 26, background: '#bf7a4b', boxShadow: '0 18px 0 #89522f'}} />
    <div style={{position: 'absolute', left: 105, top: 900, width: 150, height: 65, borderRadius: 18, background: '#d99c67'}} />
    <div style={{position: 'absolute', left: 285, top: 900, width: 150, height: 65, borderRadius: 18, background: '#d99c67'}} />
    <div style={{position: 'absolute', right: 105, top: 900, width: 150, height: 65, borderRadius: 18, background: '#d99c67'}} />

    <div style={{position: 'absolute', left: 0, right: 0, top: 1190, bottom: 0, background: 'repeating-linear-gradient(90deg,#dfb47d 0,#dfb47d 110px,#d5a66e 110px,#d5a66e 120px)'}} />

    <div style={{position: 'absolute', left: 155, top: 1085, width: 770, height: 115, borderRadius: 30, background: '#7b4a29', boxShadow: '0 18px 0 #5f351c, 0 28px 30px rgba(0,0,0,.18)', zIndex: 8}} />
    <div style={{position: 'absolute', left: 235, top: 1180, width: 45, height: 520, background: '#61381e', zIndex: 7}} />
    <div style={{position: 'absolute', right: 235, top: 1180, width: 45, height: 520, background: '#61381e', zIndex: 7}} />
  </AbsoluteFill>
);

const Plate: React.FC<{opacity?: number}> = ({opacity = 1}) => (
  <div
    style={{
      position: 'absolute',
      left: 540,
      top: 1095,
      width: 210,
      height: 68,
      borderRadius: '50%',
      transform: 'translate(-50%,-50%)',
      background: '#fafafa',
      border: '8px solid #bcbcbc',
      boxShadow: '0 9px 10px rgba(0,0,0,.16)',
      opacity,
      zIndex: 17,
    }}
  />
);

const Pizza: React.FC<{
  x: number;
  y: number;
  rotation?: number;
  scale?: number;
  opacity?: number;
  bite?: number;
}> = ({x, y, rotation = 0, scale = 1, opacity = 1, bite = 0}) => {
  const biteA = bite > 0.2;
  const biteB = bite > 0.55;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: 160,
        height: 160,
        transform: `translate(-50%, -50%) rotate(${rotation}deg) scale(${scale})`,
        transformOrigin: '50% 50%',
        zIndex: 35,
        opacity,
        filter: 'drop-shadow(0 11px 8px rgba(0,0,0,.20))',
      }}
    >
      <svg viewBox="0 0 160 160" width="160" height="160">
        <defs>
          <mask id="pizza-bites">
            <rect width="160" height="160" fill="white" />
            {biteA && <circle cx="112" cy="88" r="22" fill="black" />}
            {biteB && <circle cx="96" cy="119" r="20" fill="black" />}
          </mask>
        </defs>
        <g mask="url(#pizza-bites)">
          <path d="M25 25 Q80 5 135 25 L80 145 Z" fill="#ffd35a" stroke="#4b2e16" strokeWidth="8" strokeLinejoin="round" />
          <path d="M25 25 Q80 5 135 25" stroke="#c67b36" strokeWidth="20" strokeLinecap="round" fill="none" />
          <circle cx="65" cy="62" r="14" fill="#d73535" />
          <circle cx="98" cy="82" r="13" fill="#d73535" />
          <circle cx="78" cy="108" r="11" fill="#d73535" />
        </g>
      </svg>
    </div>
  );
};

const Crumbs: React.FC<{x: number; y: number; amount: number}> = ({x, y, amount}) => {
  if (amount <= 0) return null;
  return (
    <>
      {[0, 1, 2, 3, 4].map((i) => {
        const angle = -1.8 + i * 0.38;
        const distance = 30 + amount * (45 + i * 7);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x + Math.cos(angle) * distance,
              top: y + Math.sin(angle) * distance,
              width: 10 + i * 2,
              height: 10 + i * 2,
              borderRadius: '50%',
              background: i % 2 === 0 ? '#d73535' : '#ffd35a',
              zIndex: 42,
              opacity: 1 - amount * 0.55,
            }}
          />
        );
      })}
    </>
  );
};

const ReactionBurst: React.FC<{x: number; y: number; progress: number; color?: string}> = ({x, y, progress, color = '#111'}) => {
  if (progress <= 0) return null;
  const radius = 75 + progress * 55;
  return (
    <div style={{position: 'absolute', left: x, top: y, zIndex: 70, pointerEvents: 'none'}}>
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => {
        const a = (Math.PI * 2 * i) / 8;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              width: 8,
              height: 58,
              borderRadius: 999,
              background: color,
              transformOrigin: '50% 100%',
              transform: `translate(${Math.cos(a) * radius}px, ${Math.sin(a) * radius}px) rotate(${(a * 180) / Math.PI + 90}deg) scaleY(${0.55 + progress * 0.45})`,
              opacity: Math.min(1, progress * 1.6),
            }}
          />
        );
      })}
    </div>
  );
};

const MotionLines: React.FC<{progress: number; direction?: 'left' | 'right'}> = ({progress, direction = 'left'}) => {
  if (progress <= 0) return null;
  return (
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden', zIndex: 14, opacity: Math.min(0.6, progress)}}>
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: 610 + i * 70,
            left: direction === 'left' ? 620 + i * 18 : 110 + i * 20,
            width: 190 + i * 20,
            height: 7,
            borderRadius: 999,
            background: 'rgba(30,30,30,.30)',
            transform: `skewX(${direction === 'left' ? -20 : 20}deg) translateX(${(1 - progress) * (direction === 'left' ? 100 : -100)}px)`,
          }}
        />
      ))}
    </div>
  );
};

const HandBeat: React.FC<{label: string; progress: number}> = ({label, progress}) => {
  if (progress <= 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: '50%',
        top: 355,
        transform: `translateX(-50%) scale(${0.65 + progress * 0.35}) rotate(${(1 - progress) * -6}deg)`,
        background: '#fff',
        color: '#111',
        border: '8px solid #111',
        borderRadius: 28,
        padding: '14px 34px 17px',
        fontFamily: 'Arial Black, Arial, sans-serif',
        fontWeight: 900,
        fontSize: 62,
        boxShadow: '0 13px 0 rgba(0,0,0,.14)',
        zIndex: 90,
        opacity: Math.min(1, progress * 1.5),
      }}
    >
      {label}
    </div>
  );
};

const KineticSubtitle: React.FC<{lines: typeof episode.dialogue; frame: number}> = ({lines, frame}) => {
  if (lines.length === 0) return null;
  const primary = lines[0];
  const start = sec(primary.start);
  const duration = Math.max(1, sec(primary.duration));
  const local = Math.max(0, Math.min(duration - 1, frame - start));
  const progress = local / duration;
  const words = primary.text.split(/\s+/);
  const activeIndex = Math.min(words.length - 1, Math.floor(progress * words.length));
  const multi = lines.length > 1;
  const label = multi ? lines.map((l) => speakerLabel[l.speaker as CharacterId]).join(' + ') : speakerLabel[primary.speaker as CharacterId];
  const accent = multi ? '#8a5cff' : speakerColor[primary.speaker as CharacterId];

  return (
    <div style={{position: 'absolute', left: 65, right: 65, bottom: 145, zIndex: 130, display: 'flex', justifyContent: 'center'}}>
      <div style={{background: 'rgba(15,15,18,.92)', border: `6px solid ${accent}`, borderRadius: 32, padding: '18px 28px 24px', maxWidth: 920, boxShadow: '0 18px 40px rgba(0,0,0,.30)'}}>
        <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: accent, fontWeight: 900, fontSize: 25, letterSpacing: 2, textAlign: 'center', marginBottom: 10}}>{label}</div>
        <div style={{display: 'flex', gap: 12, flexWrap: 'wrap', justifyContent: 'center'}}>
          {words.map((word, index) => {
            const isActive = index === activeIndex;
            const pop = spring({frame: Math.max(0, local - Math.floor((index / words.length) * duration)), fps: FPS, config: {damping: 13, stiffness: 210}});
            return (
              <span
                key={`${word}-${index}`}
                style={{
                  display: 'inline-block',
                  fontFamily: 'Arial Black, Arial, sans-serif',
                  fontSize: 55,
                  lineHeight: 1.0,
                  fontWeight: 900,
                  color: isActive ? '#111' : '#fff',
                  background: isActive ? accent : 'transparent',
                  borderRadius: 14,
                  padding: isActive ? '5px 9px 8px' : '5px 1px 8px',
                  transform: `scale(${isActive ? 1.08 + pop * 0.05 : 1})`,
                  textShadow: isActive ? 'none' : '0 4px 0 #000',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const isSpeaking = (speaker: CharacterId, frame: number) =>
  episode.dialogue.some((line) => line.speaker === speaker && frame >= sec(line.start) && frame < sec(line.start + line.duration));

const activeLines = (frame: number) =>
  episode.dialogue.filter((line) => frame >= sec(line.start) && frame < sec(line.start + line.duration));

const shotTransform = (frame: number) => {
  if (frame < sec(1.35)) {
    const p = interpolate(frame, [0, sec(1.35)], [0, 1], clamp);
    return {scale: 1.28 + p * 0.13, x: 0, y: -155};
  }
  if (frame < sec(3.55)) return {scale: 1.02, x: 0, y: 0};
  if (frame < sec(5.7)) return {scale: 1.08, x: -45, y: -15};
  if (frame < sec(9.1)) return {scale: 1.18, x: 0, y: -70};
  if (frame < sec(13.25)) {
    const p = interpolate(frame, [sec(9.1), sec(13.25)], [0, 1], clamp);
    return {scale: 1.16, x: -80 - p * 75, y: -40};
  }
  if (frame < sec(15.0)) return {scale: 1.35, x: 0, y: -140};
  if (frame < sec(17.6)) return {scale: 1.08, x: 0, y: -15};
  if (frame < sec(20.1)) return {scale: 1.28, x: -120, y: -55};
  return {scale: 1.03, x: 0, y: 0};
};

export const KStickComedy: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const shot = shotTransform(frame);

  const hookIn = spring({frame, fps, config: {damping: 11, stiffness: 190}});
  const hookOut = interpolate(frame, [sec(1.0), sec(1.45)], [1, 0], clamp);

  const kEnter = interpolate(frame, [0, sec(0.75)], [-260, 55], clamp);
  const zEnter = interpolate(frame, [sec(0.3), sec(1.15)], [1110, 710], clamp);
  const mimiOpacity = interpolate(frame, [sec(3.25), sec(3.75)], [0, 1], clamp);
  const mimiX = interpolate(frame, [sec(3.4), sec(5.5), sec(9.0), sec(11.5)], [860, 720, 705, 520], clamp);
  const mimiY = interpolate(frame, [sec(3.4), sec(5.5), sec(11.5)], [725, 720, 735], clamp);

  const rpsRock = frame >= sec(6.75) && frame < sec(7.25);
  const rpsPaper = frame >= sec(7.25) && frame < sec(7.75);
  const rpsFinal = frame >= sec(7.75) && frame < sec(8.8);
  const rpsLabel = rpsRock ? 'ROCK!' : rpsPaper ? 'PAPER!' : rpsFinal ? 'SCISSORS!' : '';
  const rpsProgress = rpsLabel
    ? spring({frame: frame - (rpsRock ? sec(6.75) : rpsPaper ? sec(7.25) : sec(7.75)), fps, config: {damping: 10, stiffness: 230}})
    : 0;

  const stealProgress = interpolate(frame, [sec(9.1), sec(11.6)], [0, 1], clamp);
  const pizzaGrabProgress = interpolate(frame, [sec(10.45), sec(11.5)], [0, 1], clamp);
  const pizzaEatProgress = interpolate(frame, [sec(11.5), sec(13.25)], [0, 1], clamp);

  const mimiMouthX = mimiX + 155;
  const mimiMouthY = mimiY + 132;
  const pizzaX = interpolate(pizzaGrabProgress, [0, 1], [540, mimiMouthX + 35], clamp);
  const pizzaY = interpolate(pizzaGrabProgress, [0, 1], [1058, mimiMouthY + 5], clamp);
  const pizzaScale = interpolate(frame, [sec(10.45), sec(11.5), sec(13.25), sec(13.7)], [1, 0.72, 0.52, 0.18], clamp);
  const pizzaOpacity = interpolate(frame, [sec(13.2), sec(13.7)], [1, 0], clamp);
  const pizzaRotation = interpolate(frame, [sec(10.45), sec(13.2)], [0, 24], clamp);
  const crumbProgress = frame >= sec(11.8) && frame < sec(13.7) ? interpolate(frame, [sec(11.8), sec(13.7)], [0, 1], clamp) : 0;

  const revealProgress = spring({frame: frame - sec(13.45), fps, config: {damping: 10, stiffness: 190}});
  const reactionProgress = spring({frame: frame - sec(14.25), fps, config: {damping: 9, stiffness: 210}});
  const punchProgress = spring({frame: frame - sec(18.25), fps, config: {damping: 10, stiffness: 190}});
  const endBounce = frame >= sec(20.0) ? Math.abs(Math.sin(frame * 0.42)) : 0;

  const shake = frame >= sec(14.3) && frame < sec(15.05) ? Math.sin(frame * 2.8) * 12 : 0;
  const endShake = frame >= sec(19.1) && frame < sec(19.55) ? Math.sin(frame * 3.1) * 6 : 0;

  let kPose: Pose = 'idle';
  let zPose: Pose = 'idle';
  let mimiPose: Pose = 'idle';

  if (frame >= sec(1.0) && frame < sec(3.4)) kPose = 'accuse';
  if (frame >= sec(1.6) && frame < sec(3.4)) zPose = 'accuse';
  if (rpsRock) {kPose = 'rock'; zPose = 'rock';}
  if (rpsPaper) {kPose = 'paper'; zPose = 'paper';}
  if (rpsFinal) {kPose = 'rock'; zPose = 'scissors';}
  if (frame >= sec(8.8) && frame < sec(13.25)) {kPose = 'celebrate'; zPose = 'accuse';}
  if (frame >= sec(13.35) && frame < sec(18.1)) {kPose = 'shock'; zPose = 'shock';}
  if (frame >= sec(18.1)) {kPose = 'facepalm'; zPose = 'accuse';}

  if (frame >= sec(3.4) && frame < sec(5.6)) mimiPose = 'talk';
  if (frame >= sec(5.6) && frame < sec(10.8)) mimiPose = 'sneak';
  if (frame >= sec(10.8) && frame < sec(17.9)) mimiPose = 'eat';
  if (frame >= sec(17.9)) mimiPose = 'celebrate';

  let kEmotion: Emotion = 'happy';
  let zEmotion: Emotion = 'smug';
  let mimiEmotion: Emotion = 'deadpan';
  if (frame >= sec(1.2) && frame < sec(3.5)) {kEmotion = 'angry'; zEmotion = 'angry';}
  if (frame >= sec(8.8) && frame < sec(13.3)) {kEmotion = 'laughing'; zEmotion = 'angry';}
  if (frame >= sec(13.3)) {kEmotion = 'shocked'; zEmotion = frame < sec(17.7) ? 'shocked' : 'angry';}
  if (frame >= sec(10.7)) mimiEmotion = 'smug';
  if (frame >= sec(18.2)) mimiEmotion = 'deadpan';

  const lines = activeLines(frame);

  return (
    <AbsoluteFill style={{background: '#fff4df', overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translate(${shot.x + shake + endShake}px, ${shot.y}px) scale(${shot.scale})`,
          transformOrigin: '50% 58%',
        }}
      >
        <KitchenBackground />
        <Plate />

        <MotionLines progress={stealProgress * (1 - pizzaGrabProgress)} direction="left" />

        <StickCharacter
          id="kstick"
          x={kEnter}
          y={685}
          scale={1.05}
          pose={kPose}
          emotion={kEmotion}
          speaking={isSpeaking('kstick', frame)}
          facing="right"
          lean={frame >= sec(14.0) && frame < sec(17.0) ? -6 : 0}
          squash={frame >= sec(14.25) && frame < sec(14.8) ? 1 : 0}
        />

        <StickCharacter
          id="zippy"
          x={zEnter}
          y={685}
          scale={1.05}
          pose={zPose}
          emotion={zEmotion}
          speaking={isSpeaking('zippy', frame)}
          facing="left"
          lean={frame >= sec(14.0) && frame < sec(17.0) ? 6 : 0}
          squash={frame >= sec(14.25) && frame < sec(14.8) ? 1 : 0}
        />

        <StickCharacter
          id="mimi"
          x={mimiX}
          y={mimiY - endBounce * 8}
          scale={0.98 + punchProgress * 0.03}
          pose={mimiPose}
          emotion={mimiEmotion}
          speaking={isSpeaking('mimi', frame)}
          facing={frame < sec(9.0) ? 'left' : frame < sec(13.4) ? 'left' : 'right'}
          opacity={mimiOpacity}
          lean={frame >= sec(5.6) && frame < sec(10.8) ? -5 : 0}
        />

        <Pizza
          x={pizzaX}
          y={pizzaY}
          rotation={pizzaRotation}
          scale={pizzaScale}
          opacity={pizzaOpacity}
          bite={pizzaEatProgress}
        />
        <Crumbs x={mimiMouthX + 18} y={mimiMouthY + 10} amount={crumbProgress} />

        {frame >= sec(13.35) && frame < sec(15.4) && (
          <div
            style={{
              position: 'absolute',
              left: 540,
              top: 1015,
              transform: `translateX(-50%) scale(${0.65 + revealProgress * 0.35})`,
              zIndex: 82,
              fontFamily: 'Arial Black, Arial, sans-serif',
              fontSize: 58,
              fontWeight: 900,
              color: '#fff',
              WebkitTextStroke: '7px #111',
              paintOrder: 'stroke',
              letterSpacing: 2,
            }}
          >
            EMPTY?!
          </div>
        )}

        <ReactionBurst x={218} y={770} progress={frame >= sec(14.2) && frame < sec(16.0) ? reactionProgress : 0} color="#ef2b2d" />
        <ReactionBurst x={860} y={770} progress={frame >= sec(14.2) && frame < sec(16.0) ? reactionProgress : 0} color="#1f78ff" />
        <ReactionBurst x={690} y={795} progress={frame >= sec(18.2) && frame < sec(20.0) ? punchProgress : 0} color="#f4c430" />

        <HandBeat label={rpsLabel} progress={rpsProgress} />

        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 55,
            textAlign: 'center',
            zIndex: 100,
            opacity: hookOut,
            transform: `scale(${0.68 + hookIn * 0.32})`,
          }}
        >
          <span
            style={{
              fontFamily: 'Arial Black, Arial, sans-serif',
              fontSize: 80,
              fontWeight: 900,
              color: '#fff',
              WebkitTextStroke: '8px #111',
              paintOrder: 'stroke',
              letterSpacing: 2,
              textShadow: '0 12px 0 rgba(0,0,0,.12)',
            }}
          >
            {episode.hook}
          </span>
        </div>

        {frame >= sec(18.25) && frame < sec(20.2) && (
          <div
            style={{
              position: 'absolute',
              left: 620,
              top: 520,
              transform: `rotate(-8deg) scale(${0.7 + punchProgress * 0.3})`,
              background: '#fff',
              border: '7px solid #111',
              borderRadius: 999,
              padding: '14px 24px',
              fontFamily: 'Arial Black, Arial, sans-serif',
              fontSize: 44,
              fontWeight: 900,
              zIndex: 95,
            }}
          >
            😏
          </div>
        )}
      </div>

      <KineticSubtitle lines={lines} frame={frame} />

      {episode.dialogue.map((dialogue) => (
        <Sequence key={dialogue.id} from={sec(dialogue.start)} durationInFrames={sec(dialogue.duration + 0.35)}>
          <Audio src={staticFile(`audio/${dialogue.id}.mp3`)} volume={1.0} />
        </Sequence>
      ))}

      <Sequence from={sec(0.18)} durationInFrames={sec(0.7)}>
        <Audio src={staticFile('sfx/whoosh.wav')} volume={0.28} />
      </Sequence>
      <Sequence from={sec(3.55)} durationInFrames={sec(0.55)}>
        <Audio src={staticFile('sfx/pop.wav')} volume={0.26} />
      </Sequence>
      <Sequence from={sec(6.75)} durationInFrames={sec(0.5)}>
        <Audio src={staticFile('sfx/pop.wav')} volume={0.22} />
      </Sequence>
      <Sequence from={sec(7.25)} durationInFrames={sec(0.5)}>
        <Audio src={staticFile('sfx/pop.wav')} volume={0.22} />
      </Sequence>
      <Sequence from={sec(7.75)} durationInFrames={sec(0.6)}>
        <Audio src={staticFile('sfx/ding.wav')} volume={0.30} />
      </Sequence>
      <Sequence from={sec(9.15)} durationInFrames={sec(0.8)}>
        <Audio src={staticFile('sfx/whoosh.wav')} volume={0.18} />
      </Sequence>
      <Sequence from={sec(11.55)} durationInFrames={sec(0.9)}>
        <Audio src={staticFile('sfx/munch.wav')} volume={0.34} />
      </Sequence>
      <Sequence from={sec(13.45)} durationInFrames={sec(0.8)}>
        <Audio src={staticFile('sfx/record.wav')} volume={0.30} />
      </Sequence>
      <Sequence from={sec(14.25)} durationInFrames={sec(0.9)}>
        <Audio src={staticFile('sfx/gasp.wav')} volume={0.32} />
      </Sequence>
      <Sequence from={sec(18.25)} durationInFrames={sec(0.8)}>
        <Audio src={staticFile('sfx/ding.wav')} volume={0.34} />
      </Sequence>

      <div style={{position: 'absolute', left: 32, top: 28, fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 24, color: 'rgba(0,0,0,.24)', zIndex: 140}}>K-STICK</div>
    </AbsoluteFill>
  );
};

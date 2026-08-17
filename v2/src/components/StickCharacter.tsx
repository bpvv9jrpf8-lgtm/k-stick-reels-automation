import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export type CharacterId = 'kstick' | 'zippy' | 'mimi';
export type Pose = 'idle' | 'point' | 'talk' | 'run' | 'shock' | 'celebrate';
export type Emotion = 'happy' | 'smug' | 'shocked' | 'angry' | 'deadpan';

type Props = {
  id: CharacterId;
  x: number;
  y: number;
  scale?: number;
  pose?: Pose;
  emotion?: Emotion;
  speaking?: boolean;
  facing?: 'left' | 'right';
  opacity?: number;
  lean?: number;
};

const colors: Record<CharacterId, {accent: string; eye: string}> = {
  kstick: {accent: '#ef2b2d', eye: '#111111'},
  zippy: {accent: '#1f78ff', eye: '#111111'},
  mimi: {accent: '#f4c430', eye: '#111111'},
};

export const StickCharacter: React.FC<Props> = ({
  id,
  x,
  y,
  scale = 1,
  pose = 'idle',
  emotion = 'happy',
  speaking = false,
  facing = 'right',
  opacity = 1,
  lean = 0,
}) => {
  const frame = useCurrentFrame();
  const accent = colors[id].accent;
  const flip = facing === 'left' ? -1 : 1;
  const talkPulse = speaking ? Math.sin(frame * 1.15) : -1;
  const mouthOpen = speaking && talkPulse > -0.05;
  const blink = frame % 83 > 79;
  const idleBob = Math.sin(frame * 0.12) * (pose === 'idle' ? 4 : 2);
  const runBob = pose === 'run' ? Math.sin(frame * 0.8) * 8 : 0;
  const shockScale = pose === 'shock' ? interpolate(Math.sin(frame * 0.35), [-1, 1], [0.98, 1.04]) : 1;

  const arm = (() => {
    if (pose === 'point') return {lx: 74, ly: 245, rx: 245, ry: 190};
    if (pose === 'run') return {lx: 55, ly: 225, rx: 250, ry: 270};
    if (pose === 'celebrate') return {lx: 70, ly: 125, rx: 235, ry: 125};
    if (pose === 'shock') return {lx: 65, ly: 170, rx: 240, ry: 170};
    return {lx: 82, ly: 245, rx: 220, ry: 245};
  })();

  const legs = (() => {
    if (pose === 'run') {
      const swap = Math.sin(frame * 0.8) > 0;
      return swap
        ? {lx: 95, ly: 455, rx: 225, ry: 415}
        : {lx: 80, ly: 410, rx: 215, ry: 460};
    }
    if (pose === 'celebrate') return {lx: 85, ly: 445, rx: 225, ry: 445};
    return {lx: 105, ly: 455, rx: 205, ry: 455};
  })();

  const eyeY = emotion === 'shocked' ? 85 : 92;
  const eyeRadius = emotion === 'shocked' ? 11 : 8;
  const browTilt = emotion === 'angry' ? 14 : emotion === 'smug' ? -8 : 0;
  const mouthY = 130;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y + idleBob + runBob,
        width: 310,
        height: 500,
        transform: `scale(${scale * shockScale}) scaleX(${flip}) rotate(${lean}deg)`,
        transformOrigin: '50% 90%',
        opacity,
        zIndex: 20,
      }}
    >
      <svg width="310" height="500" viewBox="0 0 310 500">
        <g stroke="#101010" strokeWidth="13" strokeLinecap="round" fill="none">
          <line x1="155" y1="180" x2="155" y2="350" />
          <line x1="155" y1="220" x2={arm.lx} y2={arm.ly} />
          <line x1="155" y1="220" x2={arm.rx} y2={arm.ry} />
          <line x1="155" y1="348" x2={legs.lx} y2={legs.ly} />
          <line x1="155" y1="348" x2={legs.rx} y2={legs.ry} />
        </g>

        <circle cx="155" cy="105" r="72" fill="#ffffff" stroke="#101010" strokeWidth="10" />

        {!blink && (
          <>
            <circle cx="130" cy={eyeY} r={eyeRadius} fill="#111111" />
            <circle cx="180" cy={eyeY} r={eyeRadius} fill="#111111" />
          </>
        )}
        {blink && (
          <g stroke="#111111" strokeWidth="6" strokeLinecap="round">
            <line x1="119" y1="92" x2="140" y2="92" />
            <line x1="169" y1="92" x2="190" y2="92" />
          </g>
        )}

        {(emotion === 'angry' || emotion === 'smug') && (
          <g stroke="#111111" strokeWidth="5" strokeLinecap="round">
            <line x1="116" y1="70" x2="140" y2={70 + browTilt} />
            <line x1="170" y1={70 + browTilt} x2="194" y2="70" />
          </g>
        )}

        {mouthOpen ? (
          <ellipse cx="155" cy={mouthY} rx="16" ry="12" fill="#111111" />
        ) : emotion === 'deadpan' ? (
          <line x1="140" y1={mouthY} x2="170" y2={mouthY} stroke="#111111" strokeWidth="5" strokeLinecap="round" />
        ) : emotion === 'shocked' ? (
          <circle cx="155" cy={mouthY} r="11" fill="#111111" />
        ) : (
          <path d="M137 125 Q155 142 174 125" stroke="#111111" strokeWidth="5" fill="none" strokeLinecap="round" />
        )}

        {id === 'kstick' && (
          <g>
            <path d="M92 58 Q155 10 220 58 L218 82 Q155 54 94 82 Z" fill={accent} stroke="#101010" strokeWidth="8" />
            <path d="M215 64 Q254 65 266 82 Q234 86 212 80 Z" fill={accent} stroke="#101010" strokeWidth="7" />
          </g>
        )}

        {id === 'zippy' && (
          <g stroke={accent} strokeWidth="8" fill="none">
            <rect x="105" y="74" width="43" height="31" rx="12" />
            <rect x="162" y="74" width="43" height="31" rx="12" />
            <line x1="148" y1="89" x2="162" y2="89" />
          </g>
        )}

        {id === 'mimi' && (
          <g>
            <path d="M93 54 Q155 26 219 54" stroke={accent} strokeWidth="14" fill="none" strokeLinecap="round" />
            <circle cx="155" cy="42" r="12" fill={accent} stroke="#101010" strokeWidth="5" />
          </g>
        )}
      </svg>
    </div>
  );
};

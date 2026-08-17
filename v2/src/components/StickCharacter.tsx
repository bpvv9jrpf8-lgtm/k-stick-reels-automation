import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export type CharacterId = 'kstick' | 'zippy' | 'mimi';
export type Pose =
  | 'idle'
  | 'point'
  | 'talk'
  | 'run'
  | 'shock'
  | 'celebrate'
  | 'rock'
  | 'paper'
  | 'scissors'
  | 'sneak'
  | 'eat'
  | 'accuse'
  | 'facepalm';
export type Emotion = 'happy' | 'smug' | 'shocked' | 'angry' | 'deadpan' | 'worried' | 'laughing';

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
  squash?: number;
};

type P = {x: number; y: number};

type Rig = {
  leftElbow: P;
  leftHand: P;
  rightElbow: P;
  rightHand: P;
  leftKnee: P;
  leftFoot: P;
  rightKnee: P;
  rightFoot: P;
};

const colors: Record<CharacterId, {accent: string}> = {
  kstick: {accent: '#ef2b2d'},
  zippy: {accent: '#1f78ff'},
  mimi: {accent: '#f4c430'},
};

const baseRig: Rig = {
  leftElbow: {x: 105, y: 265},
  leftHand: {x: 78, y: 325},
  rightElbow: {x: 205, y: 265},
  rightHand: {x: 232, y: 325},
  leftKnee: {x: 125, y: 415},
  leftFoot: {x: 88, y: 475},
  rightKnee: {x: 185, y: 415},
  rightFoot: {x: 222, y: 475},
};

const rigForPose = (pose: Pose, frame: number): Rig => {
  const rig: Rig = JSON.parse(JSON.stringify(baseRig));
  const run = Math.sin(frame * 0.78);
  const sway = Math.sin(frame * 0.13);

  if (pose === 'idle' || pose === 'talk') {
    rig.leftHand.x += sway * 5;
    rig.rightHand.x -= sway * 5;
  }

  if (pose === 'point' || pose === 'accuse') {
    rig.rightElbow = {x: 225, y: pose === 'accuse' ? 205 : 235};
    rig.rightHand = {x: 295, y: pose === 'accuse' ? 170 : 220};
    rig.leftHand = {x: 92, y: 330};
  }

  if (pose === 'run') {
    rig.leftElbow = {x: 120 - run * 30, y: 245 + run * 15};
    rig.leftHand = {x: 68 - run * 40, y: 280 + run * 38};
    rig.rightElbow = {x: 190 + run * 30, y: 245 - run * 15};
    rig.rightHand = {x: 242 + run * 40, y: 280 - run * 38};
    rig.leftKnee = {x: 130 + run * 46, y: 405 - Math.abs(run) * 12};
    rig.leftFoot = {x: 92 + run * 78, y: 472 - Math.max(run, 0) * 45};
    rig.rightKnee = {x: 180 - run * 46, y: 405 - Math.abs(run) * 12};
    rig.rightFoot = {x: 218 - run * 78, y: 472 - Math.max(-run, 0) * 45};
  }

  if (pose === 'shock') {
    rig.leftElbow = {x: 90, y: 225};
    rig.leftHand = {x: 55, y: 175};
    rig.rightElbow = {x: 220, y: 225};
    rig.rightHand = {x: 255, y: 175};
  }

  if (pose === 'celebrate') {
    rig.leftElbow = {x: 105, y: 205};
    rig.leftHand = {x: 72, y: 125};
    rig.rightElbow = {x: 205, y: 205};
    rig.rightHand = {x: 238, y: 125};
    rig.leftKnee = {x: 118, y: 405};
    rig.leftFoot = {x: 80, y: 465};
    rig.rightKnee = {x: 192, y: 405};
    rig.rightFoot = {x: 230, y: 465};
  }

  if (pose === 'rock' || pose === 'paper' || pose === 'scissors') {
    rig.rightElbow = {x: 220, y: 245};
    rig.rightHand = {x: 292, y: 245};
    rig.leftElbow = {x: 105, y: 270};
    rig.leftHand = {x: 82, y: 330};
  }

  if (pose === 'sneak') {
    rig.leftElbow = {x: 115, y: 250};
    rig.leftHand = {x: 145, y: 290};
    rig.rightElbow = {x: 205, y: 245};
    rig.rightHand = {x: 250, y: 285};
    rig.leftKnee = {x: 135, y: 405};
    rig.leftFoot = {x: 102, y: 458};
    rig.rightKnee = {x: 205, y: 395};
    rig.rightFoot = {x: 250, y: 450};
  }

  if (pose === 'eat') {
    rig.rightElbow = {x: 205, y: 225};
    rig.rightHand = {x: 178, y: 160};
    rig.leftElbow = {x: 120, y: 250};
    rig.leftHand = {x: 98, y: 305};
  }

  if (pose === 'facepalm') {
    rig.rightElbow = {x: 205, y: 215};
    rig.rightHand = {x: 175, y: 108};
  }

  return rig;
};

const Limb: React.FC<{a: P; b: P; c: P}> = ({a, b, c}) => (
  <g stroke="#101010" strokeWidth="13" strokeLinecap="round" strokeLinejoin="round" fill="none">
    <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} />
    <line x1={b.x} y1={b.y} x2={c.x} y2={c.y} />
  </g>
);

const SpecialHand: React.FC<{pose: Pose; hand: P}> = ({pose, hand}) => {
  if (pose === 'paper') {
    return <rect x={hand.x - 17} y={hand.y - 22} width="34" height="44" rx="10" fill="#fff" stroke="#101010" strokeWidth="7" />;
  }
  if (pose === 'scissors') {
    return (
      <g stroke="#101010" strokeWidth="8" strokeLinecap="round">
        <circle cx={hand.x} cy={hand.y + 5} r="12" fill="#fff" />
        <line x1={hand.x + 4} y1={hand.y - 3} x2={hand.x + 25} y2={hand.y - 30} />
        <line x1={hand.x + 1} y1={hand.y - 4} x2={hand.x + 4} y2={hand.y - 38} />
      </g>
    );
  }
  if (pose === 'rock') {
    return <circle cx={hand.x} cy={hand.y} r="19" fill="#fff" stroke="#101010" strokeWidth="8" />;
  }
  return <circle cx={hand.x} cy={hand.y} r="8" fill="#101010" />;
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
  squash = 0,
}) => {
  const frame = useCurrentFrame();
  const accent = colors[id].accent;
  const flip = facing === 'left' ? -1 : 1;
  const rig = rigForPose(pose, frame);

  const blinkPhase = frame % 101;
  const blink = blinkPhase >= 96 && blinkPhase <= 99;
  const idleBob = Math.sin(frame * 0.11) * (pose === 'idle' || pose === 'talk' ? 4 : 2);
  const runBob = pose === 'run' ? Math.abs(Math.sin(frame * 0.78)) * -10 : 0;
  const sneakBob = pose === 'sneak' ? Math.sin(frame * 0.25) * 5 : 0;
  const shockScale = pose === 'shock' ? interpolate(Math.sin(frame * 0.42), [-1, 1], [0.98, 1.045]) : 1;
  const celebrateBounce = pose === 'celebrate' ? Math.abs(Math.sin(frame * 0.3)) * -12 : 0;

  const mouthCycle = speaking ? Math.floor(frame / 3) % 4 : 0;
  const mouthOpen = speaking && mouthCycle !== 0;
  const mouthWide = speaking && mouthCycle === 2;

  const eyeY = emotion === 'shocked' ? 87 : emotion === 'worried' ? 96 : 92;
  const eyeRadius = emotion === 'shocked' ? 12 : emotion === 'deadpan' ? 6 : 8;
  const browTilt = emotion === 'angry' ? 15 : emotion === 'smug' ? -8 : emotion === 'worried' ? -13 : 0;
  const bodySquashY = 1 - squash * 0.08;
  const bodySquashX = 1 + squash * 0.05;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y + idleBob + runBob + sneakBob + celebrateBounce,
        width: 310,
        height: 510,
        transform: `scale(${scale * shockScale}) scaleX(${flip * bodySquashX}) scaleY(${bodySquashY}) rotate(${lean}deg)`,
        transformOrigin: '50% 92%',
        opacity,
        zIndex: 20,
      }}
    >
      <svg width="310" height="510" viewBox="0 0 310 510">
        <ellipse cx="155" cy="487" rx="85" ry="13" fill="rgba(0,0,0,.13)" />

        <Limb a={{x: 155, y: 228}} b={rig.leftElbow} c={rig.leftHand} />
        <Limb a={{x: 155, y: 228}} b={rig.rightElbow} c={rig.rightHand} />
        <Limb a={{x: 155, y: 355}} b={rig.leftKnee} c={rig.leftFoot} />
        <Limb a={{x: 155, y: 355}} b={rig.rightKnee} c={rig.rightFoot} />

        <line x1="155" y1="180" x2="155" y2="355" stroke="#101010" strokeWidth="14" strokeLinecap="round" />

        <circle cx="155" cy="105" r="72" fill="#ffffff" stroke="#101010" strokeWidth="10" />

        {!blink ? (
          <>
            <ellipse cx="129" cy={eyeY} rx={eyeRadius} ry={emotion === 'deadpan' ? 4 : eyeRadius + 1} fill="#111111" />
            <ellipse cx="181" cy={eyeY} rx={eyeRadius} ry={emotion === 'deadpan' ? 4 : eyeRadius + 1} fill="#111111" />
            {emotion !== 'deadpan' && (
              <>
                <circle cx="126" cy={eyeY - 3} r="2.8" fill="#fff" />
                <circle cx="178" cy={eyeY - 3} r="2.8" fill="#fff" />
              </>
            )}
          </>
        ) : (
          <g stroke="#111111" strokeWidth="6" strokeLinecap="round">
            <line x1="117" y1="92" x2="141" y2="92" />
            <line x1="169" y1="92" x2="193" y2="92" />
          </g>
        )}

        {(emotion === 'angry' || emotion === 'smug' || emotion === 'worried') && (
          <g stroke="#111111" strokeWidth="5" strokeLinecap="round">
            <line x1="114" y1="69" x2="141" y2={69 + browTilt} />
            <line x1="169" y1={69 + browTilt} x2="196" y2="69" />
          </g>
        )}

        {mouthOpen ? (
          mouthWide ? (
            <ellipse cx="155" cy="132" rx="20" ry="15" fill="#111111" />
          ) : (
            <ellipse cx="155" cy="132" rx="13" ry="9" fill="#111111" />
          )
        ) : emotion === 'deadpan' ? (
          <line x1="139" y1="132" x2="171" y2="132" stroke="#111111" strokeWidth="5" strokeLinecap="round" />
        ) : emotion === 'shocked' ? (
          <circle cx="155" cy="132" r="12" fill="#111111" />
        ) : emotion === 'angry' ? (
          <path d="M136 139 Q155 124 175 139" stroke="#111111" strokeWidth="5" fill="none" strokeLinecap="round" />
        ) : emotion === 'worried' ? (
          <path d="M137 139 Q155 124 173 139" stroke="#111111" strokeWidth="5" fill="none" strokeLinecap="round" />
        ) : emotion === 'laughing' ? (
          <path d="M133 126 Q155 153 178 126 Q155 162 133 126" fill="#111" />
        ) : (
          <path d="M136 126 Q155 144 175 126" stroke="#111111" strokeWidth="5" fill="none" strokeLinecap="round" />
        )}

        <SpecialHand pose={pose} hand={rig.rightHand} />
        <circle cx={rig.leftHand.x} cy={rig.leftHand.y} r="8" fill="#101010" />

        {id === 'kstick' && (
          <g>
            <path d="M92 58 Q155 10 220 58 L218 82 Q155 54 94 82 Z" fill={accent} stroke="#101010" strokeWidth="8" />
            <path d="M215 64 Q254 65 266 82 Q234 86 212 80 Z" fill={accent} stroke="#101010" strokeWidth="7" />
          </g>
        )}

        {id === 'zippy' && (
          <g stroke={accent} strokeWidth="8" fill="none">
            <rect x="104" y="73" width="44" height="32" rx="12" />
            <rect x="162" y="73" width="44" height="32" rx="12" />
            <line x1="148" y1="89" x2="162" y2="89" />
          </g>
        )}

        {id === 'mimi' && (
          <g>
            <path d="M92 53 Q155 25 220 53" stroke={accent} strokeWidth="14" fill="none" strokeLinecap="round" />
            <circle cx="155" cy="42" r="12" fill={accent} stroke="#101010" strokeWidth="5" />
          </g>
        )}
      </svg>
    </div>
  );
};

import React from 'react';
import {Composition} from 'remotion';
import {KStickComedyV22} from './KStickComedyV22';
import episode from './data/episode.json';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="KStickV2"
      component={KStickComedyV22}
      durationInFrames={Math.round(episode.durationSeconds * 30)}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};

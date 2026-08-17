import React from 'react';
import {Composition} from 'remotion';
import {KStickComedy} from './KStickComedy';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="KStickV2"
      component={KStickComedy}
      durationInFrames={24 * 30}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};

import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

interface Props {
  forestId: number;
}

const Forest3D: React.FC<Props> = ({ forestId }) => {
  return (
    <Canvas className="h-full w-full">
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} />

      {/* Example tree */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.3, 0.3, 2]} />
        <meshStandardMaterial color="brown" />
      </mesh>
      <mesh position={[0, 1.5, 0]}>
        <coneGeometry args={[1, 2, 8]} />
        <meshStandardMaterial color="green" />
      </mesh>

      <OrbitControls />
    </Canvas>
  );
};

export default Forest3D;

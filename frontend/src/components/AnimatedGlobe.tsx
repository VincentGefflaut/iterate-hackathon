import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, useTexture } from '@react-three/drei';
import * as THREE from 'three';

function Globe() {
  const meshRef = useRef<THREE.Mesh>(null);
  const particlesRef = useRef<THREE.Points>(null);

  const continentTexture = useTexture('/map-continents.png');

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.1;
    }
    if (particlesRef.current) {
      particlesRef.current.rotation.y -= 0.001;
    }
  });

  // Create particle system for stars
  const particlesGeometry = new THREE.BufferGeometry();
  const particlesCount = 1000;
  const posArray = new Float32Array(particlesCount * 3);

  for (let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 10;
  }

  particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

  return (
    <>
      {/* Particle stars */}
      <points ref={particlesRef} geometry={particlesGeometry}>
        <pointsMaterial size={0.02} color="#ADD8E6" transparent opacity={0.6} />
      </points>

      {/* Main globe */}
      <Sphere ref={meshRef} args={[1.5, 64, 64]}>
        <meshStandardMaterial
          color="#87CEEB"
          map={continentTexture}
          emissive="#FFFFFF"
          emissiveMap={continentTexture}
          emissiveIntensity={1.0}
          roughness={0.7}
          metalness={0.1}
        />
      </Sphere>

      {/* Glowing outer sphere */}
      <Sphere args={[1.6, 32, 32]}>
        <meshBasicMaterial
          color="#ADD8E6"
          transparent
          opacity={0.15}
          side={THREE.BackSide}
        />
      </Sphere>

      {/* Ambient light */}
      <ambientLight intensity={0.8} />
      
      {/* Main light */}
      <directionalLight position={[5, 5, 5]} intensity={1.5} color="#FFFFFF" />
      <directionalLight position={[-5, -5, -5]} intensity={0.7} color="#ADD8E6" />
    </>
  );
}

export default function AnimatedGlobe() {
  return (
    <div className="w-full h-full">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <Globe />
        <OrbitControls 
          enableZoom={false} 
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  );
}

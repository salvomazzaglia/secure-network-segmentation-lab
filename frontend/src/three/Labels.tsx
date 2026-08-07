import { Html } from '@react-three/drei';

interface Props {
  text: string;
  position?: [number, number, number];
}

export function Labels({ text, position = [0, 4.5, 0] }: Props) {
  return (
    <Html position={position} center style={{ pointerEvents: 'none' }}>
      <div
        style={{
          color: '#9bb6bc',
          fontFamily: 'Segoe UI, Helvetica Neue, sans-serif',
          fontSize: '12px',
          whiteSpace: 'nowrap',
          background: 'rgba(7,19,22,0.7)',
          padding: '4px 8px',
          borderRadius: 6,
          border: '1px solid rgba(94,168,178,0.3)',
        }}
      >
        {text}
      </div>
    </Html>
  );
}

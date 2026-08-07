import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

afterEach(() => {
  cleanup();
});

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

vi.stubGlobal('ResizeObserver', ResizeObserverStub);

vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="r3f-canvas">{children}</div>
  ),
  useThree: () => ({
    camera: { position: { set: vi.fn() } },
    controls: { target: { set: vi.fn() }, update: vi.fn() },
  }),
}));

vi.mock('@react-three/drei', () => ({
  OrbitControls: () => null,
  PerspectiveCamera: () => null,
  Html: ({ children }: { children?: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('../src/three/NetworkScene', () => ({
  NetworkScene: () => <div data-testid="network-scene">mocked-scene</div>,
}));

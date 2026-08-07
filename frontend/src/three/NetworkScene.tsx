import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { useEffect, useMemo } from 'react';
import type { Device, Topology, ViewMode } from '../models';
import { DeviceNode } from './DeviceNode';
import { WiredEdge } from './WiredEdge';
import { WirelessAssociation } from './WirelessAssociation';
import { WirelessCoverage } from './WirelessCoverage';
import { SegmentZone } from './SegmentZone';
import { PolicyEdge } from './PolicyEdge';
import { Labels } from './Labels';
import { layoutAll, type LayoutPosition } from './LayoutEngine';

interface SceneProps {
  devices: Device[];
  topology: Topology;
  viewMode: ViewMode;
  selectedDeviceId: string | null;
  reducedMotion: boolean;
  cameraCommand: 'none' | 'fit' | 'reset' | 'focus';
  onSelect: (id: string) => void;
  onCameraHandled: () => void;
}

function CameraController({
  command,
  focus,
  onHandled,
}: {
  command: SceneProps['cameraCommand'];
  focus: LayoutPosition | null;
  onHandled: () => void;
}) {
  const { camera, controls } = useThree((s) => ({
    camera: s.camera,
    controls: s.controls as {
      target: { set: (x: number, y: number, z: number) => void };
      update: () => void;
    } | null,
  }));

  useEffect(() => {
    if (command === 'none') return;
    if (command === 'reset' || command === 'fit') {
      camera.position.set(10, 12, 14);
      controls?.target.set(0, 0, 0);
      controls?.update();
    }
    if (command === 'focus' && focus) {
      camera.position.set(focus.x + 4, focus.y + 5, focus.z + 4);
      controls?.target.set(focus.x, focus.y, focus.z);
      controls?.update();
    }
    onHandled();
  }, [command, focus, camera, controls, onHandled]);

  return null;
}

function SceneContent(props: SceneProps) {
  const {
    devices,
    topology,
    viewMode,
    selectedDeviceId,
    reducedMotion,
    cameraCommand,
    onSelect,
    onCameraHandled,
  } = props;

  const positions = useMemo(() => layoutAll(devices, viewMode), [devices, viewMode]);
  const byId = useMemo(() => new Map(devices.map((d) => [d.device_id, d])), [devices]);
  const focus = selectedDeviceId ? (positions.get(selectedDeviceId) ?? null) : null;

  const showZones = viewMode === 'SEGMENTATION';
  const showWireless = viewMode === 'WIRELESS' || viewMode === 'TOPOLOGY';
  const showPolicy = viewMode === 'POLICY_REACHABILITY';
  const showServices = viewMode === 'SERVICES';

  const segments = Array.from(new Set(devices.map((d) => d.current_segment)));

  return (
    <>
      <PerspectiveCamera makeDefault position={[10, 12, 14]} />
      <ambientLight intensity={0.55} />
      <directionalLight position={[8, 14, 6]} intensity={0.85} />
      <gridHelper args={[40, 40, '#1c3a42', '#12262e']} />
      <OrbitControls makeDefault enableDamping={!reducedMotion} />
      <CameraController command={cameraCommand} focus={focus} onHandled={onCameraHandled} />
      <Labels text={`Mode: ${viewMode}`} />

      {showZones && segments.map((s) => <SegmentZone key={s} segmentId={s} visible />)}

      {devices
        .filter((d) => d.device_class === 'access_point')
        .map((ap) => {
          const pos = positions.get(ap.device_id);
          if (!pos || !showWireless) return null;
          return (
            <WirelessCoverage
              key={`cov-${ap.device_id}`}
              position={pos}
              reducedMotion={reducedMotion}
            />
          );
        })}

      {topology.edges.map((edge) => {
        const from = positions.get(edge.source_id);
        const to = positions.get(edge.target_id);
        if (!from || !to) return null;
        if (
          edge.edge_type === 'wired' &&
          (viewMode === 'TOPOLOGY' || viewMode === 'SEGMENTATION' || viewMode === 'SERVICES')
        ) {
          return <WiredEdge key={edge.edge_id} from={from} to={to} />;
        }
        if (edge.edge_type === 'wireless_association' && showWireless) {
          const client = byId.get(edge.target_id);
          return (
            <WirelessAssociation
              key={edge.edge_id}
              from={from}
              to={to}
              signal={client?.signal_bucket}
            />
          );
        }
        if (edge.edge_type === 'policy' && showPolicy) {
          return (
            <PolicyEdge key={edge.edge_id} from={from} to={to} allowed={edge.allowed === true} />
          );
        }
        return null;
      })}

      {devices.map((device) => {
        const pos = positions.get(device.device_id);
        if (!pos) return null;
        if (
          showServices &&
          device.services.length === 0 &&
          device.device_class !== 'access_point'
        ) {
          // Still show nodes but dim via selection styling later
        }
        return (
          <DeviceNode
            key={device.device_id}
            device={device}
            position={pos}
            selected={device.device_id === selectedDeviceId}
            viewMode={viewMode}
            reducedMotion={reducedMotion}
            onSelect={onSelect}
          />
        );
      })}
    </>
  );
}

export function NetworkScene(props: SceneProps) {
  return (
    <div className="scene-wrap" data-testid="network-scene">
      <Canvas
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true }}
        onCreated={({ gl }) => {
          gl.setClearColor('#081418', 1);
        }}
      >
        <SceneContent {...props} />
      </Canvas>
    </div>
  );
}

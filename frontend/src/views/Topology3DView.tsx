import { Filters } from '../components/Filters';
import { Legend } from '../components/Legend';
import { Disclaimers } from '../components/Disclaimers';
import { NetworkScene } from '../three/NetworkScene';
import { VIEW_MODES } from '../models';
import { filterDevices, useAppState } from '../state/appState';

export function Topology3DView() {
  const { state, dispatch } = useAppState();
  const lab = state.lab;

  if (!lab) return <div className="empty-state">No topology loaded</div>;

  const devices = filterDevices(lab.devices, state.filters);

  return (
    <section aria-labelledby="topo-title" data-testid="topology-view">
      <h2 id="topo-title">3D Topology</h2>
      <p className="muted">
        Logical security map. Spatial placement is illustrative — not measured physical location.
      </p>
      <div className="toolbar" role="toolbar" aria-label="View modes">
        {VIEW_MODES.map((mode) => (
          <button
            key={mode}
            type="button"
            aria-pressed={state.viewMode === mode}
            data-testid={`view-mode-${mode}`}
            onClick={() => dispatch({ type: 'SET_VIEW_MODE', viewMode: mode })}
          >
            {mode.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div style={{ height: '0.65rem' }} />
      <div className="toolbar" role="toolbar" aria-label="Camera controls">
        <span className="muted" data-testid="camera-orbit-hint">
          Orbit / zoom / pan
        </span>
        <button
          type="button"
          onClick={() => dispatch({ type: 'SET_CAMERA_COMMAND', command: 'fit' })}
        >
          Fit
        </button>
        <button
          type="button"
          onClick={() => dispatch({ type: 'SET_CAMERA_COMMAND', command: 'focus' })}
          disabled={!state.selectedDeviceId}
        >
          Focus
        </button>
        <button
          type="button"
          onClick={() => dispatch({ type: 'SET_CAMERA_COMMAND', command: 'reset' })}
        >
          Reset
        </button>
      </div>
      <div style={{ height: '0.65rem' }} />
      <Filters devices={lab.devices} />
      <div style={{ height: '0.65rem' }} />
      <Legend />
      <div style={{ height: '0.65rem' }} />
      {devices.length === 0 ? (
        <div className="empty-state" data-testid="empty-topology">
          No devices match the current filters.
        </div>
      ) : (
        <NetworkScene
          devices={devices}
          topology={lab.topology}
          viewMode={state.viewMode}
          selectedDeviceId={state.selectedDeviceId}
          reducedMotion={state.reducedMotion}
          cameraCommand={state.cameraCommand}
          onSelect={(id) => dispatch({ type: 'SELECT_DEVICE', deviceId: id })}
          onCameraHandled={() => dispatch({ type: 'SET_CAMERA_COMMAND', command: 'none' })}
        />
      )}
      <div style={{ height: '0.65rem' }} />
      <Disclaimers />
    </section>
  );
}

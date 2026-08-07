import { ApprovalDialog } from '../components/ApprovalDialog';
import { useAppState } from '../state/appState';

export function DeviceDetailView() {
  const { state, dispatch } = useAppState();
  const lab = state.lab;
  const device = lab?.devices.find((d) => d.device_id === state.selectedDeviceId) ?? null;

  if (!device) {
    return (
      <div className="empty-state" data-testid="empty-device-detail">
        Select a device from inventory or the 3D map.
      </div>
    );
  }

  const classification = lab?.classifications.find((c) => c.device_id === device.device_id);
  const evidence = device.evidence ?? classification?.evidence ?? [];
  const deviceEvents = state.events.filter((e) => e.device_id === device.device_id);
  const reachability =
    lab?.reachability.paths.filter((p) => p.source_device_id === device.device_id) ?? [];

  return (
    <section aria-labelledby="dev-title" data-testid="device-detail-view">
      <div className="toolbar">
        <button
          type="button"
          className="btn"
          onClick={() => dispatch({ type: 'SET_APP_VIEW', appView: 'inventory' })}
        >
          Back to inventory
        </button>
        {device.awaiting_approval && (
          <button
            type="button"
            className="btn btn-primary"
            data-testid="open-approval"
            onClick={() => dispatch({ type: 'SET_APPROVAL_OPEN', open: true })}
          >
            Open synthetic approval
          </button>
        )}
      </div>
      <h2 id="dev-title">{device.alias}</h2>
      {device.quarantined && (
        <span className="badge badge-quarantine" data-testid="quarantine-badge">
          Quarantined
        </span>
      )}
      <div style={{ height: '0.75rem' }} />
      <dl className="detail-grid panel">
        <div className="kv">
          <dt>MAC</dt>
          <dd>{device.mac}</dd>
        </div>
        <div className="kv">
          <dt>IPv4</dt>
          <dd>{device.ipv4 ?? '—'}</dd>
        </div>
        <div className="kv">
          <dt>Class</dt>
          <dd>{device.device_class}</dd>
        </div>
        <div className="kv">
          <dt>Confidence</dt>
          <dd data-testid="confidence-value">{device.confidence.toFixed(2)}</dd>
        </div>
        <div className="kv">
          <dt>Classification status</dt>
          <dd>{device.classification_status}</dd>
        </div>
        <div className="kv">
          <dt>Current segment</dt>
          <dd>{device.current_segment}</dd>
        </div>
        <div className="kv">
          <dt>Recommended segment</dt>
          <dd>{device.recommended_segment}</dd>
        </div>
        <div className="kv">
          <dt>Policy decision</dt>
          <dd>{device.policy_decision ?? '—'}</dd>
        </div>
        <div className="kv">
          <dt>Security state</dt>
          <dd>{device.security_state}</dd>
        </div>
        <div className="kv">
          <dt>Connection</dt>
          <dd>{device.connection_type}</dd>
        </div>
        <div className="kv">
          <dt>Switch / AP</dt>
          <dd>{device.switch_id ?? device.ap_id ?? '—'}</dd>
        </div>
        <div className="kv">
          <dt>SSID</dt>
          <dd>{device.ssid ?? '—'}</dd>
        </div>
        <div className="kv">
          <dt>Signal bucket</dt>
          <dd data-testid="signal-bucket">{device.signal_bucket ?? '—'}</dd>
        </div>
        <div className="kv">
          <dt>First seen</dt>
          <dd>{device.first_seen_utc}</dd>
        </div>
        <div className="kv">
          <dt>Last seen</dt>
          <dd>{device.last_seen_utc}</dd>
        </div>
        <div className="kv">
          <dt>Provenance</dt>
          <dd>{device.provenance}</dd>
        </div>
      </dl>

      <div className="panel" data-testid="confidence-explanation">
        <h3>Why classified?</h3>
        <p className="muted">
          Confidence is a normalized heuristic evidence score — not a statistical probability.
        </p>
        {evidence.length === 0 ? (
          <div className="empty-state">No evidence items</div>
        ) : (
          <table className="data-table" aria-label="Classification evidence">
            <thead>
              <tr>
                <th scope="col">Source</th>
                <th scope="col">Weight</th>
                <th scope="col">Contribution</th>
                <th scope="col">Detail</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((ev) => (
                <tr key={`${ev.source}-${ev.detail}`}>
                  <td>{ev.source}</td>
                  <td>{ev.weight.toFixed(2)}</td>
                  <td>{ev.contribution.toFixed(2)}</td>
                  <td>{ev.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="panel">
        <h3>Observed services</h3>
        {device.services.length === 0 ? (
          <div className="empty-state">No services</div>
        ) : (
          <ul>
            {device.services.map((s) => (
              <li key={s.service_id}>
                {s.category}
                {s.port != null ? ` :${s.port}` : ''} · provenance {s.provenance}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="panel">
        <h3>Policy reachability</h3>
        {reachability.length === 0 ? (
          <div className="empty-state">No device-scoped paths</div>
        ) : (
          <ul>
            {reachability.map((p) => (
              <li key={p.path_id}>{p.explanation}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="panel">
        <h3>Event history</h3>
        {deviceEvents.length === 0 ? (
          <div className="empty-state">No events for device</div>
        ) : (
          <ul>
            {deviceEvents.map((e) => (
              <li key={e.event_id}>
                <code>{e.event_type}</code> — {e.message}
              </li>
            ))}
          </ul>
        )}
      </div>

      <ApprovalDialog device={device} />
    </section>
  );
}

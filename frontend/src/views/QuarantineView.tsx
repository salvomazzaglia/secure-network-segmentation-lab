import { useAppState } from '../state/appState';

export function QuarantineView() {
  const { state, dispatch } = useAppState();
  const lab = state.lab;
  if (!lab) return <div className="empty-state">No quarantine data</div>;

  const quarantined = lab.devices.filter(
    (d) => d.quarantined || d.current_segment === 'quarantine',
  );

  return (
    <section aria-labelledby="q-title" data-testid="quarantine-view">
      <h2 id="q-title">Quarantine</h2>
      <p className="muted">
        Logical isolation model only. Quarantine may use DHCP/DNS/NTP; east-west and privileged
        segments are denied in the intended policy.
      </p>
      {quarantined.length === 0 ? (
        <div className="empty-state" data-testid="empty-quarantine">
          No quarantined devices.
        </div>
      ) : (
        <div className="panel">
          <ul>
            {quarantined.map((d) => (
              <li key={d.device_id} style={{ marginBottom: '0.65rem' }}>
                <button
                  type="button"
                  className="btn"
                  onClick={() => dispatch({ type: 'SELECT_DEVICE', deviceId: d.device_id })}
                >
                  {d.alias}
                </button>{' '}
                <span className="badge badge-quarantine" data-testid="quarantine-badge">
                  Quarantined
                </span>{' '}
                <span className="muted">
                  confidence {d.confidence.toFixed(2)} · {d.classification_status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

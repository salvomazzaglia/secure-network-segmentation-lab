import { Filters } from '../components/Filters';
import { filterDevices, useAppState } from '../state/appState';

export function InventoryView() {
  const { state, dispatch } = useAppState();
  const lab = state.lab;
  if (!lab) return <div className="empty-state">No inventory</div>;

  const devices = filterDevices(lab.devices, state.filters);

  return (
    <section aria-labelledby="inv-title" data-testid="inventory-view">
      <h2 id="inv-title">Inventory</h2>
      <p className="muted">Synthetic device inventory — documentation IPs and LAA MACs only.</p>
      <Filters devices={lab.devices} />
      <div style={{ height: '0.75rem' }} />
      {devices.length === 0 ? (
        <div className="empty-state" data-testid="empty-inventory">
          No devices match the current filters.
        </div>
      ) : (
        <div className="panel" style={{ overflowX: 'auto' }}>
          <table className="data-table" aria-label="Device inventory">
            <thead>
              <tr>
                <th scope="col">Alias</th>
                <th scope="col">MAC</th>
                <th scope="col">Class</th>
                <th scope="col">Segment</th>
                <th scope="col">Confidence</th>
                <th scope="col">State</th>
                <th scope="col">Link</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((d) => (
                <tr
                  key={d.device_id}
                  tabIndex={0}
                  aria-selected={state.selectedDeviceId === d.device_id}
                  onClick={() => dispatch({ type: 'SELECT_DEVICE', deviceId: d.device_id })}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      dispatch({ type: 'SELECT_DEVICE', deviceId: d.device_id });
                    }
                  }}
                >
                  <td>{d.alias}</td>
                  <td>
                    <code>{d.mac}</code>
                  </td>
                  <td>{d.device_class}</td>
                  <td>{d.current_segment}</td>
                  <td>{d.confidence.toFixed(2)}</td>
                  <td>
                    {d.quarantined && (
                      <span className="badge badge-quarantine" data-testid="quarantine-badge">
                        Quarantined
                      </span>
                    )}{' '}
                    {d.security_state}
                  </td>
                  <td>{d.connection_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

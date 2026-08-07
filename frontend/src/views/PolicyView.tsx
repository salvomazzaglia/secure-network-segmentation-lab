import { useAppState } from '../state/appState';

export function PolicyView() {
  const { state, dispatch } = useAppState();
  const lab = state.lab;
  if (!lab) return <div className="empty-state">No policy data</div>;

  return (
    <section aria-labelledby="pol-title" data-testid="policy-view">
      <h2 id="pol-title">Policy decisions</h2>
      <p className="muted">PROPOSED / SIMULATED — NOT APPLIED</p>
      {lab.policy_decisions.length === 0 ? (
        <div className="empty-state">No policy decisions</div>
      ) : (
        <div className="panel" style={{ overflowX: 'auto' }}>
          <table className="data-table" aria-label="Policy decisions">
            <thead>
              <tr>
                <th scope="col">Device</th>
                <th scope="col">Rule</th>
                <th scope="col">Current</th>
                <th scope="col">Recommended</th>
                <th scope="col">Decision</th>
                <th scope="col">Approval</th>
              </tr>
            </thead>
            <tbody>
              {lab.policy_decisions.map((pd) => (
                <tr
                  key={pd.decision_id}
                  tabIndex={0}
                  onClick={() => dispatch({ type: 'SELECT_DEVICE', deviceId: pd.device_id })}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      dispatch({ type: 'SELECT_DEVICE', deviceId: pd.device_id });
                    }
                  }}
                >
                  <td>{pd.device_id}</td>
                  <td>{pd.matched_rule}</td>
                  <td>{pd.current_segment}</td>
                  <td>{pd.recommended_segment}</td>
                  <td>{pd.decision}</td>
                  <td>{pd.approval_required ? 'required' : 'not required'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div style={{ height: '0.85rem' }} />
      <h3>Drift findings</h3>
      {lab.drift.length === 0 ? (
        <div className="empty-state">No drift findings</div>
      ) : (
        <div className="panel">
          <ul>
            {lab.drift.map((f) => (
              <li key={f.finding_id}>
                <span className="badge badge-warn">{f.severity}</span> {f.summary}
                <div className="muted">{f.detail}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

import { Disclaimers } from '../components/Disclaimers';
import { useAppState } from '../state/appState';

export function ReachabilityView() {
  const { state } = useAppState();
  const lab = state.lab;
  if (!lab) return <div className="empty-state">No reachability data</div>;

  const paths = lab.reachability.paths;

  return (
    <section aria-labelledby="rch-title" data-testid="reachability-view">
      <h2 id="rch-title">Reachability</h2>
      <p className="muted">{lab.reachability.note}</p>
      {paths.length === 0 ? (
        <div className="empty-state">No reachability paths</div>
      ) : (
        <div className="panel" style={{ overflowX: 'auto' }}>
          <table className="data-table" aria-label="Reachability paths">
            <thead>
              <tr>
                <th scope="col">Source</th>
                <th scope="col">Destination</th>
                <th scope="col">Service</th>
                <th scope="col">Decision</th>
                <th scope="col">Explanation</th>
              </tr>
            </thead>
            <tbody>
              {paths.map((p) => (
                <tr key={p.path_id}>
                  <td>{p.source_segment}</td>
                  <td>{p.destination_segment}</td>
                  <td>{p.service}</td>
                  <td>
                    <span
                      className={`badge ${
                        p.decision === 'allowed'
                          ? 'badge-ok'
                          : p.decision === 'denied'
                            ? 'badge-danger'
                            : 'badge-warn'
                      }`}
                    >
                      {p.decision}
                    </span>
                  </td>
                  <td>{p.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div style={{ height: '0.75rem' }} />
      <Disclaimers showWireless={false} />
    </section>
  );
}

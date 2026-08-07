import { useAppState } from '../state/appState';

export function EventsView() {
  const { state, dispatch } = useAppState();
  const events = state.events;

  return (
    <section aria-labelledby="evt-title" data-testid="events-view">
      <h2 id="evt-title">Events</h2>
      <p className="muted">
        WebSocket status: <code data-testid="ws-status">{state.wsStatus}</code>
      </p>
      {events.length === 0 ? (
        <div className="empty-state" data-testid="empty-events">
          No events yet.
        </div>
      ) : (
        <div className="panel" style={{ overflowX: 'auto' }}>
          <table className="data-table" aria-label="Lab events">
            <thead>
              <tr>
                <th scope="col">Time</th>
                <th scope="col">Type</th>
                <th scope="col">Device</th>
                <th scope="col">Message</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr
                  key={e.event_id}
                  tabIndex={e.device_id ? 0 : undefined}
                  onClick={() => {
                    if (e.device_id) dispatch({ type: 'SELECT_DEVICE', deviceId: e.device_id });
                  }}
                  onKeyDown={(ev) => {
                    if ((ev.key === 'Enter' || ev.key === ' ') && e.device_id) {
                      ev.preventDefault();
                      dispatch({ type: 'SELECT_DEVICE', deviceId: e.device_id });
                    }
                  }}
                >
                  <td>
                    <code>{e.created_at_utc}</code>
                  </td>
                  <td>{e.event_type}</td>
                  <td>{e.device_id ?? '—'}</td>
                  <td>{e.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

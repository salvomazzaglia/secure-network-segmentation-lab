import { useAppState } from '../state/appState';
import { segmentColor } from '../three/LayoutEngine';

export function SegmentationView() {
  const { state, dispatch } = useAppState();
  const lab = state.lab;
  if (!lab) return <div className="empty-state">No segments</div>;

  const groups = lab.segments.map((seg) => ({
    segment: seg,
    devices: lab.devices.filter((d) => d.current_segment === seg.segment_id),
  }));

  return (
    <section aria-labelledby="seg-title" data-testid="segmentation-view">
      <h2 id="seg-title">Segmentation</h2>
      <p className="muted">
        Classification and segmentation are separate. VLAN IDs are synthetic examples only.
      </p>
      <div className="chart-grid">
        {groups.map(({ segment, devices }) => (
          <div className="panel" key={segment.segment_id}>
            <h3 style={{ color: segmentColor(segment.segment_id) }}>
              {segment.label}{' '}
              <span className="muted" style={{ fontSize: '0.8rem' }}>
                VLAN {segment.vlan_id} — {segment.vlan_note}
              </span>
            </h3>
            <p className="muted">
              {segment.logical_prefix}
              {segment.demo_ipv4_map ? ` · ${segment.demo_ipv4_map}` : ''}
            </p>
            {devices.length === 0 ? (
              <div className="empty-state">No devices in segment</div>
            ) : (
              <ul>
                {devices.map((d) => (
                  <li key={d.device_id}>
                    <button
                      type="button"
                      className="btn"
                      onClick={() => dispatch({ type: 'SELECT_DEVICE', deviceId: d.device_id })}
                    >
                      {d.alias}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

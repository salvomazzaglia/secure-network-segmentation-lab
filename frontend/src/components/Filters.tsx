import type { Device } from '../models';
import { useAppState } from '../state/appState';

interface Props {
  devices: Device[];
}

export function Filters({ devices }: Props) {
  const { state, dispatch } = useAppState();
  const { filters } = state;
  const aps = Array.from(
    new Set(devices.filter((d) => d.device_class === 'access_point').map((d) => d.device_id)),
  );
  const classes = Array.from(new Set(devices.map((d) => d.device_class))).sort();
  const segments = Array.from(new Set(devices.map((d) => d.current_segment))).sort();
  const services = Array.from(
    new Set(devices.flatMap((d) => d.services.map((s) => s.category))),
  ).sort();
  const securityStates = Array.from(new Set(devices.map((d) => d.security_state))).sort();

  return (
    <form
      className="panel filters"
      data-testid="filters"
      aria-label="Device filters"
      onSubmit={(e) => e.preventDefault()}
    >
      <label>
        Segment
        <select
          value={filters.segment}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { segment: e.target.value as typeof filters.segment },
            })
          }
          aria-label="Filter by segment"
        >
          <option value="all">All</option>
          {segments.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <label>
        Class
        <select
          value={filters.deviceClass}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { deviceClass: e.target.value as typeof filters.deviceClass },
            })
          }
          aria-label="Filter by class"
        >
          <option value="all">All</option>
          {classes.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </label>
      <label>
        Connection
        <select
          value={filters.connection}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { connection: e.target.value as typeof filters.connection },
            })
          }
          aria-label="Filter by connection"
        >
          <option value="all">All</option>
          <option value="wired">Wired</option>
          <option value="wireless">Wireless</option>
        </select>
      </label>
      <label>
        Online
        <select
          value={filters.online}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { online: e.target.value as typeof filters.online },
            })
          }
          aria-label="Filter by online status"
        >
          <option value="all">All</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
        </select>
      </label>
      <label>
        Confidence min
        <input
          type="number"
          min={0}
          max={1}
          step={0.05}
          value={filters.confidenceMin}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { confidenceMin: Number(e.target.value) },
            })
          }
          aria-label="Minimum confidence"
        />
      </label>
      <label>
        Confidence max
        <input
          type="number"
          min={0}
          max={1}
          step={0.05}
          value={filters.confidenceMax}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { confidenceMax: Number(e.target.value) },
            })
          }
          aria-label="Maximum confidence"
        />
      </label>
      <label>
        Security state
        <select
          value={filters.securityState}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { securityState: e.target.value as typeof filters.securityState },
            })
          }
          aria-label="Filter by security state"
        >
          <option value="all">All</option>
          {securityStates.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <label>
        Access point
        <select
          value={filters.apId}
          onChange={(e) => dispatch({ type: 'SET_FILTERS', filters: { apId: e.target.value } })}
          aria-label="Filter by access point"
        >
          <option value="all">All</option>
          {aps.map((id) => (
            <option key={id} value={id}>
              {id}
            </option>
          ))}
        </select>
      </label>
      <label>
        Service
        <select
          value={filters.serviceCategory}
          onChange={(e) =>
            dispatch({
              type: 'SET_FILTERS',
              filters: { serviceCategory: e.target.value as typeof filters.serviceCategory },
            })
          }
          aria-label="Filter by service"
        >
          <option value="all">All</option>
          {services.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <button type="button" className="btn" onClick={() => dispatch({ type: 'RESET_FILTERS' })}>
        Reset filters
      </button>
    </form>
  );
}

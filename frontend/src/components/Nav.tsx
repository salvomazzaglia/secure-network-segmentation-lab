import type { AppView } from '../models';
import { useAppState } from '../state/appState';

const ITEMS: { id: AppView; label: string }[] = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'topology', label: '3D Topology' },
  { id: 'segmentation', label: 'Segmentation' },
  { id: 'reachability', label: 'Reachability' },
  { id: 'inventory', label: 'Inventory' },
  { id: 'quarantine', label: 'Quarantine' },
  { id: 'policy', label: 'Policy' },
  { id: 'events', label: 'Events' },
];

export function Nav() {
  const { state, dispatch } = useAppState();

  return (
    <nav className="nav" aria-label="Primary">
      <p className="nav-brand">
        SNS Lab
        <span>Secure Network Segmentation</span>
      </p>
      {ITEMS.map((item) => (
        <button
          key={item.id}
          type="button"
          aria-current={state.appView === item.id ? 'page' : undefined}
          onClick={() => dispatch({ type: 'SET_APP_VIEW', appView: item.id })}
        >
          {item.label}
        </button>
      ))}
    </nav>
  );
}

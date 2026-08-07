import type { ReactNode } from 'react';
import { Banner } from './components/Banner';
import { Nav } from './components/Nav';
import { useApi } from './hooks/useApi';
import { useEvents } from './hooks/useEvents';
import { useReducedMotion } from './hooks/useReducedMotion';
import { useAppState } from './state/appState';
import { WIRELESS_DISCLAIMER } from './models';
import { DashboardView } from './views/DashboardView';
import { Topology3DView } from './views/Topology3DView';
import { SegmentationView } from './views/SegmentationView';
import { ReachabilityView } from './views/ReachabilityView';
import { InventoryView } from './views/InventoryView';
import { QuarantineView } from './views/QuarantineView';
import { PolicyView } from './views/PolicyView';
import { EventsView } from './views/EventsView';
import { DeviceDetailView } from './views/DeviceDetailView';

function AppContent() {
  useApi();
  useEvents(true);
  const reduced = useReducedMotion();
  const { state } = useAppState();

  let body: ReactNode;
  switch (state.appView) {
    case 'dashboard':
      body = <DashboardView />;
      break;
    case 'topology':
      body = <Topology3DView />;
      break;
    case 'segmentation':
      body = <SegmentationView />;
      break;
    case 'reachability':
      body = <ReachabilityView />;
      break;
    case 'inventory':
      body = <InventoryView />;
      break;
    case 'quarantine':
      body = <QuarantineView />;
      break;
    case 'policy':
      body = <PolicyView />;
      break;
    case 'events':
      body = <EventsView />;
      break;
    case 'device':
      body = <DeviceDetailView />;
      break;
    default:
      body = <DashboardView />;
  }

  return (
    <div className={`app-shell${reduced ? ' reduce-motion' : ''}`} data-testid="app-root">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <Nav />
      <div className="main-column">
        <Banner />
        <p
          className="disclaimer"
          data-testid="wireless-disclaimer-global"
          style={{ margin: 0, borderRadius: 0 }}
        >
          {WIRELESS_DISCLAIMER}
        </p>
        <main id="main-content" className="content" tabIndex={-1}>
          {state.loading && (
            <p className="loading-pulse muted" data-testid="loading">
              Loading synthetic lab…
            </p>
          )}
          {state.error && (
            <div className="error-banner" role="alert" data-testid="api-error">
              API notice: {state.error}. Showing synthetic fallback data.
            </div>
          )}
          {body}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return <AppContent />;
}

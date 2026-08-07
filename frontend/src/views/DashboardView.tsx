import { SummaryCards, SummaryCharts } from '../components/SummaryCards';
import { Disclaimers } from '../components/Disclaimers';
import { computeSummary } from '../data/mockLab';
import { useAppState } from '../state/appState';

export function DashboardView() {
  const { state } = useAppState();
  const lab = state.lab;
  if (!lab) {
    return <div className="empty-state">Loading lab snapshot…</div>;
  }

  const summary = computeSummary(lab.devices, state.events);

  return (
    <section aria-labelledby="dashboard-title" data-testid="dashboard-view">
      <h2 id="dashboard-title">Dashboard</h2>
      <p className="muted">Synthetic security operations overview — no live network telemetry.</p>
      <SummaryCards summary={summary} />
      <div style={{ height: '0.85rem' }} />
      <SummaryCharts summary={summary} />
      <div style={{ height: '0.85rem' }} />
      <Disclaimers />
      {state.fromMock && (
        <p className="muted" data-testid="mock-notice">
          Using local synthetic fallback data (API unavailable or offline test mode).
        </p>
      )}
    </section>
  );
}

import type { LabSummary } from '../models';

const CARDS: { key: keyof LabSummary; label: string }[] = [
  { key: 'total', label: 'Total' },
  { key: 'online', label: 'Online' },
  { key: 'unknown', label: 'Unknown' },
  { key: 'quarantined', label: 'Quarantined' },
  { key: 'awaiting_approval', label: 'Awaiting approval' },
  { key: 'policy_violations', label: 'Policy violations' },
  { key: 'wired', label: 'Wired' },
  { key: 'wireless', label: 'Wireless' },
];

interface Props {
  summary: LabSummary;
}

export function SummaryCards({ summary }: Props) {
  return (
    <div className="summary-grid" data-testid="summary-cards" role="list" aria-label="Lab counters">
      {CARDS.map((card) => (
        <div
          className="summary-card"
          role="listitem"
          key={card.key}
          data-testid={`card-${card.key}`}
        >
          <div className="label">{card.label}</div>
          <div className="value">{summary[card.key] as number}</div>
        </div>
      ))}
    </div>
  );
}

function BarChart({
  title,
  data,
  testId,
}: {
  title: string;
  data: Record<string, number>;
  testId: string;
}) {
  const entries = Object.entries(data);
  const max = Math.max(1, ...entries.map(([, v]) => v));
  const width = 280;
  const barH = 16;
  const gap = 8;
  const height = Math.max(40, entries.length * (barH + gap));

  return (
    <div className="panel chart-card" data-testid={testId}>
      <h3>{title}</h3>
      {entries.length === 0 ? (
        <div className="empty-state">No data</div>
      ) : (
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
          {entries.map(([label, value], i) => {
            const y = i * (barH + gap);
            const w = (value / max) * (width - 110);
            return (
              <g key={label}>
                <text
                  x={0}
                  y={y + 12}
                  fill="#9bb6bc"
                  fontSize="11"
                  fontFamily="Segoe UI, sans-serif"
                >
                  {label}
                </text>
                <rect x={100} y={y} width={w} height={barH} fill="#2ec4b6" rx={3} />
                <text
                  x={108 + w}
                  y={y + 12}
                  fill="#e6f2f4"
                  fontSize="11"
                  fontFamily="Consolas, monospace"
                >
                  {value}
                </text>
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}

export function SummaryCharts({ summary }: Props) {
  return (
    <div className="chart-grid">
      <BarChart title="By segment" data={summary.by_segment} testId="chart-segment" />
      <BarChart title="By class" data={summary.by_class} testId="chart-class" />
      <BarChart
        title="By confidence band"
        data={summary.by_confidence_band}
        testId="chart-confidence"
      />
      <BarChart
        title="By security state"
        data={summary.by_security_state}
        testId="chart-security"
      />
      <BarChart title="Events by type" data={summary.events_by_type} testId="chart-events" />
    </div>
  );
}

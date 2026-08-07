const ITEMS: { color: string; label: string }[] = [
  { color: '#3d8bfd', label: 'Management' },
  { color: '#2ec4b6', label: 'Infrastructure' },
  { color: '#5dbe8a', label: 'Trusted' },
  { color: '#e6b84d', label: 'IoT' },
  { color: '#9b7bff', label: 'Guest' },
  { color: '#c47a4a', label: 'Quarantine' },
  { color: '#e06c75', label: 'Policy violation' },
  { color: '#9bb6bc', label: 'Offline' },
];

export function Legend() {
  return (
    <div className="panel legend" data-testid="legend" aria-label="Segment legend">
      {ITEMS.map((item) => (
        <span className="legend-item" key={item.label}>
          <span className="swatch" style={{ background: item.color }} aria-hidden="true" />
          {item.label}
        </span>
      ))}
    </div>
  );
}

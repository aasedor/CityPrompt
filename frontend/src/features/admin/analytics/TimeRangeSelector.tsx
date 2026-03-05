const ranges = ['7d', '30d', '90d', '1y'] as const;

const labels: Record<string, string> = {
  '7d': '7 Days',
  '30d': '30 Days',
  '90d': '90 Days',
  '1y': '1 Year',
};

interface Props {
  value: string;
  onChange: (range: string) => void;
}

export function TimeRangeSelector({ value, onChange }: Props) {
  return (
    <div className="inline-flex rounded-lg border border-primary-950/[0.08] bg-white p-1">
      {ranges.map((r) => (
        <button
          key={r}
          onClick={() => onChange(r)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            value === r
              ? 'bg-primary-600 text-white'
              : 'text-primary-950/50 hover:bg-primary-950/[0.04]'
          }`}
        >
          {labels[r]}
        </button>
      ))}
    </div>
  );
}

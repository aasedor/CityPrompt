import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { CreationTrendsResponse } from '@/services/api';

interface Props {
  data: CreationTrendsResponse | null;
}

function formatDate(dateStr: string, granularity: string): string {
  const d = new Date(dateStr);
  if (granularity === 'month') return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  if (granularity === 'week') return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function CreationTrendsChart({ data }: Props) {
  if (!data) return null;

  // Merge projects and buildings into a unified dataset keyed by period
  const periodMap = new Map<string, { period: string; projects: number; buildings: number }>();

  for (const pt of data.projects) {
    const label = formatDate(pt.period, data.granularity);
    const entry = periodMap.get(label) || { period: label, projects: 0, buildings: 0 };
    entry.projects = pt.count;
    periodMap.set(label, entry);
  }

  for (const pt of data.buildings) {
    const label = formatDate(pt.period, data.granularity);
    const entry = periodMap.get(label) || { period: label, projects: 0, buildings: 0 };
    entry.buildings = pt.count;
    periodMap.set(label, entry);
  }

  const chartData = Array.from(periodMap.values());

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-primary-950/60">Creation Trends</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="period" tick={{ fontSize: 12, fill: '#9ca3af' }} stroke="rgba(255,255,255,0.1)" />
            <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#9ca3af' }} stroke="rgba(255,255,255,0.1)" />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', fontSize: '13px', backgroundColor: 'rgba(15,15,30,0.9)', color: '#e5e7eb' }}
            />
            <Legend wrapperStyle={{ fontSize: '13px', color: '#9ca3af' }} />
            <Bar dataKey="projects" name="Projects" fill="#22c55e" radius={[4, 4, 0, 0]} />
            <Bar dataKey="buildings" name="Buildings" fill="#a855f7" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

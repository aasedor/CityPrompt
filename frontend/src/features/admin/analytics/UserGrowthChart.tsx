import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { TimeSeriesResponse } from '@/services/api';

interface Props {
  data: TimeSeriesResponse | null;
}

function formatDate(dateStr: string, granularity: string): string {
  const d = new Date(dateStr);
  if (granularity === 'month') return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  if (granularity === 'week') return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function UserGrowthChart({ data }: Props) {
  if (!data) return null;

  const chartData = data.data.map((pt) => ({
    period: formatDate(pt.period, data.granularity),
    count: pt.count,
  }));

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-primary-950/60 dark:text-white/60">User Growth</h3>
        <span className="text-xs text-primary-950/50 dark:text-white/50">{data.total_in_range} new users</span>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4e539a" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#4e539a" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="period" tick={{ fontSize: 12, fill: '#9ca3af' }} stroke="rgba(255,255,255,0.1)" />
            <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#9ca3af' }} stroke="rgba(255,255,255,0.1)" />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', fontSize: '13px', backgroundColor: 'rgba(15,15,30,0.9)', color: '#e5e7eb' }}
            />
            <Area
              type="monotone"
              dataKey="count"
              name="Signups"
              stroke="#4e539a"
              fill="url(#blueGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

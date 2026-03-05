import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { GenerationStatsResponse } from '@/services/api';

interface Props {
  data: GenerationStatsResponse | null;
}

const STATUS_COLORS: Record<string, string> = {
  completed: '#22c55e',
  failed: '#ef4444',
  generating: '#f59e0b',
  idle: '#a0afc2',
};

export function GenerationStatsWidget({ data }: Props) {
  if (!data) return null;

  // Aggregate all statuses across engines for the pie chart
  const statusTotals: Record<string, number> = {};
  for (const statuses of Object.values(data.by_engine)) {
    for (const [status, count] of Object.entries(statuses)) {
      statusTotals[status] = (statusTotals[status] || 0) + count;
    }
  }

  const pieData = Object.entries(statusTotals).map(([name, value]) => ({ name, value }));

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-primary-950/60 dark:text-white/60">3D Generation Stats</h3>

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Pie chart */}
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={75}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || '#6b7280'} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', fontSize: '13px', backgroundColor: 'rgba(15,15,30,0.9)', color: '#e5e7eb' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Stat cards */}
        <div className="flex flex-col justify-center gap-3">
          <div className="rounded-lg bg-white dark:bg-primary-900 px-4 py-3">
            <p className="text-xs text-primary-950/50 dark:text-white/50">Total Generations</p>
            <p className="text-xl font-bold text-primary-950 dark:text-accent-50">{data.total_generations}</p>
          </div>
          <div className="rounded-lg bg-green-500/15 px-4 py-3">
            <p className="text-xs text-green-400">Success Rate</p>
            <p className="text-xl font-bold text-green-400">{data.success_rate}%</p>
          </div>
          <div className="rounded-lg bg-white dark:bg-primary-900 px-4 py-3">
            <p className="text-xs text-primary-950/50 dark:text-white/50">Engines Active</p>
            <p className="text-xl font-bold text-primary-950 dark:text-accent-50">{Object.keys(data.by_engine).length}</p>
          </div>
        </div>
      </div>

      {/* Per-engine breakdown */}
      {Object.keys(data.by_engine).length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-xs font-medium text-primary-950/50 dark:text-white/50">By Engine</p>
          {Object.entries(data.by_engine).map(([engine, statuses]) => (
            <div key={engine} className="flex items-center justify-between rounded-md bg-white dark:bg-primary-900 px-3 py-2">
              <span className="text-sm font-medium capitalize text-primary-950/60 dark:text-white/60">{engine}</span>
              <div className="flex gap-3">
                {Object.entries(statuses).map(([status, count]) => (
                  <span key={status} className="text-xs text-primary-950/50 dark:text-white/50">
                    <span className="capitalize">{status}</span>: <span className="font-medium text-primary-950/60 dark:text-white/60">{count}</span>
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { GenerationStatsResponse } from '@/services/api';

interface Props {
  data: GenerationStatsResponse | null;
}

const STATUS_COLORS: Record<string, string> = {
  completed: '#22c55e',
  failed: '#ef4444',
  generating: '#f59e0b',
  idle: '#9ca3af',
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
      <h3 className="mb-4 text-sm font-semibold text-gray-700">3D Generation Stats</h3>

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
                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '13px' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Stat cards */}
        <div className="flex flex-col justify-center gap-3">
          <div className="rounded-lg bg-gray-50 px-4 py-3">
            <p className="text-xs text-gray-500">Total Generations</p>
            <p className="text-xl font-bold text-gray-900">{data.total_generations}</p>
          </div>
          <div className="rounded-lg bg-green-50 px-4 py-3">
            <p className="text-xs text-green-600">Success Rate</p>
            <p className="text-xl font-bold text-green-700">{data.success_rate}%</p>
          </div>
          <div className="rounded-lg bg-gray-50 px-4 py-3">
            <p className="text-xs text-gray-500">Engines Active</p>
            <p className="text-xl font-bold text-gray-900">{Object.keys(data.by_engine).length}</p>
          </div>
        </div>
      </div>

      {/* Per-engine breakdown */}
      {Object.keys(data.by_engine).length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-xs font-medium text-gray-500">By Engine</p>
          {Object.entries(data.by_engine).map(([engine, statuses]) => (
            <div key={engine} className="flex items-center justify-between rounded-md bg-gray-50 px-3 py-2">
              <span className="text-sm font-medium capitalize text-gray-700">{engine}</span>
              <div className="flex gap-3">
                {Object.entries(statuses).map(([status, count]) => (
                  <span key={status} className="text-xs text-gray-500">
                    <span className="capitalize">{status}</span>: <span className="font-medium text-gray-700">{count}</span>
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

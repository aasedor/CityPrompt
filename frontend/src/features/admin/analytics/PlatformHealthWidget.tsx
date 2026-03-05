import { Activity, Clock, HardDrive, FileText } from 'lucide-react';
import type { PlatformHealthResponse } from '@/services/api';

interface Props {
  data: PlatformHealthResponse | null;
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
}

export function PlatformHealthWidget({ data }: Props) {
  if (!data) return null;

  const docTotal = Object.values(data.documents).reduce((sum, v) => sum + v, 0);

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-primary-950/60">Platform Health</h3>

      <div className="grid gap-3 sm:grid-cols-2">
        {/* API stats */}
        <div className="rounded-lg border border-primary-950/[0.08] p-3">
          <div className="mb-2 flex items-center gap-2 text-blue-400">
            <Activity size={16} />
            <span className="text-xs font-semibold">API Performance</span>
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between text-sm">
              <span className="text-primary-950/50">Avg Response</span>
              <span className="font-medium text-primary-950">{data.api.avg_response_ms.toFixed(1)} ms</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-primary-950/50">P95 Response</span>
              <span className="font-medium text-primary-950">{data.api.p95_response_ms.toFixed(1)} ms</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-primary-950/50">Total Requests</span>
              <span className="font-medium text-primary-950">{data.api.total_requests.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Uptime */}
        <div className="rounded-lg border border-primary-950/[0.08] p-3">
          <div className="mb-2 flex items-center gap-2 text-green-400">
            <Clock size={16} />
            <span className="text-xs font-semibold">Uptime</span>
          </div>
          <p className="text-2xl font-bold text-primary-950">{formatUptime(data.api.uptime_seconds)}</p>
          <p className="text-xs text-primary-950/50">{data.api.recent_samples} recent samples</p>
        </div>

        {/* Queue */}
        <div className="rounded-lg border border-primary-950/[0.08] p-3">
          <div className="mb-2 flex items-center gap-2 text-purple-400">
            <HardDrive size={16} />
            <span className="text-xs font-semibold">Task Queue</span>
          </div>
          {data.queue.available ? (
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-primary-950/50">Active</span>
                <span className="font-medium text-primary-950">{data.queue.active}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-primary-950/50">Reserved</span>
                <span className="font-medium text-primary-950">{data.queue.reserved}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-primary-950/50">Scheduled</span>
                <span className="font-medium text-primary-950">{data.queue.scheduled}</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-primary-950/50">Queue unavailable</p>
          )}
        </div>

        {/* Documents pipeline */}
        <div className="rounded-lg border border-primary-950/[0.08] p-3">
          <div className="mb-2 flex items-center gap-2 text-orange-400">
            <FileText size={16} />
            <span className="text-xs font-semibold">Doc Pipeline ({docTotal})</span>
          </div>
          <div className="space-y-1.5">
            {Object.entries(data.documents).map(([status, count]) => (
              <div key={status} className="flex justify-between text-sm">
                <span className="capitalize text-primary-950/50">{status}</span>
                <span className="font-medium text-primary-950">{count}</span>
              </div>
            ))}
            {Object.keys(data.documents).length === 0 && (
              <p className="text-sm text-primary-950/50">No documents</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

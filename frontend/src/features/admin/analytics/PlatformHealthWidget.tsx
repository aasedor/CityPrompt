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
      <h3 className="mb-4 text-sm font-semibold text-gray-700">Platform Health</h3>

      <div className="grid gap-3 sm:grid-cols-2">
        {/* API stats */}
        <div className="rounded-lg border border-gray-100 p-3">
          <div className="mb-2 flex items-center gap-2 text-blue-600">
            <Activity size={16} />
            <span className="text-xs font-semibold">API Performance</span>
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Avg Response</span>
              <span className="font-medium text-gray-900">{data.api.avg_response_ms.toFixed(1)} ms</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">P95 Response</span>
              <span className="font-medium text-gray-900">{data.api.p95_response_ms.toFixed(1)} ms</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Total Requests</span>
              <span className="font-medium text-gray-900">{data.api.total_requests.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Uptime */}
        <div className="rounded-lg border border-gray-100 p-3">
          <div className="mb-2 flex items-center gap-2 text-green-600">
            <Clock size={16} />
            <span className="text-xs font-semibold">Uptime</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{formatUptime(data.api.uptime_seconds)}</p>
          <p className="text-xs text-gray-400">{data.api.recent_samples} recent samples</p>
        </div>

        {/* Queue */}
        <div className="rounded-lg border border-gray-100 p-3">
          <div className="mb-2 flex items-center gap-2 text-purple-600">
            <HardDrive size={16} />
            <span className="text-xs font-semibold">Task Queue</span>
          </div>
          {data.queue.available ? (
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Active</span>
                <span className="font-medium text-gray-900">{data.queue.active}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Reserved</span>
                <span className="font-medium text-gray-900">{data.queue.reserved}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Scheduled</span>
                <span className="font-medium text-gray-900">{data.queue.scheduled}</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-400">Queue unavailable</p>
          )}
        </div>

        {/* Documents pipeline */}
        <div className="rounded-lg border border-gray-100 p-3">
          <div className="mb-2 flex items-center gap-2 text-orange-600">
            <FileText size={16} />
            <span className="text-xs font-semibold">Doc Pipeline ({docTotal})</span>
          </div>
          <div className="space-y-1.5">
            {Object.entries(data.documents).map(([status, count]) => (
              <div key={status} className="flex justify-between text-sm">
                <span className="capitalize text-gray-500">{status}</span>
                <span className="font-medium text-gray-900">{count}</span>
              </div>
            ))}
            {Object.keys(data.documents).length === 0 && (
              <p className="text-sm text-gray-400">No documents</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

import { Trophy } from 'lucide-react';
import type { TopUsersResponse } from '@/services/api';

interface Props {
  data: TopUsersResponse | null;
}

const RANK_COLORS = ['text-yellow-500', 'text-neutral-400', 'text-amber-600'];

export function TopUsersTable({ data }: Props) {
  if (!data) return null;

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-neutral-300">Top Users by Activity</h3>

      {data.users.length === 0 ? (
        <p className="py-8 text-center text-sm text-neutral-400">No activity in this period</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.08] text-left text-xs text-neutral-400">
                <th className="pb-2 pr-3">#</th>
                <th className="pb-2 pr-3">User</th>
                <th className="pb-2 pr-3 text-right">Projects</th>
                <th className="pb-2 pr-3 text-right">Buildings</th>
                <th className="pb-2 pr-3 text-right">Documents</th>
                <th className="pb-2 text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {data.users.map((user, i) => (
                <tr key={user.id} className="border-b border-white/[0.06] last:border-0">
                  <td className="py-2.5 pr-3">
                    {i < 3 ? (
                      <Trophy size={16} className={RANK_COLORS[i]} />
                    ) : (
                      <span className="text-neutral-400">{i + 1}</span>
                    )}
                  </td>
                  <td className="py-2.5 pr-3">
                    <p className="font-medium text-white">{user.full_name || user.email}</p>
                    {user.full_name && (
                      <p className="text-xs text-neutral-400">{user.email}</p>
                    )}
                  </td>
                  <td className="py-2.5 pr-3 text-right text-neutral-400">{user.project_count}</td>
                  <td className="py-2.5 pr-3 text-right text-neutral-400">{user.building_count}</td>
                  <td className="py-2.5 pr-3 text-right text-neutral-400">{user.document_count}</td>
                  <td className="py-2.5 text-right font-semibold text-white">{user.total_activity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

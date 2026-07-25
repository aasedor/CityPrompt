import { Trophy } from 'lucide-react';
import type { TopUsersResponse } from '@/services/api';

interface Props {
  data: TopUsersResponse | null;
}

const RANK_COLORS = ['text-yellow-500', 'text-primary-950/50', 'text-amber-600'];

export function TopUsersTable({ data }: Props) {
  if (!data) return null;

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-primary-950/60">Top Users by Activity</h3>

      {data.users.length === 0 ? (
        <p className="py-8 text-center text-sm text-primary-950/50">No activity in this period</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-primary-950/[0.08] text-left text-xs text-primary-950/50">
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
                <tr key={user.id} className="border-b border-primary-950/[0.06] last:border-0">
                  <td className="py-2.5 pr-3">
                    {i < 3 ? (
                      <Trophy size={16} className={RANK_COLORS[i]} />
                    ) : (
                      <span className="text-primary-950/50">{i + 1}</span>
                    )}
                  </td>
                  <td className="py-2.5 pr-3">
                    <p className="font-medium text-primary-950">{user.full_name || user.email}</p>
                    {user.full_name && (
                      <p className="text-xs text-primary-950/50">{user.email}</p>
                    )}
                  </td>
                  <td className="py-2.5 pr-3 text-right text-primary-950/50">{user.project_count}</td>
                  <td className="py-2.5 pr-3 text-right text-primary-950/50">{user.building_count}</td>
                  <td className="py-2.5 pr-3 text-right text-primary-950/50">{user.document_count}</td>
                  <td className="py-2.5 text-right font-semibold text-primary-950">{user.total_activity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { analyticsApi } from '@/services/api';
import type {
  TimeSeriesResponse,
  CreationTrendsResponse,
  GenerationStatsResponse,
  PlatformHealthResponse,
  TopUsersResponse,
} from '@/services/api';
import { TimeRangeSelector } from './analytics/TimeRangeSelector';
import { UserGrowthChart } from './analytics/UserGrowthChart';
import { ActiveUsersChart } from './analytics/ActiveUsersChart';
import { CreationTrendsChart } from './analytics/CreationTrendsChart';
import { GenerationStatsWidget } from './analytics/GenerationStatsWidget';
import { PlatformHealthWidget } from './analytics/PlatformHealthWidget';
import { TopUsersTable } from './analytics/TopUsersTable';

export function CofounderAnalyticsPage() {
  const [range, setRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [userGrowth, setUserGrowth] = useState<TimeSeriesResponse | null>(null);
  const [activeUsers, setActiveUsers] = useState<TimeSeriesResponse | null>(null);
  const [creationTrends, setCreationTrends] = useState<CreationTrendsResponse | null>(null);
  const [generationStats, setGenerationStats] = useState<GenerationStatsResponse | null>(null);
  const [platformHealth, setPlatformHealth] = useState<PlatformHealthResponse | null>(null);
  const [topUsers, setTopUsers] = useState<TopUsersResponse | null>(null);

  const fetchAll = useCallback(async (r: string) => {
    setLoading(true);
    setError('');
    try {
      const [ug, au, ct, gs, ph, tu] = await Promise.all([
        analyticsApi.getUserGrowth(r),
        analyticsApi.getActiveUsers(r),
        analyticsApi.getCreationTrends(r),
        analyticsApi.getGenerationStats(r),
        analyticsApi.getPlatformHealth(),
        analyticsApi.getTopUsers(r),
      ]);
      setUserGrowth(ug);
      setActiveUsers(au);
      setCreationTrends(ct);
      setGenerationStats(gs);
      setPlatformHealth(ph);
      setTopUsers(tu);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll(range);
  }, [range, fetchAll]);

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Link
            to="/admin"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          >
            <ArrowLeft size={18} />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        </div>
        <TimeRangeSelector value={range} onChange={setRange} />
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Row 1: User Growth + Active Users */}
          <div className="grid gap-6 lg:grid-cols-2">
            <UserGrowthChart data={userGrowth} />
            <ActiveUsersChart data={activeUsers} />
          </div>

          {/* Row 2: Creation Trends + Generation Stats */}
          <div className="grid gap-6 lg:grid-cols-2">
            <CreationTrendsChart data={creationTrends} />
            <GenerationStatsWidget data={generationStats} />
          </div>

          {/* Row 3: Platform Health + Top Users */}
          <div className="grid gap-6 lg:grid-cols-2">
            <PlatformHealthWidget data={platformHealth} />
            <TopUsersTable data={topUsers} />
          </div>
        </div>
      )}
    </div>
  );
}

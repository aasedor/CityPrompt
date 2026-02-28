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
  ApiBalanceResponse,
  ApiUsageResponse,
} from '@/services/api';
import { TimeRangeSelector } from './analytics/TimeRangeSelector';
import { UserGrowthChart } from './analytics/UserGrowthChart';
import { ActiveUsersChart } from './analytics/ActiveUsersChart';
import { CreationTrendsChart } from './analytics/CreationTrendsChart';
import { GenerationStatsWidget } from './analytics/GenerationStatsWidget';
import { PlatformHealthWidget } from './analytics/PlatformHealthWidget';
import { TopUsersTable } from './analytics/TopUsersTable';
import { ApiBalancesWidget } from './analytics/ApiBalancesWidget';
import { ApiUsageChart } from './analytics/ApiUsageChart';

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
  const [apiBalances, setApiBalances] = useState<ApiBalanceResponse | null>(null);
  const [apiUsage, setApiUsage] = useState<ApiUsageResponse | null>(null);
  const [apiBalancesLoading, setApiBalancesLoading] = useState(false);
  const [apiUsageLoading, setApiUsageLoading] = useState(false);
  const [apiUsageRange, setApiUsageRange] = useState('30d');

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

  const fetchApiBalances = useCallback(async () => {
    setApiBalancesLoading(true);
    try {
      const balances = await analyticsApi.getApiBalances();
      setApiBalances(balances);
    } catch {
      // silently fail — balances widget handles null
    } finally {
      setApiBalancesLoading(false);
    }
  }, []);

  const fetchApiUsage = useCallback(async (r: string) => {
    setApiUsageLoading(true);
    try {
      const usage = await analyticsApi.getApiUsage(r);
      setApiUsage(usage);
    } catch {
      // silently fail — usage chart handles null
    } finally {
      setApiUsageLoading(false);
    }
  }, []);

  const fetchApiData = useCallback(async () => {
    await Promise.all([fetchApiBalances(), fetchApiUsage(apiUsageRange)]);
  }, [fetchApiBalances, fetchApiUsage, apiUsageRange]);

  useEffect(() => {
    fetchAll(range);
    fetchApiData();
  }, [range, fetchAll, fetchApiData]);

  useEffect(() => {
    fetchApiUsage(apiUsageRange);
  }, [apiUsageRange, fetchApiUsage]);

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

          {/* Row 4: API Usage & Balances */}
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-800">API Usage & Balances</h2>
            <div className="space-y-6">
              <ApiBalancesWidget
                data={apiBalances}
                loading={apiBalancesLoading}
                onRefresh={fetchApiBalances}
              />
              <ApiUsageChart
                data={apiUsage}
                range={apiUsageRange}
                onRangeChange={setApiUsageRange}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

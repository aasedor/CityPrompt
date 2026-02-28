import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { analyticsApi, settingsApi } from '@/services/api';
import type {
  TimeSeriesResponse,
  CreationTrendsResponse,
  GenerationStatsResponse,
  PlatformHealthResponse,
  TopUsersResponse,
  ApiBalanceResponse,
  ApiUsageResponse,
  PlatformSettings,
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

function SectionSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
    </div>
  );
}

export function CofounderAnalyticsPage() {
  const [range, setRange] = useState('30d');

  // Each section has its own data + loading state
  const [userGrowth, setUserGrowth] = useState<TimeSeriesResponse | null>(null);
  const [userGrowthLoading, setUserGrowthLoading] = useState(true);

  const [activeUsers, setActiveUsers] = useState<TimeSeriesResponse | null>(null);
  const [activeUsersLoading, setActiveUsersLoading] = useState(true);

  const [creationTrends, setCreationTrends] = useState<CreationTrendsResponse | null>(null);
  const [creationTrendsLoading, setCreationTrendsLoading] = useState(true);

  const [generationStats, setGenerationStats] = useState<GenerationStatsResponse | null>(null);
  const [generationStatsLoading, setGenerationStatsLoading] = useState(true);

  const [platformHealth, setPlatformHealth] = useState<PlatformHealthResponse | null>(null);
  const [platformHealthLoading, setPlatformHealthLoading] = useState(true);

  const [topUsers, setTopUsers] = useState<TopUsersResponse | null>(null);
  const [topUsersLoading, setTopUsersLoading] = useState(true);

  const [apiBalances, setApiBalances] = useState<ApiBalanceResponse | null>(null);
  const [apiBalancesLoading, setApiBalancesLoading] = useState(true);

  const [apiUsage, setApiUsage] = useState<ApiUsageResponse | null>(null);
  const [apiUsageLoading, setApiUsageLoading] = useState(true);
  const [apiUsageRange, setApiUsageRange] = useState('30d');

  const [platformSettings, setPlatformSettings] = useState<PlatformSettings | null>(null);
  const [settingsLoading, setSettingsLoading] = useState(true);
  const [settingsSaving, setSettingsSaving] = useState(false);

  // Individual fetch functions — each sets its own loading state
  const fetchUserGrowth = useCallback(async (r: string) => {
    setUserGrowthLoading(true);
    try { setUserGrowth(await analyticsApi.getUserGrowth(r)); } catch { /* widget handles null */ }
    finally { setUserGrowthLoading(false); }
  }, []);

  const fetchActiveUsers = useCallback(async (r: string) => {
    setActiveUsersLoading(true);
    try { setActiveUsers(await analyticsApi.getActiveUsers(r)); } catch {}
    finally { setActiveUsersLoading(false); }
  }, []);

  const fetchCreationTrends = useCallback(async (r: string) => {
    setCreationTrendsLoading(true);
    try { setCreationTrends(await analyticsApi.getCreationTrends(r)); } catch {}
    finally { setCreationTrendsLoading(false); }
  }, []);

  const fetchGenerationStats = useCallback(async (r: string) => {
    setGenerationStatsLoading(true);
    try { setGenerationStats(await analyticsApi.getGenerationStats(r)); } catch {}
    finally { setGenerationStatsLoading(false); }
  }, []);

  const fetchPlatformHealth = useCallback(async () => {
    setPlatformHealthLoading(true);
    try { setPlatformHealth(await analyticsApi.getPlatformHealth()); } catch {}
    finally { setPlatformHealthLoading(false); }
  }, []);

  const fetchTopUsers = useCallback(async (r: string) => {
    setTopUsersLoading(true);
    try { setTopUsers(await analyticsApi.getTopUsers(r)); } catch {}
    finally { setTopUsersLoading(false); }
  }, []);

  const fetchApiBalances = useCallback(async () => {
    setApiBalancesLoading(true);
    try { setApiBalances(await analyticsApi.getApiBalances()); } catch {}
    finally { setApiBalancesLoading(false); }
  }, []);

  const fetchApiUsage = useCallback(async (r: string) => {
    setApiUsageLoading(true);
    try { setApiUsage(await analyticsApi.getApiUsage(r)); } catch {}
    finally { setApiUsageLoading(false); }
  }, []);

  const fetchPlatformSettings = useCallback(async () => {
    setSettingsLoading(true);
    try { setPlatformSettings(await settingsApi.getPlatformSettings()); } catch {}
    finally { setSettingsLoading(false); }
  }, []);

  const handleProviderChange = useCallback(async (provider: string) => {
    setSettingsSaving(true);
    try {
      const updated = await settingsApi.updatePlatformSettings({ layout_ai_provider: provider });
      setPlatformSettings(updated);
    } catch {
      // silently fail
    } finally {
      setSettingsSaving(false);
    }
  }, []);

  // On mount & range change: kick off all fetches in parallel
  useEffect(() => {
    fetchUserGrowth(range);
    fetchActiveUsers(range);
    fetchCreationTrends(range);
    fetchGenerationStats(range);
    fetchPlatformHealth();
    fetchTopUsers(range);
    fetchApiBalances();
    fetchApiUsage(apiUsageRange);
    fetchPlatformSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [range]);

  // Separate effect for API usage range changes
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

      <div className="space-y-6">
        {/* Row 1: User Growth + Active Users */}
        <div className="grid gap-6 lg:grid-cols-2">
          {userGrowthLoading && !userGrowth ? <SectionSpinner /> : <UserGrowthChart data={userGrowth} />}
          {activeUsersLoading && !activeUsers ? <SectionSpinner /> : <ActiveUsersChart data={activeUsers} />}
        </div>

        {/* Row 2: Creation Trends + Generation Stats */}
        <div className="grid gap-6 lg:grid-cols-2">
          {creationTrendsLoading && !creationTrends ? <SectionSpinner /> : <CreationTrendsChart data={creationTrends} />}
          {generationStatsLoading && !generationStats ? <SectionSpinner /> : <GenerationStatsWidget data={generationStats} />}
        </div>

        {/* Row 3: Platform Health + Top Users */}
        <div className="grid gap-6 lg:grid-cols-2">
          {platformHealthLoading && !platformHealth ? <SectionSpinner /> : <PlatformHealthWidget data={platformHealth} />}
          {topUsersLoading && !topUsers ? <SectionSpinner /> : <TopUsersTable data={topUsers} />}
        </div>

        {/* Row 4: Platform Settings */}
        {settingsLoading && !platformSettings ? (
          <SectionSpinner />
        ) : platformSettings ? (
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-800">Platform Settings</h2>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
              <div className="flex-1">
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Layout AI Provider
                </label>
                <p className="text-xs text-gray-500">
                  Controls which AI provider generates site layouts for multi-unit zones.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <select
                  value={platformSettings.layout_ai_provider}
                  onChange={(e) => handleProviderChange(e.target.value)}
                  disabled={settingsSaving}
                  className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-50"
                >
                  <option value="claude" disabled={!platformSettings.claude_configured}>
                    Claude {!platformSettings.claude_configured ? '(not configured)' : ''}
                  </option>
                  <option value="gemini" disabled={!platformSettings.gemini_configured}>
                    Gemini {!platformSettings.gemini_configured ? '(not configured)' : ''}
                  </option>
                  <option value="algorithmic">Algorithmic (no AI)</option>
                </select>
                {settingsSaving && <Loader2 className="h-4 w-4 animate-spin text-gray-400" />}
              </div>
            </div>
            <div className="mt-3 flex gap-4 text-xs text-gray-500">
              <span className={platformSettings.claude_configured ? 'text-green-600' : 'text-gray-400'}>
                Claude: {platformSettings.claude_configured ? 'configured' : 'not configured'}
              </span>
              <span className={platformSettings.gemini_configured ? 'text-green-600' : 'text-gray-400'}>
                Gemini: {platformSettings.gemini_configured ? 'configured' : 'not configured'}
              </span>
            </div>
          </div>
        ) : null}

        {/* Row 5: API Usage & Balances */}
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
    </div>
  );
}

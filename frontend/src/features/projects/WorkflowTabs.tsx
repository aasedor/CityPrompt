import { ImageIcon, Map, LayoutGrid, Box } from 'lucide-react';

export type WorkflowTab = 'master-plan' | 'block-editor' | 'master-plan-2d' | '3d-viewer';

interface WorkflowTabsProps {
  activeTab: WorkflowTab;
  onTabChange: (tab: WorkflowTab) => void;
  hasEditableZones: boolean;
  hasSiteGeometry: boolean;
  hasFinalizedLayout: boolean;
  hasMasterPlan3DReady: boolean;
}

export function WorkflowTabs({
  activeTab, onTabChange, hasEditableZones, hasSiteGeometry, hasFinalizedLayout, hasMasterPlan3DReady,
}: WorkflowTabsProps) {
  const tabs: { id: WorkflowTab; label: string; Icon: typeof Map; enabled: boolean; description: string }[] = [
    {
      id: 'master-plan',
      label: 'Master Plan',
      Icon: Map,
      enabled: true,
      description: 'Draw zones and define your site',
    },
    {
      id: 'block-editor',
      label: 'Block Editor',
      Icon: LayoutGrid,
      enabled: hasEditableZones,
      description: hasEditableZones ? 'Edit building layouts' : 'Create zones with descriptions first',
    },
    {
      id: 'master-plan-2d',
      label: '2D Master Plan Generator',
      Icon: ImageIcon,
      enabled: hasSiteGeometry,
      description: hasSiteGeometry ? 'Generate presentation-grade orthographic plan boards' : 'Create site geometry first',
    },
    {
      id: '3d-viewer',
      label: '3D Viewer',
      Icon: Box,
      enabled: hasFinalizedLayout || hasMasterPlan3DReady,
      description: hasMasterPlan3DReady ? 'Review prepared 3D render packages and viewer handoff' : hasFinalizedLayout ? 'View your 3D environment' : 'Finalize layout in Block Editor first',
    },
  ];

  return (
    <div className="flex items-center gap-1 border-t border-primary-950/[0.06] bg-white/95 px-3 py-1.5">
      {tabs.map((tab, idx) => {
        const isActive = activeTab === tab.id;
        const isEnabled = tab.enabled;

        return (
          <div key={tab.id} className="flex items-center">
            {idx > 0 && (
              <div className={`mx-2 h-px w-6 ${idx <= tabs.findIndex(t => t.id === activeTab) ? 'bg-indigo-400' : 'bg-primary-950/10'}`} />
            )}
            <button
              onClick={() => isEnabled && onTabChange(tab.id)}
              disabled={!isEnabled}
              className={`group relative flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-medium transition-all ${
                isActive
                  ? 'bg-indigo-500/10 text-indigo-600 ring-1 ring-indigo-400/30'
                  : isEnabled && tab.id === 'block-editor' && activeTab === 'master-plan'
                    ? 'text-red-600 bg-red-500/10 ring-2 ring-red-500/60 shadow-[0_0_20px_rgba(239,68,68,0.5),0_0_40px_rgba(239,68,68,0.25)] animate-pulse hover:bg-red-500/15'
                  : isEnabled
                    ? 'text-primary-950/80 hover:bg-primary-950/[0.04] hover:text-primary-950'
                    : 'cursor-not-allowed text-primary-950/40'
              }`}
              title={tab.description}
            >
              <span className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold ${
                isActive
                  ? 'bg-indigo-500 text-white'
                  : isEnabled
                    ? 'bg-primary-950/10 text-primary-950/80'
                    : 'bg-primary-950/5 text-primary-950/35'
              }`}>
                {idx + 1}
              </span>
              <tab.Icon size={14} />
              <span>{tab.label}</span>
            </button>
          </div>
        );
      })}
    </div>
  );
}


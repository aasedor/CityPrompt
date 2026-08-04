import { Check } from 'lucide-react';
import type {
  CityPromptWorkflowState,
  CityPromptWorkflowStep,
} from '@/features/workflow/cityPromptWorkflow';

interface WorkflowStepperProps {
  state: CityPromptWorkflowState;
  activeStep?: CityPromptWorkflowStep;
  onStepClick?: (step: CityPromptWorkflowStep) => void;
  compact?: boolean;
}

const STEPS: ReadonlyArray<{
  num: CityPromptWorkflowStep;
  label: string;
  description: string;
}> = [
  { num: 1, label: 'Site', description: 'Draw the active site boundary' },
  { num: 2, label: 'Plan', description: 'Draw a plan or use the Master Planner' },
  { num: 3, label: '3D', description: 'Generate buildings, public realm, and landscaping' },
  { num: 4, label: 'Render', description: 'Create images and video from the compiled scene' },
];

export function WorkflowStepper({
  state,
  activeStep = state.currentStep,
  onStepClick,
  compact = false,
}: WorkflowStepperProps) {
  const completeThrough = state.sceneReady ? 3 : Math.max(0, state.currentStep - 1);

  const canOpen = (step: CityPromptWorkflowStep) => {
    if (step === 1) return true;
    if (step === 2) return state.canPlan;
    if (step === 3) return state.canGenerate3D;
    return state.canRender;
  };

  return (
    <div
      className={compact
        ? 'rounded-lg border-2 border-[#151515] bg-white/95 p-2 shadow-[2px_2px_0_0_#151515]'
        : 'flex items-center gap-1 border-b border-gray-800 bg-gray-900/90 px-4 py-2 backdrop-blur-sm'}
      aria-label="City Prompt workflow"
    >
      <div className={compact ? 'grid grid-cols-4 gap-1' : 'flex items-center gap-1'}>
        {STEPS.map((step, index) => {
          const isActive = step.num === activeStep;
          const isCompleted = step.num <= completeThrough
            || (step.num === 4 && state.hasOutput);
          const isClickable = canOpen(step.num);
          return (
            <div key={step.num} className={compact ? 'min-w-0' : 'flex items-center'}>
              <button
                type="button"
                onClick={() => isClickable && onStepClick?.(step.num)}
                disabled={!isClickable}
                title={step.description}
                aria-current={isActive ? 'step' : undefined}
                className={compact
                  ? `flex w-full min-w-0 flex-col items-center gap-0.5 rounded border px-1 py-1.5 text-[9px] font-black uppercase transition ${
                    isActive
                      ? 'border-[#151515] bg-[#c9ff3d] text-[#151515]'
                      : isCompleted
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-800'
                        : 'border-[#151515]/20 bg-white text-[#151515]/45 disabled:cursor-not-allowed'
                  }`
                  : `flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
                      : isCompleted
                        ? 'cursor-pointer bg-green-600/20 text-green-400 hover:bg-green-600/30'
                        : isClickable
                          ? 'cursor-pointer bg-gray-700 text-gray-300 hover:bg-gray-600'
                          : 'cursor-not-allowed bg-gray-800 text-gray-500'
                  }`}
              >
                <span className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold ${
                  isActive
                    ? compact ? 'bg-[#151515] text-white' : 'bg-white/20 text-white'
                    : isCompleted
                      ? 'bg-green-500/30 text-green-500'
                      : compact ? 'bg-[#151515]/10 text-[#151515]/50' : 'bg-gray-700 text-gray-500'
                }`}>
                  {isCompleted ? <Check size={11} strokeWidth={3} /> : step.num}
                </span>
                <span className="truncate">{step.label}</span>
              </button>

              {!compact && index < STEPS.length - 1 && (
                <div className={`mx-1 h-0.5 w-8 ${isCompleted ? 'bg-green-500/40' : 'bg-gray-700'}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

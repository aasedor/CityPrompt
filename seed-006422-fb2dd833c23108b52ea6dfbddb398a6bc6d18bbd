/**
 * WorkflowStepper.tsx
 *
 * 2-step indicator bar for the site generation workflow:
 *   1. Draw & Style — draw zones, pick development types
 *   2. AI Render — generate photorealistic rendering
 */

interface WorkflowStepperProps {
  currentStep: number; // 1 or 2
  onStepClick: (step: number) => void;
  /** Whether step 2 has been reached */
  hasRender?: boolean;
}

const STEPS = [
  { num: 1, label: 'Draw & Style', description: 'Draw zones and choose development types' },
  { num: 2, label: 'AI Render', description: 'Generate photorealistic rendering' },
];

export function WorkflowStepper({ currentStep, onStepClick, hasRender }: WorkflowStepperProps) {
  return (
    <div className="flex items-center gap-1 px-4 py-2 bg-gray-900/80 backdrop-blur-sm border-b border-gray-800">
      {STEPS.map((step, idx) => {
        const isActive = step.num === currentStep;
        const isCompleted = step.num < currentStep;
        const isClickable =
          step.num <= currentStep ||
          (step.num === 2 && !!hasRender);

        return (
          <div key={step.num} className="flex items-center">
            <button
              onClick={() => isClickable && onStepClick(step.num)}
              disabled={!isClickable}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all
                ${isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
                  : isCompleted
                    ? 'bg-green-600/20 text-green-400 hover:bg-green-600/30 cursor-pointer'
                    : isClickable
                      ? 'bg-gray-700 text-gray-300 hover:bg-gray-600 cursor-pointer'
                      : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                }
              `}
              title={step.description}
            >
              <span className={`
                flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-bold
                ${isActive
                  ? 'bg-white/20 text-white'
                  : isCompleted
                    ? 'bg-green-500/30 text-green-400'
                    : 'bg-gray-700 text-gray-500'
                }
              `}>
                {isCompleted ? '✓' : step.num}
              </span>
              <span>{step.label}</span>
            </button>

            {idx < STEPS.length - 1 && (
              <div className={`
                w-8 h-0.5 mx-1
                ${step.num < currentStep ? 'bg-green-500/40' : 'bg-gray-700'}
              `} />
            )}
          </div>
        );
      })}
    </div>
  );
}

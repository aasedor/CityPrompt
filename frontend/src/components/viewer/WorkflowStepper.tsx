/**
 * WorkflowStepper.tsx
 *
 * 3-step indicator bar for the site generation workflow:
 *   1. Draw & Style
 *   2. Generate Massing
 *   3. AI Render
 */

interface WorkflowStepperProps {
  currentStep: number; // 1, 2, or 3
  onStepClick: (step: number) => void;
}

const STEPS = [
  { num: 1, label: 'Draw & Style' },
  { num: 2, label: 'Generate Massing' },
  { num: 3, label: 'AI Render' },
];

export function WorkflowStepper({ currentStep, onStepClick }: WorkflowStepperProps) {
  return (
    <div className="flex items-center gap-1 px-4 py-2 bg-gray-900/80 backdrop-blur-sm border-b border-gray-800">
      {STEPS.map((step, idx) => {
        const isActive = step.num === currentStep;
        const isCompleted = step.num < currentStep;
        const isClickable = step.num <= currentStep; // can go back, not forward

        return (
          <div key={step.num} className="flex items-center">
            {/* Step pill */}
            <button
              onClick={() => isClickable && onStepClick(step.num)}
              disabled={!isClickable}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all
                ${isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
                  : isCompleted
                    ? 'bg-green-600/20 text-green-400 hover:bg-green-600/30 cursor-pointer'
                    : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {/* Step number / check mark */}
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

            {/* Connector line between steps */}
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

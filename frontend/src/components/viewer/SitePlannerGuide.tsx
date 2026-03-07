import { useState } from 'react';
import { X, MapPin, Layers, Settings, Sparkles, Eye } from 'lucide-react';

const STORAGE_KEY = 'site-planner-guide-dismissed';

const STEPS = [
  {
    Icon: MapPin,
    title: 'Draw a Site Boundary',
    description: 'Select Site Boundary from the main creation tools and draw around your development area.',
  },
  {
    Icon: Layers,
    title: 'Add Zones Inside',
    description: 'Use Buildings, Streets and Paths, and Parks / Plazas to lay out the community inside the boundary.',
  },
  {
    Icon: Settings,
    title: 'Configure Each Zone',
    description: 'Click a zone to edit its properties: height, materials, aesthetic, descriptive text.',
  },
  {
    Icon: Sparkles,
    title: 'Generate Community',
    description: 'Select the Site Boundary and click "Generate Community" to generate the integrated 3D community.',
  },
  {
    Icon: Eye,
    title: 'View & Explore',
    description: 'View in 3D or walk through your neighborhood at street level.',
  },
] as const;

interface SitePlannerGuideProps {
  forceShow?: boolean;
  onDismiss?: () => void;
}

export function SitePlannerGuide({ forceShow, onDismiss }: SitePlannerGuideProps) {
  const [dismissed, setDismissed] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  });

  // Show if: first visit (not dismissed) OR manually triggered via forceShow
  const visible = forceShow || !dismissed;
  if (!visible) return null;

  const handleDismiss = () => {
    setDismissed(true);
    try {
      localStorage.setItem(STORAGE_KEY, 'true');
    } catch {
      // Ignore storage errors
    }
    onDismiss?.();
  };

  return (
    <div className="absolute inset-0 z-40 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="relative mx-4 max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <button
          onClick={handleDismiss}
          className="absolute right-3 top-3 rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
        >
          <X size={16} />
        </button>

        <h2 className="text-lg font-bold text-gray-900 mb-1">
          Site Planner Quick Start
        </h2>
        <p className="text-xs text-gray-500 mb-4">
          Build your neighborhood in 5 steps
        </p>

        <div className="space-y-3">
          {STEPS.map((step, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-purple-100 text-purple-600">
                <step.Icon size={14} />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">
                  <span className="text-purple-600 mr-1">{i + 1}.</span>
                  {step.title}
                </p>
                <p className="text-xs text-gray-500">{step.description}</p>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleDismiss}
          className="mt-5 w-full rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-primary-950 hover:bg-purple-700"
        >
          Got it, let's start!
        </button>
      </div>
    </div>
  );
}


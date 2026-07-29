// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components (Dashboard.jsx)
// Date: 2026-07-29
// ---------------------------------------------------------------------------
import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  Check,
  ClipboardCheck,
  Layers3,
  Route,
  Sparkles,
  Target,
} from 'lucide-react';

const JOURNEY_STEPS = [
  {
    number: '01',
    title: 'Business Validations',
    description:
      'Validate application ownership, business criticality, lifecycle status, and strategic alignment.',
    outcome: 'A trusted business baseline',
    route: '/app-rationalization/technical-assessment/business-validations',
    action: 'Start with validations',
    icon: ClipboardCheck,
    accent: '#0078d4',
    tint: '#eff6fc',
  },
  {
    number: '02',
    title: 'Wave Inputs',
    description:
      'Capture technical complexity, dependencies, risk, effort, and readiness factors used for sequencing.',
    outcome: 'Decision-ready assessment inputs',
    route: '/app-rationalization/technical-assessment/wave-inputs',
    action: 'Prepare wave inputs',
    icon: Layers3,
    accent: '#8764b8',
    tint: '#f5f2fb',
  },
  {
    number: '03',
    title: 'Wave Planning',
    description:
      'Group applications into practical transformation waves and shape an actionable modernization roadmap.',
    outcome: 'A prioritized execution roadmap',
    route: '/app-rationalization/technical-assessment/wave-planning',
    action: 'Build the wave plan',
    icon: Route,
    accent: '#107c10',
    tint: '#f1f8f1',
  },
];

const MODULE_OUTCOMES = [
  'Create a consistent view of the application portfolio',
  'Balance business value, technical health, risk, and effort',
  'Prioritize actions and sequence applications into delivery waves',
];

// Function: Dashboard
const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <main className="min-h-full" style={{ background: 'var(--az-bg)' }}>
      <section
        className="relative overflow-hidden px-8 py-10 lg:px-12 lg:py-12"
        style={{
          background:
            'linear-gradient(118deg, #ffffff 0%, #f7fbff 58%, #edf6fc 100%)',
          borderBottom: '1px solid var(--az-border)',
        }}
      >
        <div
          className="absolute rounded-full"
          aria-hidden="true"
          style={{
            width: 360,
            height: 360,
            right: -130,
            top: -190,
            border: '54px solid rgba(0, 120, 212, 0.05)',
          }}
        />

        <div className="relative max-w-5xl">
          <div
            className="mb-5 inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold"
            style={{
              color: 'var(--az-blue)',
              background: 'var(--az-blue-tint)',
              border: '1px solid var(--az-blue-border)',
            }}
          >
            <Sparkles size={14} />
            Application portfolio transformation
          </div>

          <h1
            className="max-w-3xl text-3xl font-semibold leading-tight lg:text-4xl"
            style={{ color: 'var(--az-text)' }}
          >
            Start your Application Rationalization journey
          </h1>
          <p
            className="mt-4 max-w-3xl text-base leading-7"
            style={{ color: 'var(--az-text-muted)' }}
          >
            Turn portfolio knowledge into a focused modernization roadmap. This
            module helps teams validate business context, assess the inputs that
            drive prioritization, and organize applications into achievable
            transformation waves.
          </p>

          <div className="mt-7 flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="az-btn az-btn-primary"
              onClick={() => navigate(JOURNEY_STEPS[0].route)}
            >
              Start the journey
              <ArrowRight size={15} />
            </button>
            <span
              className="text-xs"
              style={{ color: 'var(--az-text-muted)' }}
            >
              Begin with business validation or choose any stage below.
            </span>
          </div>
        </div>
      </section>

      <div className="px-8 py-8 lg:px-12 lg:py-10">
        <div className="mx-auto max-w-7xl">
          <div className="mb-5 flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
            <div>
              <p className="az-panel-eyebrow">Choose where to begin</p>
              <h2 className="mt-1 text-xl font-semibold" style={{ color: 'var(--az-text)' }}>
                Your rationalization journey
              </h2>
            </div>
            <p className="max-w-md text-sm sm:text-right" style={{ color: 'var(--az-text-muted)' }}>
              Follow the stages in sequence for a new assessment, or open the stage
              that matches your current progress.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
            {JOURNEY_STEPS.map((step, index) => {
              const Icon = step.icon;
              return (
                <article
                  key={step.number}
                  className="group relative flex min-h-[300px] flex-col overflow-hidden bg-white p-6 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                  style={{
                    border: '1px solid var(--az-border)',
                    borderTop: `3px solid ${step.accent}`,
                    borderRadius: 4,
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div
                      className="inline-flex h-11 w-11 items-center justify-center rounded"
                      style={{ color: step.accent, background: step.tint }}
                    >
                      <Icon size={22} />
                    </div>
                    <span
                      className="text-xs font-bold tracking-widest"
                      style={{ color: step.accent }}
                    >
                      STEP {step.number}
                    </span>
                  </div>

                  <h3 className="mt-5 text-lg font-semibold" style={{ color: 'var(--az-text)' }}>
                    {step.title}
                  </h3>
                  <p className="mt-2 text-sm leading-6" style={{ color: 'var(--az-text-muted)' }}>
                    {step.description}
                  </p>

                  <div
                    className="mt-5 flex items-start gap-2 border-t pt-4 text-xs"
                    style={{ borderColor: 'var(--az-border)', color: 'var(--az-text)' }}
                  >
                    <Check size={15} className="mt-0.5 shrink-0" style={{ color: step.accent }} />
                    <span>
                      <strong>Outcome:</strong> {step.outcome}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => navigate(step.route)}
                    className="mt-auto flex items-center justify-between pt-6 text-sm font-semibold"
                    style={{ color: step.accent }}
                    aria-label={`${step.action}: ${step.title}`}
                  >
                    {step.action}
                    <ArrowRight
                      size={16}
                      className="transition-transform duration-200 group-hover:translate-x-1"
                    />
                  </button>

                  {index < JOURNEY_STEPS.length - 1 && (
                    <div
                      className="absolute -right-3 top-1/2 z-10 hidden h-6 w-6 items-center justify-center rounded-full bg-white lg:flex"
                      style={{ border: '1px solid var(--az-border)', color: 'var(--az-text-muted)' }}
                      aria-hidden="true"
                    >
                      <ArrowRight size={12} />
                    </div>
                  )}
                </article>
              );
            })}
          </div>

          <section className="az-panel mt-7">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,0.75fr)_minmax(0,1.25fr)] lg:items-center">
              <div className="flex items-start gap-4">
                <div className="az-panel-icon">
                  <Target size={21} />
                </div>
                <div>
                  <p className="az-panel-eyebrow">What this module delivers</p>
                  <h2 className="az-panel-title mt-1">From portfolio data to decisions</h2>
                  <p className="mt-2 text-sm leading-6" style={{ color: 'var(--az-text-muted)' }}>
                    Bring business and technical perspectives together to make
                    rationalization choices transparent, repeatable, and ready for execution.
                  </p>
                </div>
              </div>

              <ul className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                {MODULE_OUTCOMES.map((outcome) => (
                  <li
                    key={outcome}
                    className="flex items-start gap-2 rounded p-3 text-sm leading-5"
                    style={{
                      color: 'var(--az-text)',
                      background: 'var(--az-bg)',
                      border: '1px solid var(--az-border)',
                    }}
                  >
                    <Check size={15} className="mt-0.5 shrink-0 text-emerald-600" />
                    {outcome}
                  </li>
                ))}
              </ul>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
};

export default Dashboard;

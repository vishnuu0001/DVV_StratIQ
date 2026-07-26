// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/components/ui (SectionHeader.tsx)
// Date: 2026-01-05
// ---------------------------------------------------------------------------
interface SectionHeaderProps {
  eyebrow: string
  title: string
  subtitle?: string
}

// Function: SectionHeader
export default function SectionHeader({ eyebrow, title, subtitle }: SectionHeaderProps) {
  return (
    <div className="mb-6">
      <div className="text-xs font-semibold uppercase tracking-widest text-accent-blue mb-1">
        {eyebrow}
      </div>
      <h2 className="text-2xl font-bold text-slate-100">{title}</h2>
      {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
    </div>
  )
}

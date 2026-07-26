// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (ExportPDFButton.jsx)
// Date: 2026-07-12
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { FileDown, Loader2 } from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'

// Function: formatDateRange
function formatDateRange(dateRange) {
  if (!dateRange?.startDate && !dateRange?.endDate) return 'All Time'
  // Function: fmt
  const fmt = (s) => new Date(s + 'T00:00:00').toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  if (dateRange.startDate && dateRange.endDate) return `${fmt(dateRange.startDate)} to ${fmt(dateRange.endDate)}`
  if (dateRange.startDate) return `From ${fmt(dateRange.startDate)}`
  return `Until ${fmt(dateRange.endDate)}`
}

// Function: ExportPDFButton
export default function ExportPDFButton({ printRef, title = 'Dashboard' }) {
  const [exporting, setExporting] = useState(false)
  const { dateRange } = useDashboard()

  // Function: handleExport
  async function handleExport() {
    if (!printRef?.current || exporting) return
    setExporting(true)
    try {
      const [{ default: jsPDF }, { default: html2canvas }] = await Promise.all([
        import('jspdf'),
        import('html2canvas'),
      ])

      const el = printRef.current
      const canvas = await html2canvas(el, {
        scale: 1.5,
        backgroundColor: '#0f172a',
        useCORS: true,
        allowTaint: true,
        logging: false,
        windowWidth: el.scrollWidth,
        windowHeight: el.scrollHeight,
      })

      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
      const pageW = pdf.internal.pageSize.getWidth()
      const pageH = pdf.internal.pageSize.getHeight()

      // Header bar
      pdf.setFillColor(15, 23, 42)
      pdf.rect(0, 0, pageW, pageH, 'F')

      pdf.setFont('helvetica', 'bold')
      pdf.setFontSize(13)
      pdf.setTextColor(224, 242, 254)
      pdf.text(title, 10, 10)

      pdf.setFont('helvetica', 'normal')
      pdf.setFontSize(8)
      pdf.setTextColor(148, 163, 184)
      const rangeLabel = formatDateRange(dateRange)
      pdf.text(`Period: ${rangeLabel}`, 10, 16)
      pdf.text(`Generated: ${new Date().toLocaleString()}`, pageW - 10, 16, { align: 'right' })

      // Content image
      const contentTop = 20
      const contentH = pageH - contentTop - 5
      const imgAspect = canvas.width / canvas.height
      const fitW = Math.min(pageW - 10, contentH * imgAspect)
      const fitH = fitW / imgAspect
      const imgX = (pageW - fitW) / 2
      const imgY = contentTop

      if (fitH <= contentH) {
        pdf.addImage(imgData, 'PNG', imgX, imgY, fitW, fitH)
      } else {
        // multi-page: slice canvas into page-height chunks
        const sliceH = Math.floor(canvas.height * (contentH / fitH))
        let offsetY = 0
        let page = 0
        while (offsetY < canvas.height) {
          if (page > 0) {
            pdf.addPage()
            pdf.setFillColor(15, 23, 42)
            pdf.rect(0, 0, pageW, pageH, 'F')
          }
          const remaining = canvas.height - offsetY
          const thisSlice = Math.min(sliceH, remaining)
          const sliceCanvas = document.createElement('canvas')
          sliceCanvas.width = canvas.width
          sliceCanvas.height = thisSlice
          const ctx = sliceCanvas.getContext('2d')
          ctx.drawImage(canvas, 0, offsetY, canvas.width, thisSlice, 0, 0, canvas.width, thisSlice)
          const sliceData = sliceCanvas.toDataURL('image/png')
          const sliceFitH = (thisSlice / canvas.height) * fitH
          pdf.addImage(sliceData, 'PNG', imgX, contentTop, fitW, sliceFitH)
          offsetY += sliceH
          page++
        }
      }

      const safeTitle = title.replace(/[^a-z0-9]/gi, '-').toLowerCase()
      pdf.save(`${safeTitle}.pdf`)
    } catch (err) {
      console.error('PDF export failed:', err)
    } finally {
      setExporting(false)
    }
  }

  return (
    <button
      onClick={handleExport}
      disabled={exporting}
      title={`Export ${title} as PDF`}
      className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium border border-slate-600/40 bg-slate-700/30 text-slate-300 hover:bg-slate-700/60 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all"
    >
      {exporting
        ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
        : <FileDown className="w-3.5 h-3.5" />}
      <span>{exporting ? 'Exporting…' : 'Export PDF'}</span>
    </button>
  )
}

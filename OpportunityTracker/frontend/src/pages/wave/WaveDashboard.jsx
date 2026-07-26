// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages/wave (WaveDashboard.jsx)
// Date: 2026-07-04
// ---------------------------------------------------------------------------
import React, { useCallback, useState } from 'react';
import toast from 'react-hot-toast';
import { pollWaveJob, listWaveCategories } from '../../services/api';
import WaveUploadPanel from './WaveUploadPanel';
import WaveJobStatus from './WaveJobStatus';
import WaveCategoryPicker from './WaveCategoryPicker';
import WaveCategoryDetail from './WaveCategoryDetail';

// Function: WaveDashboard
export default function WaveDashboard() {
  const [job, setJob] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [categories, setCategories] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);

  const loadCategories = useCallback(async (id) => {
    const { data } = await listWaveCategories(id);
    setCategories(data);
  }, []);

  const handleJobStarted = useCallback((id) => {
    setJobId(id);
    setJob(null);
    setCategories(null);
    setSelectedCategory(null);

    pollWaveJob(id, (progress) => setJob(progress))
      .then(async (finalStatus) => {
        setJob(finalStatus);
        await loadCategories(id);
        if (finalStatus.status === 'done') {
          toast.success('Wave planning analysis complete.');
        } else {
          toast.error('Analysis finished with errors — check per-category status.');
        }
      })
      .catch((err) => {
        toast.error(err.message || 'Analysis job failed.');
      });
  }, [loadCategories]);

  if (selectedCategory) {
    return (
      <WaveCategoryDetail
        jobId={jobId}
        category={selectedCategory}
        onBack={() => setSelectedCategory(null)}
      />
    );
  }

  if (categories) {
    return (
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-lg font-bold text-white">Wave Planning</p>
            <p className="text-sm text-slate-400">{categories.length} Solution Approach categories analyzed</p>
          </div>
          <button
            type="button"
            className="ot-btn-secondary text-xs px-3 py-1.5"
            onClick={() => { setJob(null); setJobId(null); setCategories(null); }}
          >
            Upload new data
          </button>
        </div>
        <WaveCategoryPicker categories={categories} onSelect={setSelectedCategory} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-lg font-bold text-white">Wave Planning</p>
        <p className="text-sm text-slate-400 mt-1">
          Upload the Application Scope and Business Categorization spreadsheets to generate an
          LLM-assisted migration wave plan, drillable down to individual applications.
        </p>
      </div>
      {job ? <WaveJobStatus job={job} /> : <WaveUploadPanel onJobStarted={handleJobStarted} />}
    </div>
  );
}

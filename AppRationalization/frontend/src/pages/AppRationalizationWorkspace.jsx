// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/pages (AppRationalizationWorkspace.jsx)
// Date: 2025-09-24
// ---------------------------------------------------------------------------
import React, { useEffect } from 'react';
import { Route, Routes } from 'react-router-dom';
import axios from 'axios';
import { getAuthToken } from '../services/authSession';
import { API_BASE } from '../services/api';

import Analysis from '../components/Analysis';
import BusinessCapabilityMapping from '../components/business-capability/BusinessCapabilityMapping';
import StandardizationERP from '../components/business-capability/StandardizationERP';
import FinalTraceabilityMatrix from '../components/business-capability/FinalTraceabilityMatrix';
import CASTAnalysis from '../components/CASTAnalysis';
import CorrelationDashboard from '../components/CorrelationDashboard';
import Dashboard from '../components/Dashboard';
import FileUpload from '../components/FileUpload';
import GoldenData from '../components/GoldenData';
import IndustryTemplates from '../components/IndustryTemplates';
import Layout from '../components/Layout';
import TechnicalAssessmentData from '../components/TechnicalAssessmentData';
import TechnicalEvaluationCategorize from '../components/TechnicalEvaluationCategorize';
import WavePlanning from '../components/WavePlanning';

// Function: AppRationalizationWorkspace
const AppRationalizationWorkspace = () => {
  useEffect(() => {
    const SESSION_KEY = 'app_reset_done';
    if (!sessionStorage.getItem(SESSION_KEY)) {
      ['cache_standardization', 'cache_capability_mapping', 'cache_capability_analysis', 'cache_traceability'].forEach(
        (key) => localStorage.removeItem(key)
      );

      axios
        .post(
          `${API_BASE}/reset`,
          {},
          {
            headers: {
              Authorization: `Bearer ${getAuthToken()}`,
            },
          }
        )
        .then(() => {
          sessionStorage.setItem(SESSION_KEY, '1');
        })
        .catch(() => {
          // Non-blocking reset path.
        });
    }
  }, []);

  return (
    <Layout>
      <Routes>
        <Route index element={<Dashboard />} />
        <Route path="upload" element={<FileUpload />} />
        <Route path="industry-templates" element={<IndustryTemplates />} />
        <Route path="cast-analysis" element={<CASTAnalysis />} />
        <Route path="analysis" element={<Analysis />} />
        <Route path="golden-data" element={<GoldenData />} />
        <Route path="correlation" element={<CorrelationDashboard />} />
        <Route path="capability/inventory" element={<BusinessCapabilityMapping />} />
        <Route path="capability/standardization" element={<StandardizationERP />} />
        <Route path="capability/traceability" element={<FinalTraceabilityMatrix />} />
        <Route path="technical-assessment/business-validations" element={<TechnicalAssessmentData key="business-validations" dataset="business-validations" />} />
        <Route path="technical-assessment/wave-inputs" element={<TechnicalAssessmentData key="wave-inputs" dataset="wave-inputs" />} />
        <Route path="technical-evaluation/categorize" element={<TechnicalEvaluationCategorize />} />
        <Route path="technical-evaluation/validate" element={<TechnicalEvaluationCategorize mode="validate" />} />
        <Route path="technical-assessment/wave-planning" element={<WavePlanning />} />
      </Routes>
    </Layout>
  );
};

export default AppRationalizationWorkspace;

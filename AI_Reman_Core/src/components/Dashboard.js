// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Reman_Core — src/components (Dashboard.js)
// Date: 2026-02-04
// ---------------------------------------------------------------------------
import React, { useState } from 'react';
import { Upload, Activity, ScanLine, Terminal, Home } from 'lucide-react';
import { motion } from 'framer-motion';
import { analyzeCore, generateAnalysisSteps } from '../services/AISimulationService';

import CameraFeed from './CameraFeed';
import ImageSelector from './ImageSelector';
import ResultCard from './ResultCard';

// Function: Dashboard
const Dashboard = () => {
    const [mode, setMode] = useState('upload');
    const [image, setImage] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const [coreType, setCoreType] = useState("Turbocharger");

    const [scanLog, setScanLog] = useState("");
    const [progress, setProgress] = useState(0);

    // Function: handleCapture
    const handleCapture = (imageSrc) => {
        setImage(imageSrc);
        setResult(null);
        setMode('preview');
        // Trigger automatic real-time analysis
        setTimeout(() => triggerRealTimeAnalysis(imageSrc), 300);
    };

    // Function: handleImageSelect
    const handleImageSelect = (imageSrc, type) => {
        setImage(imageSrc);
        setCoreType(type);
        setResult(null);
        setMode('preview');
        // Trigger automatic real-time analysis
        setTimeout(() => triggerRealTimeAnalysis(imageSrc), 300);
    };

    // Function: handleFileUpload
    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImage(reader.result);
                setMode('preview');
                setResult(null);
                // Trigger automatic real-time analysis
                setTimeout(() => triggerRealTimeAnalysis(reader.result), 300);
            };
            reader.readAsDataURL(file);
        }
    };

    // Function: triggerRealTimeAnalysis
    const triggerRealTimeAnalysis = async (imageSrc) => {
        setAnalyzing(true);
        setResult(null);
        setScanLog("Initializing Real-Time Assessment...");
        setProgress(0);

        const steps = generateAnalysisSteps();
        const stepDuration = 600;

        for (let i = 0; i < steps.length; i++) {
            await new Promise(r => setTimeout(r, stepDuration));
            setScanLog(steps[i]);
            setProgress(((i + 1) / steps.length) * 100);
        }

        const data = await analyzeCore(imageSrc, coreType);
        setResult(data);
        setAnalyzing(false);
    };

    // Function: runSimulation
    const runSimulation = async () => {
        if (!image) return;
        await triggerRealTimeAnalysis(image);
    };

    // Function: reset
    const reset = () => {
        setImage(null);
        setResult(null);
        setMode('upload');
        setScanLog("");
        setProgress(0);
    };

    return (
        <div className="dashboard-container">
            <header className="app-header" style={{position: 'relative'}}>
                <h1><Activity className="icon" /> RemanCore AI Predictor</h1>
                <p style={{margin: '8px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem'}}>Real-Time Automated Assessment System</p>

                {/* HOME BUTTON */}
                <button
                    onClick={reset}
                    style={{
                        position: 'absolute', right: 0, top: '50%', transform: 'translateY(-50%)',
                        background: 'rgba(26, 31, 58, 0.8)', border: '1px solid rgba(100, 150, 255, 0.2)', 
                        color: 'var(--text-muted)', padding: '10px 18px', borderRadius: '8px', 
                        cursor: 'pointer', display: 'flex', gap: '8px', fontWeight: '600',
                        transition: 'var(--transition)'
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.borderColor = 'rgba(100, 150, 255, 0.4)';
                        e.target.style.background = 'rgba(26, 31, 58, 0.95)';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.borderColor = 'rgba(100, 150, 255, 0.2)';
                        e.target.style.background = 'rgba(26, 31, 58, 0.8)';
                    }}
                >
                    <Home size={16} /> <span className="mobile-hide">Reset</span>
                </button>
            </header>

            <div className="main-grid">
                {/* --- LEFT COLUMN --- */}
                <div className="card input-section">
                    <div className="card-header">
                        <h2>Inspection Station</h2>
                        <div className="btn-group">
                            <button
                                onClick={() => { setMode('camera'); setImage(null); setResult(null); }}
                                className={mode === 'camera' ? 'active' : ''}
                            >
                                Camera
                            </button>
                            <button
                                onClick={() => { setMode('upload'); setImage(null); setResult(null); }}
                                className={mode === 'upload' ? 'active' : ''}
                            >
                                Upload / Gallery
                            </button>
                        </div>
                    </div>

                    <div className="controls">
                        <select value={coreType} onChange={(e) => setCoreType(e.target.value)}>
                            <option value="Turbocharger">Turbocharger</option>
                            <option value="Alternator">Alternator</option>
                            <option value="ECU Module">ECU Module</option>
                            <option value="Starter Motor">Starter Motor</option>
                            <option value="Transmission">Transmission</option>
                        </select>
                    </div>

                    <div className="viewport">
                        {mode === 'camera' && !image && (
                            <CameraFeed onCapture={handleCapture} />
                        )}

                        {mode === 'upload' && !image && (
                            <div className="upload-container-wrapper" style={{width: '100%', padding: '20px'}}>
                                <div className="upload-dropzone" style={{border: '2px dashed #334155', borderRadius: '12px', padding: '40px', textAlign: 'center', marginBottom: '20px', cursor: 'pointer', position: 'relative'}}>
                                    <Upload size={32} style={{marginBottom: '10px', color: '#64748b'}} />
                                    <p style={{margin: 0, color: '#94a3b8'}}>Tap to Upload File</p>
                                    <input type="file" onChange={handleFileUpload} accept="image/*" style={{opacity: 0, position: 'absolute', top:0, left:0, width:'100%', height:'100%'}} />
                                </div>
                                <ImageSelector onSelect={handleImageSelect} selectedImage={image} />
                            </div>
                        )}

                        {image && (
                            <>
                                <img src={image} alt="Core Inspection" />
                                {analyzing && (
                                    <>
                                        <motion.div
                                            className="scan-line"
                                            animate={{ top: ['0%', '100%', '0%'] }}
                                            transition={{ repeat: Infinity, duration: 2.5, ease: "linear" }}
                                        />
                                        <div className="simulation-log-overlay">
                                            <div style={{display:'flex', alignItems:'center', gap:'8px', marginBottom:'8px'}}>
                                                <Terminal size={14} color="#00ff9d"/>
                                                <span style={{color:'#64748b', fontSize:'0.75rem'}}>AI_PROCESS_V1.2</span>
                                            </div>
                                            <p className="log-text">> {scanLog}</p>
                                            <div className="progress-bar">
                                                <div className="fill" style={{width: `${progress}%`}}></div>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </>
                        )}
                    </div>

                    {/* Primary Action: Run Simulation */}
                    {image && !analyzing && !result && (
                        <motion.button 
                            className="analyze-btn" 
                            onClick={runSimulation}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <ScanLine size={20} /> Analyze Core
                        </motion.button>
                    )}
                </div>

                {/* --- RIGHT COLUMN --- */}
                {/* We pass the reset function here so the button inside ResultCard works */}
                <ResultCard result={result} loading={analyzing} onReset={reset} />
            </div>
        </div>
    );
};

export default Dashboard;
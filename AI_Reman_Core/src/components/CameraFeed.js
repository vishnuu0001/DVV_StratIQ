// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Reman_Core — src/components (CameraFeed.js)
// Date: 2026-02-08
// ---------------------------------------------------------------------------
import React, { useRef, useCallback, useState } from 'react';
import Webcam from 'react-webcam';
import { Camera } from 'lucide-react';

// Function: CameraFeed
const CameraFeed = ({ onCapture }) => {
    const webcamRef = useRef(null);
    const [isRecording, setIsRecording] = useState(false);

    const videoConstraints = {
        width: 1280,
        height: 720,
        facingMode: "environment" // Uses rear camera on phones
    };

    const capture = useCallback(() => {
        if (webcamRef.current) {
            const imageSrc = webcamRef.current.getScreenshot();
            setIsRecording(true);
            setTimeout(() => setIsRecording(false), 400);
            onCapture(imageSrc);
        }
    }, [webcamRef, onCapture]);

    return (
        <div className="webcam-wrapper" style={{position: 'relative', height: '100%', background: '#000'}}>
            <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={videoConstraints}
                className="webcam-feed"
                style={{width: '100%', height: '100%', objectFit: 'cover'}}
            />

            {/* Live Indicator Badge */}
            <div style={{
                position: 'absolute', top: '16px', left: '16px', 
                background: 'rgba(26, 31, 58, 0.7)', backdropFilter: 'blur(8px)',
                border: '1px solid rgba(100, 150, 255, 0.3)', color: 'white',
                padding: '8px 14px', borderRadius: '20px', display: 'flex', 
                alignItems: 'center', gap: '8px', fontSize: '0.8rem', fontWeight: '600',
                zIndex: 998
            }}>
                <span style={{
                    width: '8px', height: '8px', borderRadius: '50%', 
                    background: '#ef4444', animation: 'pulse 2s infinite'
                }}></span>
                LIVE
            </div>

            {/* OVERLAY UI - Forced Z-Index to ensure visibility */}
            <div className="camera-overlay" style={{
                position: 'absolute', bottom: '20px', left: 0, width: '100%',
                display: 'flex', justifyContent: 'center', alignItems: 'flex-end', 
                zIndex: 999, padding: '0 20px'
            }}>
                <button
                    className="capture-btn"
                    onClick={capture}
                    style={{
                        background: isRecording ? 'rgba(239, 68, 68, 0.9)' : 'linear-gradient(135deg, #ef4444, #dc2626)',
                        color: 'white', padding: '16px 32px',
                        borderRadius: '50px', border: '3px solid white', fontSize: '1.2rem',
                        fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px',
                        cursor: 'pointer', boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                        transition: 'all 0.3s ease', transform: isRecording ? 'scale(0.95)' : 'scale(1)'
                    }}
                    onMouseEnter={(e) => !isRecording && (e.target.style.transform = 'scale(1.05)')}
                    onMouseLeave={(e) => !isRecording && (e.target.style.transform = 'scale(1)')}
                >
                    <Camera size={24} /> {isRecording ? 'CAPTURED' : 'CAPTURE'}
                </button>
            </div>

            {/* Corner Grid Indicators */}
            <div style={{
                position: 'absolute', top: '0', left: '0', width: '100%', height: '100%',
                pointerEvents: 'none', zIndex: 1,
                background: `
                    linear-gradient(90deg, 
                        rgba(100, 150, 255, 0.1) 1px, transparent 1px,
                        transparent calc(33.33% - 1px), rgba(100, 150, 255, 0.1) calc(33.33% - 1px),
                        rgba(100, 150, 255, 0.1) calc(33.33% + 1px), transparent calc(33.33% + 1px),
                        transparent calc(66.66% - 1px), rgba(100, 150, 255, 0.1) calc(66.66% - 1px),
                        rgba(100, 150, 255, 0.1) calc(66.66% + 1px), transparent calc(66.66% + 1px)
                    ),
                    linear-gradient(0deg,
                        rgba(100, 150, 255, 0.1) 1px, transparent 1px,
                        transparent calc(33.33% - 1px), rgba(100, 150, 255, 0.1) calc(33.33% - 1px),
                        rgba(100, 150, 255, 0.1) calc(33.33% + 1px), transparent calc(33.33% + 1px),
                        transparent calc(66.66% - 1px), rgba(100, 150, 255, 0.1) calc(66.66% - 1px),
                        rgba(100, 150, 255, 0.1) calc(66.66% + 1px), transparent calc(66.66% + 1px)
                    )`
            }} />

            <style>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `}</style>
        </div>
    );
};

export default CameraFeed;
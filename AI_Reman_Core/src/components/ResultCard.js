// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Reman_Core — src/components (ResultCard.js)
// Date: 2026-03-27
// ---------------------------------------------------------------------------
import React from 'react';
import { CheckCircle, XCircle, Shield, Clock, BarChart2, RefreshCw, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

// Function: ResultCard
const ResultCard = ({ result, loading, onReset }) => {
    const containerVariants = {
        hidden: { opacity: 0 },
        show: { opacity: 1, transition: { staggerChildren: 0.1 } }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 10 },
        show: { opacity: 1, y: 0, transition: { duration: 0.3 } }
    };
    return (
        <div className="card results-section" style={{minHeight: '400px', display:'flex', flexDirection:'column', height: '100%'}}>
            <div className="card-header">
                <h2>2. AI Diagnostic Report</h2>
            </div>

            {/* State 1: Idle */}
            {!result && !loading && (
                <div style={{
                    flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    border: '2px dashed rgba(100, 150, 255, 0.2)', borderRadius: '12px', 
                    color: '#64748b', flexDirection: 'column', gap: '12px'
                }}>
                    <Zap size={32} style={{ opacity: 0.4 }} />
                    <p>Awaiting Real-Time Assessment...</p>
                    <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>Upload or capture an image to begin</p>
                </div>
            )}

            {/* State 2: Loading */}
            {loading && (
                <motion.div 
                    className="loading-state" 
                    style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}
                    animate={{ opacity: [0.6, 1, 0.6] }}
                    transition={{ duration: 2, repeat: Infinity }}
                >
                    <div className="spinner" style={{
                        width: '60px', height: '60px', border: '4px solid rgba(100, 150, 255, 0.1)',
                        borderTop: '4px solid var(--accent)', borderRadius: '50%', animation: 'spin 1.5s linear infinite'
                    }}></div>
                    <p style={{marginTop: '24px', color: 'var(--text-muted)', fontSize: '1rem', fontWeight: '500'}}>Processing Visual Data...</p>
                    <p style={{marginTop: '8px', color: 'var(--text-muted)', fontSize: '0.85rem'}}>Analyzing surface, texture, and anomalies</p>
                </motion.div>
            )}

            {/* State 3: Final Result */}
            {result && !loading && (
                <motion.div 
                    className="results-content fade-in" 
                    style={{display: 'flex', flexDirection: 'column', height: '100%'}}
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                >

                    <motion.div 
                        className={`status-badge ${result.status.toLowerCase()}`} 
                        style={{
                            padding: '28px', borderRadius: '14px', textAlign: 'center', marginBottom: '24px',
                            background: result.status === 'Pass' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                            border: result.status === 'Pass' ? '2px solid rgba(16, 185, 129, 0.4)' : '2px solid rgba(239, 68, 68, 0.4)',
                            color: result.status === 'Pass' ? '#10b981' : '#ef4444',
                            boxShadow: result.status === 'Pass' ? '0 0 20px rgba(16, 185, 129, 0.15)' : '0 0 20px rgba(239, 68, 68, 0.15)'
                        }}
                        variants={itemVariants}
                    >
                        <motion.div
                            animate={{ scale: [1, 1.1, 1] }}
                            transition={{ duration: 0.5 }}
                        >
                            {result.status === 'Pass' ? <CheckCircle size={56} /> : <XCircle size={56} />}
                        </motion.div>
                        <h1 style={{margin: '12px 0 6px 0', fontSize: '2.8rem', textTransform: 'uppercase', letterSpacing:'2px', fontWeight: '800'}}>
                            {result.status === 'Salvage' ? 'REJECTED' : 'ACCEPTED'}
                        </h1>
                        <p style={{margin: 0, opacity: 0.85, fontSize: '0.95rem'}}>{result.status === 'Pass' ? '✓ Condition Meets Reman Standards' : '✗ Critical Defects Detected - Recycle'}</p>
                    </motion.div>

                    <motion.div 
                        className="metric-grid"
                        variants={itemVariants}
                    >
                        <div className="metric-box">
                            <label><Clock size={14}/> EST. NEW LIFE</label>
                            <span className="value" style={{color: result.predictedLifeYears < 3 ? '#ef4444' : 'var(--success)'}}>
                                {result.predictedLifeYears} <small>Yrs</small>
                            </span>
                        </div>
                        <div className="metric-box">
                            <label><Shield size={14}/> WARRANTY</label>
                            <span className="value">
                                {result.warrantyMonths} <small>Mo</small>
                            </span>
                        </div>
                        <div className="metric-box">
                            <label><BarChart2 size={14}/> CONFIDENCE</label>
                            <span className="value">{result.confidence}</span>
                        </div>
                    </motion.div>

                    <motion.div 
                        className="defects-list" 
                        style={{flex: 1}}
                        variants={itemVariants}
                    >
                        <h3 style={{fontSize: '0.9rem', color: 'var(--text-muted)', borderBottom: '1px solid rgba(100, 150, 255, 0.15)', paddingBottom: '10px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                            IDENTIFIED ANOMALIES
                        </h3>
                        <ul style={{listStyle: 'none', padding: 0, margin: '12px 0 0 0'}}>
                            {result.defects.map((d, i) => (
                                <motion.li 
                                    key={i} 
                                    style={{
                                        display: 'flex', justifyContent: 'space-between', padding: '14px',
                                        marginBottom: '8px', background: 'rgba(100, 150, 255, 0.05)', borderRadius: '8px',
                                        borderLeft: d.severity === 'High' ? '4px solid #ef4444' : d.severity === 'Medium' ? '4px solid #f59e0b' : '4px solid #10b981',
                                        transition: 'var(--transition)'
                                    }}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    whileHover={{ backgroundColor: 'rgba(100, 150, 255, 0.1)' }}
                                >
                                    <span style={{fontWeight: '500'}}>{d.name}</span>
                                    <span className="severity-tag" style={{
                                        fontSize: '0.7rem', padding: '4px 10px', borderRadius: '12px',
                                        background: d.severity === 'High' ? 'rgba(239, 68, 68, 0.2)' : d.severity === 'Medium' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                                        color: d.severity === 'High' ? '#ef4444' : d.severity === 'Medium' ? '#f59e0b' : '#10b981',
                                        fontWeight: '600'
                                    }}>{d.severity}</span>
                                </motion.li>
                            ))}
                        </ul>
                    </motion.div>

                    {/* NEW RESET BUTTON INSIDE RESULT CARD */}
                    <motion.button
                        onClick={onReset}
                        style={{
                            marginTop: '20px', width: '100%', padding: '16px', 
                            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(59, 130, 246, 0.1))',
                            color: 'white', border: '1px solid rgba(100, 150, 255, 0.3)',
                            borderRadius: '10px', fontWeight: '700', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                            transition: 'var(--transition)', textTransform: 'uppercase', fontSize: '0.9rem', letterSpacing: '0.5px'
                        }}
                        variants={itemVariants}
                        whileHover={{ backgroundColor: 'rgba(59, 130, 246, 0.2)' }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <RefreshCw size={18}/> NEW INSPECTION
                    </motion.button>

                </motion.div>
            )}
        </div>
    );
};

export default ResultCard;
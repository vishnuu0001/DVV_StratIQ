// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Reman_Core — src/components (ImageSelector.js)
// Date: 2026-03-15
// ---------------------------------------------------------------------------
import React from 'react';

// References images located in public/asset/ based on your screenshot
const SAMPLE_CORES = [
    {
        id: 'turbo',
        name: 'Turbocharger',
        type: 'Turbocharger',
        src: '/asset/turbocharger.jpg'
    },
    {
        id: 'alt',
        name: 'Alternator',
        type: 'Alternator',
        src: '/asset/heavyduty.jpg' // Using your heavy duty image for alternator demo
    },
    {
        id: 'ecu',
        name: 'ECU Module',
        type: 'ECU Module',
        src: '/asset/ecu_mod.jpg'
    },
    {
        id: 'starter',
        name: 'Starter Motor',
        type: 'Starter Motor',
        src: '/asset/StarterMotor.jpg'
    },
    {
        id: 'trans',
        name: 'Transmission',
        type: 'Transmission',
        src: '/asset/transmission.jpg'
    },
];

// Function: ImageSelector
const ImageSelector = ({ onSelect, selectedImage }) => {
    return (
        <div className="image-selector-container">
            <div className="divider">
                <span>SELECT CORE FOR INSPECTION</span>
            </div>

            <div className="thumbnail-grid">
                {SAMPLE_CORES.map((core) => (
                    <button
                        key={core.id}
                        className={`thumbnail-card ${selectedImage === core.src ? 'active' : ''}`}
                        onClick={() => onSelect(core.src, core.type)}
                    >
                        <div className="thumb-img-wrapper">
                            <img src={core.src} alt={core.name} onError={(e) => {e.target.src = 'https://placehold.co/100?text=Missing'}} />
                        </div>
                        <span className="thumb-label">{core.name}</span>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default ImageSelector;
// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Reman_Core — src (index.js)
// Date: 2025-08-20
// ---------------------------------------------------------------------------
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Create the root element
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the App component wrapped in StrictMode for additional checks during development
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
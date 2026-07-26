// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components (PageHeader.jsx)
// Date: 2025-11-10
// ---------------------------------------------------------------------------
import React from 'react';

// Function: PageHeader
const PageHeader = ({ title, subtitle, children }) => {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-8 px-8 rounded-lg mb-8">
      <h1 className="text-4xl font-bold mb-2">{title}</h1>
      <p className="text-blue-100 mb-4">{subtitle}</p>
      {children}
    </div>
  );
};

export default PageHeader;

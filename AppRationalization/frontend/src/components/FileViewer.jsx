// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components (FileViewer.jsx)
// Date: 2026-04-27
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react';
import { Download, ChevronLeft, ChevronRight } from 'lucide-react';
import apiClient, { API_BASE } from '../services/api';

// Function: getFileType
const getFileType = (name) => {
  const ext = name.split('.').pop().toLowerCase();
  if (['xls', 'xlsx', 'xlsm'].includes(ext)) return 'excel';
  if (['pdf'].includes(ext)) return 'pdf';
  return 'unknown';
};

// Function: filterExcelRows
const filterExcelRows = (rows, searchTerm) => {
  if (!searchTerm.trim()) return rows;
  return rows.filter((row) =>
    Object.values(row).some((cell) => String(cell).toLowerCase().includes(searchTerm.toLowerCase()))
  );
};

// Function: loadExcelPreview
const loadExcelPreview = (fileId, { setIsLoadingExcel, setError, setSheetNames, setExcelData, setCurrentSheet }) => {
  setIsLoadingExcel(true);
  setError(null);
  apiClient.get(`/upload/preview/${fileId}`, {
    params: { max_rows: 500 }
  })
    .then(response => {
      if (!response || typeof response.data !== 'object' || response.data === null) {
        throw new Error('Invalid preview response from server');
      }

      const sheetNameList = response.data?.sheet_names || [];
      const previewSheets = response.data?.sheets || {};

      if (!Array.isArray(sheetNameList) || sheetNameList.length === 0) {
        throw new Error('No sheet metadata found in preview response');
      }

      const sheetsByIndex = {};
      sheetNameList.forEach((name, idx) => {
        sheetsByIndex[idx] = previewSheets[name] || [];
      });

      setSheetNames(sheetNameList);
      setExcelData(sheetsByIndex);
      setCurrentSheet(0);
      setIsLoadingExcel(false);
    })
    .catch(err => {
      setIsLoadingExcel(false);
      setError('Failed to load Excel file: ' + (err?.response?.data?.error || err.message));
    });
};

// Function: SheetTabs
const SheetTabs = ({ sheetNames, currentSheet, onSelect }) => {
  if (sheetNames.length <= 1) return null;
  return (
    <div className="flex items-center gap-2 p-4 border-b border-gray-200 bg-gray-50 overflow-x-auto">
      {currentSheet > 0 && (
        <button
          onClick={() => onSelect(currentSheet - 1)}
          className="p-1 hover:bg-gray-200 rounded transition"
          title="Previous sheet"
        >
          <ChevronLeft size={18} />
        </button>
      )}
      {sheetNames.map((name, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(idx)}
          className={`px-3 py-1 rounded text-sm font-medium whitespace-nowrap transition ${
            currentSheet === idx
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
          }`}
        >
          {name}
        </button>
      ))}
      {currentSheet < sheetNames.length - 1 && (
        <button
          onClick={() => onSelect(currentSheet + 1)}
          className="p-1 hover:bg-gray-200 rounded transition ml-auto"
          title="Next sheet"
        >
          <ChevronRight size={18} />
        </button>
      )}
    </div>
  );
};

// Function: ExcelSearchBar
const ExcelSearchBar = ({ searchTerm, onSearchChange, filteredCount, totalCount }) => (
  <div className="p-4 border-b border-gray-200 bg-gray-50">
    <input
      type="text"
      placeholder="Search records..."
      value={searchTerm}
      onChange={onSearchChange}
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
    />
    <p className="text-xs text-gray-600 mt-2">
      Showing {filteredCount} of {totalCount} records
    </p>
  </div>
);

// Function: ExcelDataTable
const ExcelDataTable = ({ sheetRows, filteredRows, searchTerm }) => (
  <div className="overflow-x-auto max-h-96">
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="bg-gray-100 border-b border-gray-300">
          {sheetRows.length > 0
            ? Object.keys(sheetRows[0]).map((key) => (
                <th
                  key={key}
                  className="px-4 py-2 text-left font-semibold text-gray-700 border-r border-gray-300 whitespace-nowrap"
                >
                  {key}
                </th>
              ))
            : null}
        </tr>
      </thead>
      <tbody>
        {filteredRows.length > 0 ? (
          filteredRows.map((row, rowIdx) => (
            <tr key={rowIdx} className="border-b border-gray-200 hover:bg-blue-50">
              {Object.values(row).map((cell, cellIdx) => (
                <td
                  key={cellIdx}
                  className="px-4 py-2 text-gray-600 border-r border-gray-200 whitespace-nowrap overflow-hidden text-ellipsis max-w-xs"
                  title={String(cell)}
                >
                  {cell !== null && cell !== undefined ? String(cell) : '-'}
                </td>
              ))}
            </tr>
          ))
        ) : (
          <tr>
            <td colSpan="100" className="px-4 py-4 text-center text-gray-500 text-sm">
              No records found matching "{searchTerm}"
            </td>
          </tr>
        )}
      </tbody>
    </table>
  </div>
);

// Function: ExcelPreview
const ExcelPreview = ({
  error, excelData, isLoadingExcel, sheetNames, currentSheet, setCurrentSheet,
  searchTerm, setSearchTerm, filteredExcelData,
}) => {
  if (error) {
    return (
      <div className="p-8 bg-red-50">
        <p className="text-red-700 text-sm font-medium mb-2">⚠️ Preview Error</p>
        <p className="text-red-600 text-xs">{error}</p>
        <p className="text-red-600 text-xs mt-2">Click Download to open in Excel.</p>
      </div>
    );
  }

  if (excelData && Object.keys(excelData).length > 0) {
    const sheetRows = excelData[currentSheet] || [];
    return (
      <div>
        <SheetTabs sheetNames={sheetNames} currentSheet={currentSheet} onSelect={setCurrentSheet} />
        <ExcelSearchBar
          searchTerm={searchTerm}
          onSearchChange={(e) => setSearchTerm(e.target.value)}
          filteredCount={filteredExcelData.length}
          totalCount={sheetRows.length}
        />
        <ExcelDataTable sheetRows={sheetRows} filteredRows={filteredExcelData} searchTerm={searchTerm} />
      </div>
    );
  }

  if (isLoadingExcel) {
    return (
      <div className="p-8 bg-gray-50 text-center">
        <p className="text-gray-500 text-sm">Loading Excel file...</p>
      </div>
    );
  }

  return (
    <div className="p-8 bg-yellow-50 text-center">
      <p className="text-yellow-700 text-sm">No Excel data available for preview.</p>
    </div>
  );
};

// Function: PdfPreview
const PdfPreview = ({ fileId, fileUrl, filename, fileType, onError }) => (
  <div className="w-full">
    <iframe
      key={fileId}
      src={fileUrl}
      className="w-full border-0"
      style={{
        minHeight: '700px',
        height: '700px'
      }}
      title={filename}
      onError={() => onError(`Failed to load ${fileType}`)}
    />
  </div>
);

// Function: FileViewer
const FileViewer = ({ fileId, filename, onClose, isInline = true }) => {
  const [error, setError] = useState(null);
  const [excelData, setExcelData] = useState(null);
  const [isLoadingExcel, setIsLoadingExcel] = useState(false);
  const [currentSheet, setCurrentSheet] = useState(0);
  const [sheetNames, setSheetNames] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const fileUrl = `${API_BASE}/upload/pdf/${fileId}`;

  const fileType = getFileType(filename);

  // Load and parse Excel file
  useEffect(() => {
    if (fileType === 'excel') {
      loadExcelPreview(fileId, { setIsLoadingExcel, setError, setSheetNames, setExcelData, setCurrentSheet });
    }
  }, [fileId, filename, fileType, fileUrl]);

  // Function: handleDownload
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Filter Excel data based on search term
  const filteredExcelData = excelData && excelData[currentSheet]
    ? filterExcelRows(excelData[currentSheet], searchTerm)
    : [];

  // Only inline mode (in expandable frame) is rendered
  if (!isInline) return null;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div className="flex-1" />
        <button
          onClick={handleDownload}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
          title={`Download ${fileType}`}
        >
          <Download size={18} />
          Download
        </button>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {fileType === 'excel' ? (
          <div className="w-full">
            <ExcelPreview
              error={error}
              excelData={excelData}
              isLoadingExcel={isLoadingExcel}
              sheetNames={sheetNames}
              currentSheet={currentSheet}
              setCurrentSheet={setCurrentSheet}
              searchTerm={searchTerm}
              setSearchTerm={setSearchTerm}
              filteredExcelData={filteredExcelData}
            />
          </div>
        ) : (
          <PdfPreview fileId={fileId} fileUrl={fileUrl} filename={filename} fileType={fileType} onError={setError} />
        )}
      </div>
    </div>
  );
};

export default FileViewer;

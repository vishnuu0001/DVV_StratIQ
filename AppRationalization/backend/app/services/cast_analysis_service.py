# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: CAST Analysis PDF Extraction Service
# Date: 2026-07-06
# ---------------------------------------------------------------------------
"""CAST Analysis PDF Extraction Service"""

import logging
import re
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

logger = logging.getLogger(__name__)

# ===== PERFORMANCE OPTIMIZATIONS =====
# Pre-compiled regex patterns
WHITESPACE_PATTERN = re.compile(r'\s+')
HEADER_KEYWORDS = {'app id', 'application', 'metric', 'total', 'report', 'page', 'value'}

# Function: _normalize_whitespace
def _normalize_whitespace(text):
    """Optimize whitespace normalization"""
    if not text:
        return ""
    return WHITESPACE_PATTERN.sub(' ', text)

# Function: _cell
def _cell(row_data, idx):
    """Stripped string value of a table cell, or "" if empty/falsy."""
    return str(row_data[idx]).strip() if row_data[idx] else ""

# Function: _is_header_row
def _is_header_row(first_cell_str, second_cell_str=None):
    """
    Fast header detection - checks both first and second cell
    For 13-column tables with empty first column, check second cell instead
    """
    # If first cell is empty, check second cell
    if not first_cell_str or str(first_cell_str).strip() == "":
        if second_cell_str:
            first_cell_str = second_cell_str
        else:
            return True
    
    first_cell_lower = str(first_cell_str).lower().strip()
    
    # Empty cell or starts with # = header
    if first_cell_lower == '' or first_cell_lower.startswith('#'):
        return True
    
    # Check for common header keywords
    if any(kw in first_cell_lower for kw in HEADER_KEYWORDS):
        return True
    
    # "Rank", "Risk", numeric IDs = not header
    if first_cell_lower in ['rank', 'risk', 'total', 'page']:
        return False
    
    return False


# Function: _dispatch_cast_table_by_shape
def _dispatch_cast_table_by_shape(table_data, num_cols, first_cell, buckets):
    """Route one extracted table to the correct CAST bucket based on column count/shape."""
    # Inventory: 12 or 13 columns
    if num_cols in (12, 13):
        _extract_app_inventory(table_data, buckets['app_inventory'])
    # Classification: 6 or 7 columns
    elif num_cols in (6, 7):
        _extract_app_classification(table_data, buckets['app_classification'])
    # Architecture: 10 columns
    elif num_cols == 10:
        # Check if it's high-risk (Rank-based) or regular architecture
        if first_cell.lower() == "rank":
            _extract_high_risk_applications(table_data, buckets['high_risk_applications'])
        else:
            _extract_internal_architecture(table_data, buckets['internal_architecture'])
    # Architecture: 9, 11, or other columns
    elif num_cols in (9, 11):
        _extract_internal_architecture(table_data, buckets['internal_architecture'])


# Function: _process_cast_page_tables
def _process_cast_page_tables(page, buckets):
    """Find and dispatch all tables on one page; returns the number of tables found."""
    tabs = page.find_tables()

    table_count = 0
    for table in tabs:
        table_count += 1
        table_data = table.extract()

        if len(table_data) <= 1:
            continue

        # Determine which table type by column count and structure
        num_cols = len(table_data[0])
        first_cell = str(table_data[0][0]).strip() if table_data[0][0] else ""

        _dispatch_cast_table_by_shape(table_data, num_cols, first_cell, buckets)

    return table_count


class CASTAnalysisService:
    """Service for extracting CAST Analysis data from PDF"""

    # Function: extract_pdf_tables
    @staticmethod
    def extract_pdf_tables(file_path):
        """
        Extract CAST Analysis tables from PDF
        Expected tables:
        1. Application Inventory (12 or 13 columns)
        2. Application Classification (6 or 7 columns)
        3. Internal Architecture (9 or 10 columns with empty first or varied format)
        4. High-Risk Applications (10 columns with Rank first)
        """
        if not fitz:
            raise ImportError("PyMuPDF (fitz) is required for PDF extraction. Install: pip install PyMuPDF")
        
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            logger.info(f"[CAST Extraction] Starting: {total_pages} pages")
            
            app_inventory_rows = []
            app_classification_rows = []
            internal_architecture_rows = []
            high_risk_applications_rows = []
            
            pages_processed = 0
            tables_found = 0

            buckets = {
                'app_inventory': app_inventory_rows,
                'app_classification': app_classification_rows,
                'internal_architecture': internal_architecture_rows,
                'high_risk_applications': high_risk_applications_rows,
            }

            for page_num in range(total_pages):
                page = doc[page_num]

                try:
                    table_count = _process_cast_page_tables(page, buckets)
                except Exception:
                    continue

                if table_count > 0:
                    pages_processed += 1
                    tables_found += table_count
            
            doc.close()
            
            logger.info(f"[CAST Extraction] Complete: App Inventory={len(app_inventory_rows)}, Classification={len(app_classification_rows)}, Architecture={len(internal_architecture_rows)}, High-Risk={len(high_risk_applications_rows)}")
            
            return {
                'app_inventory': app_inventory_rows,
                'app_classification': app_classification_rows,
                'internal_architecture': internal_architecture_rows,
                'high_risk_applications': high_risk_applications_rows,
                'pages_processed': pages_processed,
                'tables_found': tables_found,
            }
            
        except Exception as e:
            logger.error(f"[CAST Extraction] Error: {str(e)}", exc_info=True)
            raise


# Function: _extract_app_inventory
def _parse_app_inventory_row(row_data, start_col):
    """Parse and validate one Application Inventory row; returns dict or None."""
    if not row_data or len(row_data) < (12 + start_col):
        return None

    # Check for header row - use second cell if first is empty
    first_cell = str(row_data[start_col]).strip() if row_data[start_col] else ""
    if _is_header_row(first_cell, str(row_data[start_col] if start_col > 0 else None)):
        return None

    try:
        app_id = _cell(row_data, start_col + 0)
        application = _cell(row_data, start_col + 1)

        # Fast validation
        if not app_id or not application:
            return None

        if app_id.upper() == 'APP ID' or application.upper() == 'APPLICATION':
            return None

        row_dict = {
            'app_id': app_id,
            'application': application,
            'repo': _cell(row_data, start_col + 2),
            'primary_language': _cell(row_data, start_col + 3),
            'framework': _cell(row_data, start_col + 4),
            'loc_k': _to_float(row_data[start_col + 5]),
            'modules': _to_int(row_data[start_col + 6]),
            'db_name': _cell(row_data, start_col + 7),
            'ext_int': _cell(row_data, start_col + 8),
            'quality': _cell(row_data, start_col + 9),
            'security': _cell(row_data, start_col + 10),
            'cloud_ready': _cell(row_data, start_col + 11),
        }

        # Normalize whitespace
        for key in row_dict:
            if isinstance(row_dict[key], str):
                row_dict[key] = _normalize_whitespace(row_dict[key])

        return row_dict

    except Exception:
        return None


# Function: _extract_app_inventory
def _extract_app_inventory(table_data, rows):
    """Extract Application Inventory table (12 or 13 columns)"""
    num_cols = len(table_data[0]) if table_data else 0

    # Determine if we have 13-col (with empty first col) or 12-col format
    has_empty_first_col = (num_cols == 13)
    start_col = 1 if has_empty_first_col else 0

    for row_data in table_data:
        row_dict = _parse_app_inventory_row(row_data, start_col)
        if row_dict is None:
            continue

        rows.append(row_dict)

        if len(rows) % 100 == 0:
            logger.info(f"[CAST] App Inventory: {len(rows)} rows extracted")


# Function: _extract_app_classification
def _parse_app_classification_row(row_data, start_col):
    """Parse and validate one Application Classification row; returns dict or None."""
    if not row_data or len(row_data) < (6 + start_col):
        return None

    # Check for header row
    first_cell = str(row_data[start_col]).strip() if row_data[start_col] else ""
    if _is_header_row(first_cell, str(row_data[start_col] if start_col > 0 else None)):
        return None

    try:
        app_id = _cell(row_data, start_col + 0)
        application = _cell(row_data, start_col + 1)

        # Fast validation
        if not app_id or not application:
            return None

        if app_id.upper() == 'APP ID' or application.upper() == 'APPLICATION':
            return None

        row_dict = {
            'app_id': app_id,
            'application': application,
            'business_owner': _cell(row_data, start_col + 2),
            'application_type': _cell(row_data, start_col + 3),
            'install_type': _cell(row_data, start_col + 4),
            'capabilities': _cell(row_data, start_col + 5),
        }

        # Normalize whitespace
        for key in row_dict:
            if isinstance(row_dict[key], str):
                row_dict[key] = _normalize_whitespace(row_dict[key])

        return row_dict

    except Exception:
        return None


# Function: _extract_app_classification
def _extract_app_classification(table_data, rows):
    """Extract Application Classification table (6 or 7 columns)"""
    num_cols = len(table_data[0]) if table_data else 0

    # Determine if we have 7-col (with empty first col) or 6-col format
    has_empty_first_col = (num_cols == 7)
    start_col = 1 if has_empty_first_col else 0

    for row_data in table_data:
        row_dict = _parse_app_classification_row(row_data, start_col)
        if row_dict is None:
            continue

        rows.append(row_dict)

        if len(rows) % 100 == 0:
            logger.info(f"[CAST] App Classification: {len(rows)} rows extracted")


# Function: _build_internal_architecture_row_10col
def _build_internal_architecture_row_10col(row_data, start_col, app_id, application):
    # 10-col format from PDF: cols are Risk, Quality, Security, Cloud, App Type, Install Type, Capabilities
    return {
        'app_id': app_id,
        'application': application,
        'module': _cell(row_data, start_col + 2),  # Risk
        'layer': _cell(row_data, start_col + 3),   # Quality
        'language': _cell(row_data, start_col + 4),  # Security
        'db_calls': _to_int(row_data[start_col + 5]),  # Cloud rating
        'external_calls': _to_int(0),  # Not available in 10-col format
        'app_type': _cell(row_data, start_col + 6),
        'install_type': _cell(row_data, start_col + 7),
    }


# Function: _build_internal_architecture_row_9col
def _build_internal_architecture_row_9col(row_data, start_col, app_id, application):
    return {
        'app_id': app_id,
        'application': application,
        'module': _cell(row_data, start_col + 2),
        'layer': _cell(row_data, start_col + 3),
        'language': _cell(row_data, start_col + 4),
        'db_calls': _to_int(row_data[start_col + 5]),
        'external_calls': _to_int(row_data[start_col + 6]),
        'app_type': _cell(row_data, start_col + 7),
        'install_type': _cell(row_data, start_col + 8),
    }


# Function: _parse_internal_architecture_row
def _parse_internal_architecture_row(row_data, start_col, has_rank_col):
    """Parse and validate one Internal Architecture row; returns dict or None."""
    if not row_data or len(row_data) < (9 + (1 if has_rank_col else 0)):
        return None

    # Check for header row (check both first and second cell for 10-col tables)
    check_cell = _cell(row_data, start_col)
    if _is_header_row(check_cell, str(row_data[start_col] if start_col > 0 else None)):
        return None

    try:
        # For 10-col tables: skip rank, extract from App ID onwards
        # For 9-col tables: extract from col 0 onwards
        app_id = _cell(row_data, start_col + 0)
        application = _cell(row_data, start_col + 1)

        # Fast validation
        if not app_id or not application:
            return None

        if app_id.upper() == 'APP ID' or application.upper() == 'APPLICATION':
            return None

        if has_rank_col:
            row_dict = _build_internal_architecture_row_10col(row_data, start_col, app_id, application)
        else:
            row_dict = _build_internal_architecture_row_9col(row_data, start_col, app_id, application)

        # Normalize whitespace
        for key in row_dict:
            if isinstance(row_dict[key], str):
                row_dict[key] = _normalize_whitespace(row_dict[key])

        return row_dict

    except Exception:
        return None


# Function: _extract_internal_architecture
def _extract_internal_architecture(table_data, rows):
    """Extract Internal Architecture table (9 or 10 columns)"""
    num_cols = len(table_data[0]) if table_data else 0

    # Determine if we have 10-col (with rank first col) or 9-col format
    # 10-col format: Rank, APP ID, Application, Risk, Quality, Security, Cloud, App Type, Install Type, Capabilities
    # 9-col format: APP ID, Application, Module, Layer, Language, DB Calls, External Calls, App Type, Install Type
    has_rank_col = (num_cols == 10)
    start_col = 1 if has_rank_col else 0

    for row_data in table_data:
        row_dict = _parse_internal_architecture_row(row_data, start_col, has_rank_col)
        if row_dict is None:
            continue

        rows.append(row_dict)

        if len(rows) % 100 == 0:
            logger.info(f"[CAST] Internal Architecture: {len(rows)} rows extracted")


# Function: _to_int
def _to_int(value):
    """Convert value to integer safely"""
    if not value:
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError, AttributeError):
        return None


# Function: _parse_high_risk_application_row
def _parse_high_risk_application_row(row_data):
    """Parse and validate one High-Risk Applications row; returns dict or None."""
    if not row_data or len(row_data) < 10:
        return None

    # Check for header row
    first_cell = _cell(row_data, 0)
    if first_cell.lower() == "rank" or _is_header_row(first_cell):
        return None

    try:
        rank = _to_int(row_data[0])
        app_id = _cell(row_data, 1)
        application = _cell(row_data, 2)

        # Fast validation
        if not app_id or not application:
            return None

        if app_id.upper() == 'APP ID' or application.upper() == 'APPLICATION':
            return None

        row_dict = {
            'rank': rank,
            'app_id': app_id,
            'application': application,
            'risk': _cell(row_data, 3),
            'quality': _cell(row_data, 4),
            'security': _cell(row_data, 5),
            'cloud': _cell(row_data, 6),
            'app_type': _cell(row_data, 7),
            'install_type': _cell(row_data, 8),
            'capabilities': _cell(row_data, 9),
        }

        # Normalize whitespace
        for key in row_dict:
            if isinstance(row_dict[key], str):
                row_dict[key] = _normalize_whitespace(row_dict[key])

        return row_dict

    except Exception:
        return None


# Function: _extract_high_risk_applications
def _extract_high_risk_applications(table_data, rows):
    """Extract High-Risk Applications table (10 columns with Rank first)"""
    # Format: Rank, APP ID, Application, Risk, Quality, Security, Cloud, App Type, Install Type, Capabilities

    for row_data in table_data:
        row_dict = _parse_high_risk_application_row(row_data)
        if row_dict is None:
            continue

        rows.append(row_dict)

        if len(rows) % 100 == 0:
            logger.info(f"[CAST] High-Risk Applications: {len(rows)} rows extracted")


# Function: _to_float
def _to_float(value):
    """Convert value to float safely"""
    if not value:
        return None
    try:
        return float(str(value).strip())
    except (ValueError, TypeError, AttributeError):
        return None

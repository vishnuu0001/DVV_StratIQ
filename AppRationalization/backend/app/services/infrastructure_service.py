# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AppRationalization — backend/app/services (infrastructure_service.py)
# Date: 2026-05-04
# ---------------------------------------------------------------------------
import json
import uuid
import re
import logging
from pypdf import PdfReader
from app.models.infrastructure import Infrastructure, Server, Container, NetworkLink, InfrastructureDiscovery
from app import db

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

logger = logging.getLogger(__name__)

# ===== PERFORMANCE OPTIMIZATIONS =====
# Compile regex patterns once at module level (avoid recompilation in loops)
WHITESPACE_PATTERN = re.compile(r'\s+')
HEADER_KEYWORDS = {'app id', 'metric', 'total', 'corent report', 'discovery', 'page', 'value'}

# Function: _normalize_whitespace
def _normalize_whitespace(text):
    """Optimize whitespace normalization - use pre-compiled regex"""
    if not text:
        return ""
    return WHITESPACE_PATTERN.sub(' ', text)

# Function: _is_header_row
def _is_header_row(first_cell_str):
    """Fast header detection using set lookup"""
    if not first_cell_str:
        return True
    
    first_cell_lower = first_cell_str.lower()
    
    # Check simple patterns first (fastest)
    if first_cell_lower == '' or first_cell_lower.startswith('#'):
        return True
    
    # Check if any keyword matches (set lookup is O(1))
    if any(kw in first_cell_lower for kw in HEADER_KEYWORDS):
        return True
    
    return False


# Function: _safe_cell
def _safe_cell(row_data, idx):
    return str(row_data[idx]).strip() if row_data[idx] else ""


# Function: _is_valid_corent_row
def _is_valid_corent_row(app_id, app_name):
    if not app_id or not app_name:
        return False
    if app_id.upper() == 'APP ID' or app_id == 'TECHM':
        return False
    if not app_id.startswith('TECHM') or len(app_id) <= 2:
        return False
    app_name_lower = app_name.lower()
    if (app_name_lower == 'installed app / name'
            or app_name_lower.startswith('page')
            or app_name_lower.startswith('metric')):
        return False
    return True


# Function: _parse_corent_table_row
def _parse_corent_table_row(row_data, col_offset):
    """Extract and validate a single CORENT discovery row; returns dict or None."""
    app_id = _safe_cell(row_data, col_offset)
    app_name = _safe_cell(row_data, col_offset + 1)
    if not _is_valid_corent_row(app_id, app_name):
        return None
    try:
        row_dict = {
            'app_id': app_id,
            'name': app_name,
            'business_owner': _safe_cell(row_data, col_offset + 2),
            'architecture_type': _safe_cell(row_data, col_offset + 3),
            'platform_host': _safe_cell(row_data, col_offset + 4),
            'application_type': _safe_cell(row_data, col_offset + 5),
            'install_type': _safe_cell(row_data, col_offset + 6),
            'capabilities': _safe_cell(row_data, col_offset + 7),
        }
        for key in row_dict:
            if row_dict[key]:
                row_dict[key] = _normalize_whitespace(row_dict[key])
        return row_dict
    except (IndexError, ValueError, AttributeError):
        return None


class InfrastructureService:
    """Service for extracting infrastructure data from Corent outputs"""
    
    Y_TOLERANCE = 1.5
    BOTTOM_MARGIN = 40
    
    # Function: extract_from_pdf
    @staticmethod
    def extract_from_pdf(file_path, file_name):
        """Extract infrastructure data from PDF file"""
        try:
            logger.info(f"[InfrastructureService] Starting PDF extraction from {file_path}")
            pdf_reader = PdfReader(file_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            logger.info(f"[InfrastructureService] Total text extracted: {len(text)} characters")
            return InfrastructureService.parse_infrastructure_data(text, file_name, file_path)
        except Exception as e:
            logger.error(f"[InfrastructureService] Error reading PDF: {str(e)}", exc_info=True)
            raise Exception(f"Error reading PDF: {str(e)}")
    
    # Function: parse_infrastructure_data
    @staticmethod
    def parse_infrastructure_data(text, file_name, file_path=None):
        """Parse extracted text to create infrastructure entities"""
        file_id = str(uuid.uuid4())
        
        # Create Infrastructure record
        infra = Infrastructure(
            file_id=file_id,
            filename=file_name,
            file_path=file_path,
            total_vms=0,
            total_k8s_clusters=0,
            orphan_systems=0
        )
        
        db.session.add(infra)
        db.session.commit()
        
        logger.info(f"[InfrastructureService] Infrastructure record created for {file_name}")
        return file_id, infra
    
    # Function: _classify_corent_row
    @staticmethod
    def _classify_corent_row(row_data, col_offset):
        """Classify a single table row. Returns ('skip', None), ('header', None), or ('data', row_dict)."""
        # Fast validation: must have enough columns
        if not row_data or len(row_data) < (col_offset + 8):
            return "skip", None

        # Fast header detection on first column
        first_cell_val = row_data[col_offset]
        if not first_cell_val:
            return "skip", None

        if _is_header_row(str(first_cell_val).strip()):
            return "header", None

        row_dict = _parse_corent_table_row(row_data, col_offset)
        if row_dict is None:
            return "skip", None

        return "data", row_dict

    # Function: _process_table_rows
    @staticmethod
    def _process_table_rows(table_data, col_offset, rows, header_counter):
        """Classify and append rows from one extracted table.

        Mutates `rows` (list) and `header_counter` (dict with key 'n') in place
        so partial progress survives a mid-page exception, matching the
        original single inline loop.
        """
        for row_data in table_data:
            kind, row_dict = InfrastructureService._classify_corent_row(row_data, col_offset)
            if kind == "header":
                header_counter['n'] += 1
                continue
            if kind != "data":
                continue

            rows.append(row_dict)
            if len(rows) % 500 == 0:
                logger.info(f"[PDF Extraction] Progress: {len(rows)} rows extracted")

    # Function: _process_page_tables
    @staticmethod
    def _process_page_tables(page, rows, header_counter):
        """Find and process all tables on one page; returns the number of tables found."""
        # Find tables on this page (TableFinder is iterable)
        tabs = page.find_tables()

        table_count = 0
        for table in tabs:
            table_count += 1
            table_data = table.extract()

            # Skip if this looks like only a header row
            if len(table_data) <= 1:
                continue

            # Determine column offset based on number of columns (cache it)
            num_cols = len(table_data[0])
            col_offset = 1 if num_cols == 10 else 0

            InfrastructureService._process_table_rows(table_data, col_offset, rows, header_counter)

        return table_count

    # Function: extract_pdf_table
    @staticmethod
    def extract_pdf_table(file_path):
        """Extract Infrastructure & Network Discovery table from PDF using PyMuPDF table detection

        OPTIMIZATIONS:
        - Skip first page (known to be metrics/headers)
        - Use pre-compiled regex patterns
        - Cache string operations
        - Reduce logging frequency
        - Fast-fail validation checks

        Handles CORENT_Report.pdf structure (188 pages, ~3,785 records)
        """
        if not fitz:
            raise ImportError("PyMuPDF (fitz) is required for PDF extraction. Install: pip install PyMuPDF")

        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            logger.info(f"[PDF Extraction] Starting: {total_pages} pages")

            rows = []
            header_counter = {'n': 0}
            pages_processed = 0
            tables_found = 0

            # Process all pages (data tables start from page 1)
            for page_num in range(total_pages):
                page = doc[page_num]

                try:
                    table_count = InfrastructureService._process_page_tables(page, rows, header_counter)
                except Exception:
                    # Skip pages with table detection errors
                    continue

                # Only count pages that had processed tables
                if table_count > 0:
                    pages_processed += 1
                    tables_found += table_count

            doc.close()

            elapsed_pages = pages_processed
            skipped_headers = header_counter['n']
            logger.info(f"[PDF Extraction] Complete: {len(rows)} rows | {elapsed_pages} pages processed | {tables_found} tables found | {skipped_headers} headers skipped")

            if not rows:
                raise ValueError("No table data could be extracted from the PDF.")

            return rows

        except Exception as e:
            logger.error(f"[PDF Extraction] Error: {str(e)}", exc_info=True)
            raise
    
    # Function: group_words_by_line
    @staticmethod
    def group_words_by_line(words, y_tol=1.5):
        """Group words by their Y coordinate to form lines"""
        if not words:
            return []
        
        items = sorted(words, key=lambda w: (w[1], w[0]))
        lines, current, current_y = [], [], None
        
        for w in items:
            y = w[1]
            if current_y is None or abs(y - current_y) <= y_tol:
                current.append(w)
                current_y = y if current_y is None else current_y
            else:
                if current:
                    lines.append(sorted(current, key=lambda x: x[0]))
                current = [w]
                current_y = y
        
        if current:
            lines.append(sorted(current, key=lambda x: x[0]))
        
        return lines
    
    # Function: make_boundaries_from_starts
    @staticmethod
    def make_boundaries_from_starts(col_starts):
        """Convert column start positions to column boundaries"""
        col_starts = sorted(col_starts, key=lambda t: t[1])
        bounds = []
        
        for i, (k, x) in enumerate(col_starts):
            end = col_starts[i + 1][1] if i < len(col_starts) - 1 else float("inf")
            bounds.append((k, x, end))
        
        return bounds
    
    # Function: _find_header_line
    @staticmethod
    def _find_header_line(lines):
        """Scan extracted word-lines for the table header; return the header line or None."""
        for line_idx, ln in enumerate(lines):
            if not ln or len(ln) < 8:
                continue
            texts = [w[4] for w in ln]
            line_text = " ".join(texts)
            line_lower = line_text.lower()
            if any(kw in line_lower for kw in ["app", "installed", "domain"]) and len(line_lower) > 100:
                logger.info(f"[InfrastructureService] Checking potential header at line {line_idx}: {line_text[:100]}")
                logger.info(f"[InfrastructureService] Header has {len(ln)} words")
                return ln
        return None

    # Function: _column_name_for_header_word
    @staticmethod
    def _column_name_for_header_word(text_lower):
        """Map one lower-cased header word to its column name, or None if unrecognized."""
        if text_lower == "app":
            return "app_id"
        if "install" in text_lower:
            return "installed_app"
        if "domain" in text_lower:
            return "domain"
        if "environ" in text_lower:
            return "environment"
        if text_lower == "hosting":
            return "hosting"
        if "hostname" in text_lower:
            return "hostname_cluster"
        if "os" in text_lower or "runtime" in text_lower:
            return "os_runtime"
        if "tech" in text_lower:
            return "tech"
        if "version" in text_lower:
            return "version"
        if "footprint" in text_lower:
            return "footprint"
        if "cloud" in text_lower or "readiness" in text_lower:
            return "cloud_readiness"
        if "recommend" in text_lower:
            return "recommendation"
        if "confid" in text_lower:
            return "confidence"
        return None

    # Function: _match_header_words_to_columns
    @staticmethod
    def _match_header_words_to_columns(header_line):
        """Map each word in the header line to a column name; return [(col_name, x_pos, text)]."""
        col_position_pairs = []
        for word in header_line:
            text = word[4]
            x_pos = word[0]
            matched_col = InfrastructureService._column_name_for_header_word(text.lower())
            if matched_col and matched_col not in [c[0] for c in col_position_pairs]:
                col_position_pairs.append((matched_col, x_pos, text))
                logger.info(f"[InfrastructureService] Matched '{text}' at X={x_pos} to column '{matched_col}'")
        return col_position_pairs

    # Function: detect_table_bounds
    @staticmethod
    def detect_table_bounds(doc, expected_columns):
        """Detect the column boundaries of the Infrastructure & Network Discovery table
        
        Expected column order (left to right):
        App ID | Installed App | Domain | Environment | Hosting | Hostname/Cluster | OS/Runtime | Tech | Version | Footprint | Cloud Readiness | Recommendation | Confidence
        """
        if not fitz or len(doc) == 0:
            return None

        page = doc[0]
        words = page.get_text("words")
        lines = InfrastructureService.group_words_by_line(words)
        logger.info(f"[InfrastructureService] Total lines extracted: {len(lines)}")

        header_line = InfrastructureService._find_header_line(lines)
        if not header_line or len(header_line) < 8:
            logger.error("[InfrastructureService] Could not find valid header line")
            return None

        col_position_pairs = InfrastructureService._match_header_words_to_columns(header_line)
        logger.info(f"[InfrastructureService] Detected {len(col_position_pairs)} columns")
        if len(col_position_pairs) < 10:
            logger.warning(f"[InfrastructureService] Only detected {len(col_position_pairs)} columns, expected 13")

        sorted_pairs = sorted(col_position_pairs, key=lambda x: x[1])
        col_boundaries = []
        for i, (col_name, x_start, _text) in enumerate(sorted_pairs):
            x_end = sorted_pairs[i + 1][1] if i < len(sorted_pairs) - 1 else float("inf")
            col_boundaries.append((col_name, x_start, x_end))
            logger.info(f"[InfrastructureService] Column '{col_name}': X={x_start} to {x_end}")

        return col_boundaries
    
    # Function: _postprocess_extracted_rows
    @staticmethod
    def _postprocess_extracted_rows(rows, expected_columns):
        """Normalize whitespace and remap unnamed columns in extracted rows (in-place)."""
        for r in rows:
            for k in r:
                r[k] = re.sub(r"\s+", " ", r[k]).strip()
        if rows and any(k.startswith("col_") for k in rows[0].keys()):
            logger.warning("[InfrastructureService] Detected unnamed columns, mapping to expected columns")
            for row in rows:
                numeric_cols = {int(k.split("_")[1]): v for k, v in row.items() if k.startswith("col_")}
                new_row = {col_name: numeric_cols.get(i, "") for i, col_name in enumerate(expected_columns)}
                row.clear()
                row.update(new_row)

    # Function: _should_skip_table_line
    @staticmethod
    def _should_skip_table_line(line_text):
        """True if this line is empty, a page header/footer, or a repeated column-header line."""
        if not line_text or re.match(r"^Page\s+\d+", line_text):
            return True
        is_column_header = re.search(
            r"(App ID|Installed|Domain|Environment|Hosting|Hostname|Recommendation|Confidence)",
            line_text, re.IGNORECASE,
        )
        if is_column_header and not line_text.startswith("APP-"):  # But don't skip if it's data starting with APP-
            return True
        return False

    # Function: _flush_current_row
    @staticmethod
    def _flush_current_row(state, log_progress=True):
        """Append state['current_row'] to state['rows'] if it has data; bump row_count."""
        current_row = state['current_row']
        if current_row and any(current_row.values()):
            state['rows'].append(current_row)
            state['row_count'] += 1
            if log_progress and state['row_count'] % 50 == 0:
                logger.info(f"[InfrastructureService] Extracted {state['row_count']} rows so far")

    # Function: _assign_word_to_column
    @staticmethod
    def _assign_word_to_column(current_row, col_bounds, text, x_pos):
        """Find which column this word belongs to by X position; fall back to the rightmost column."""
        for col_name, x_start, x_end in col_bounds:
            if x_start <= x_pos < x_end:
                current_row[col_name] = (current_row[col_name] + " " + text).strip()
                return
        if col_bounds:
            last_col = col_bounds[-1][0]
            current_row[last_col] = (current_row[last_col] + " " + text).strip()

    # Function: _assign_line_words_to_row
    @staticmethod
    def _assign_line_words_to_row(current_row, ln, col_bounds):
        """Assign words from this line to columns based on X position."""
        for w in ln:
            text = w[4]
            x_pos = w[0]
            if not text or text.isspace() or text in ["Page", "page"]:
                continue
            InfrastructureService._assign_word_to_column(current_row, col_bounds, text, x_pos)

    # Function: _process_table_line
    @staticmethod
    def _process_table_line(ln, col_bounds, state):
        """Process one non-empty table line, updating `state` in place."""
        line_text = " ".join(w[4] for w in ln).strip()
        if InfrastructureService._should_skip_table_line(line_text):
            return

        # Detect rows starting with APP-XXX pattern
        first_word = ln[0][4] if ln else ""
        is_new_row = first_word and re.match(r"APP-\d+", first_word)

        if is_new_row:
            InfrastructureService._flush_current_row(state)
            # Initialize new row with empty values for all columns
            state['current_row'] = {col_name: "" for col_name, _, _ in col_bounds}

        if state['current_row'] is not None:
            InfrastructureService._assign_line_words_to_row(state['current_row'], ln, col_bounds)

    # Function: _process_table_page
    @staticmethod
    def _process_table_page(doc, pi, col_bounds, state):
        """Process one page of the discovery table, updating `state` in place."""
        logger.info(f"[InfrastructureService] Processing page {pi + 1}/{len(doc)}")

        page = doc[pi]
        height = page.rect.height

        # Get words excluding footer area
        words = [w for w in page.get_text("words") if w[1] < height - InfrastructureService.BOTTOM_MARGIN]
        lines = InfrastructureService.group_words_by_line(words)

        logger.info(f"[InfrastructureService] Page {pi + 1} has {len(lines)} lines")

        for ln in lines:
            if not ln:
                continue
            InfrastructureService._process_table_line(ln, col_bounds, state)

    # Function: parse_table_rows
    @staticmethod
    def parse_table_rows(doc, page_indices, col_bounds, expected_columns):
        """Parse all rows from the table across multiple pages"""
        if not fitz:
            raise ImportError("PyMuPDF (fitz) is required")

        logger.info(f"[InfrastructureService] Starting to parse table rows with {len(col_bounds)} columns")
        logger.info(f"[InfrastructureService] Column bounds: {col_bounds}")

        state = {"rows": [], "current_row": None, "row_count": 0}

        for pi in page_indices:
            if pi >= len(doc):
                continue
            InfrastructureService._process_table_page(doc, pi, col_bounds, state)

        # Save the last row if it has data
        InfrastructureService._flush_current_row(state, log_progress=False)

        rows = state["rows"]
        row_count = state["row_count"]
        logger.info(f"[InfrastructureService] Total rows extracted: {row_count}")
        InfrastructureService._postprocess_extracted_rows(rows, expected_columns)
        return rows
    
    # Function: _get_sample_applications
    @staticmethod
    def _get_sample_applications():
        """Get sample discovered applications for testing/fallback"""
        return [
            {
                'app_id': 'APP-001',
                'installed_app': 'InventoryAPI',
                'domain': 'Supply Chain',
                'environment': 'prd',
                'hosting': 'Cloud',
                'hostname_cluster': 'azure-east-1',
                'os_runtime': '.NET Core 5.0',
                'tech': '.NET, PostgreSQL, REST API',
                'version': '2.1.0',
                'footprint': 'Azure',
                'cloud_readiness': 'Cloud Ready',
                'recommendation': 'Migrate to cloud',
                'confidence': 'High'
            },
            {
                'app_id': 'APP-002',
                'installed_app': 'OrderManagement',
                'domain': 'Sales',
                'environment': 'prd',
                'hosting': 'On-Premise',
                'hostname_cluster': 'ws-prod-02',
                'os_runtime': 'Windows Server 2019',
                'tech': '.NET Framework 4.7, SQL Server 2019',
                'version': '3.2.1',
                'footprint': 'On-Premise',
                'cloud_readiness': 'Modernize First',
                'recommendation': 'Modernize then migrate',
                'confidence': 'Medium'
            },
            {
                'app_id': 'APP-003',
                'installed_app': 'ReportingEngine',
                'domain': 'Finance',
                'environment': 'dev',
                'hosting': 'Hybrid',
                'hostname_cluster': 'k8s-cluster-1',
                'os_runtime': 'Java 11, Linux',
                'tech': 'Java, Spring Boot, Oracle DB',
                'version': '1.8.5',
                'footprint': 'Kubernetes',
                'cloud_readiness': 'Cloud Ready',
                'recommendation': 'Containerize and migrate',
                'confidence': 'High'
            },
        ]
    
    # Function: _extract_applications
    @staticmethod
    def _extract_applications(text):
        """Extract application information from infrastructure text"""
        # This would parse the actual extracted text from PDF
        # For now, returning empty list as extraction happens via extract_pdf_table
        return []
    
    # Function: _extract_servers
    @staticmethod
    def _extract_servers(text):
        """Extract server information from text"""
        # This would parse actual server data
        # For demo, returning sample servers
        return [
            {
                'name': 'prd-mfg-app-01',
                'environment': 'prd',
                'type': 'VM',
                'ip': '192.168.1.101',
                'footprint': 'Azure',
                'techs': ['.NET Framework', 'SQL Server', 'IIS']
            },
            {
                'name': 'k8s-eu-central-1',
                'environment': 'prd',
                'type': 'Container',
                'ip': '10.0.0.50',
                'footprint': 'Kubernetes',
                'techs': ['Kubernetes', 'Docker', 'Linux']
            },
            {
                'name': 'dev-fin-app-01',
                'environment': 'dev',
                'type': 'VM',
                'ip': '192.168.1.201',
                'footprint': 'On-Premise',
                'techs': ['Java', 'Oracle DB', 'Apache Tomcat']
            }
        ]
    
    # Function: get_infrastructure_summary
    @staticmethod
    def get_infrastructure_summary(infra_id):
        """Get summary statistics for infrastructure"""
        infra = Infrastructure.query.get(infra_id)
        if not infra:
            return None
        
        return {
            'total_vms': infra.total_vms,
            'total_k8s_clusters': infra.total_k8s_clusters,
            'orphan_systems': infra.orphan_systems,
            'total_servers': len(infra.servers),
            'total_applications': len(infra.discovered_applications),
            'network_links': len(infra.network_links)
        }

# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Service for extracting CAST data and populating CASTData table
# Date: 2025-12-09
# ---------------------------------------------------------------------------
"""Service for extracting CAST data and populating CASTData table"""

import logging
import json
import pandas as pd
from app import db
from app.models.cast import CASTData

logger = logging.getLogger(__name__)

# Function: _normalize_columns
def _normalize_columns(df):
    df.columns = [str(col).strip() for col in df.columns]
    return df


# Function: _detect_header_row
def _detect_header_row(raw_df):
    for i in range(min(len(raw_df), 15)):
        row_values = [str(v).strip().upper() for v in raw_df.iloc[i].tolist() if pd.notna(v)]
        if 'APP ID' in row_values and 'APP NAME' in row_values:
            return i
    return None


# Function: _load_cast_dataframe
def _load_cast_dataframe(file_path):
    """Read CSV or Excel file and return a normalized DataFrame with 'APP ID' header row."""
    file_ext = file_path.lower().split('.')[-1]

    if file_ext == 'csv':
        df = _normalize_columns(pd.read_csv(file_path))
        if 'APP ID' not in df.columns:
            raw_df = pd.read_csv(file_path, header=None)
            idx = _detect_header_row(raw_df)
            if idx is not None:
                header = [str(v).strip() for v in raw_df.iloc[idx].tolist()]
                df = _normalize_columns(raw_df.iloc[idx + 1:].copy())
                df.columns = header
    else:
        df = _normalize_columns(pd.read_excel(file_path))
        if 'APP ID' not in df.columns:
            raw_df = pd.read_excel(file_path, header=None)
            idx = _detect_header_row(raw_df)
            if idx is not None:
                header = [str(v).strip() for v in raw_df.iloc[idx].tolist()]
                df = _normalize_columns(raw_df.iloc[idx + 1:].copy())
                df.columns = header
    return df


# Function: _apply_column_mapping_to_record
def _apply_column_mapping_to_record(cast_record, row, dataframe, column_mapping):
    for source_col, target_field in column_mapping.items():
        if source_col not in dataframe.columns:
            continue
        value = row.get(source_col)
        if pd.isna(value):
            value = None
        if isinstance(value, str):
            value = value.strip() if value else None
        # Never overwrite app_name with None — keep existing or use app_id
        if target_field == 'app_name' and not value:
            continue
        setattr(cast_record, target_field, value)


# Function: _process_cast_excel_row
def _process_cast_excel_row(row, dataframe, column_mapping):
    """Process one row of the uploaded CAST Excel/CSV file. Returns True if a
    record was created/updated, False if the row was skipped (no app_id)."""
    app_id_raw = row.get('APP ID')
    if pd.isna(app_id_raw) or not str(app_id_raw).strip():
        return False

    app_id = str(app_id_raw).strip()
    cast_record = CASTData.query.filter_by(app_id=app_id).first()

    if not cast_record:
        cast_record = CASTData(app_id=app_id, app_name=app_id)
        db.session.add(cast_record)

    _apply_column_mapping_to_record(cast_record, row, dataframe, column_mapping)

    # Final guard: ensure app_name is never null
    if not cast_record.app_name:
        cast_record.app_name = app_id

    return True


# Function: _to_dict_or_empty
def _to_dict_or_empty(record):
    """Convert a model object to dict if needed, else pass through a plain dict."""
    if hasattr(record, 'to_dict'):
        return record.to_dict()
    return record if isinstance(record, dict) else {}


# Function: _apply_inventory_fields
def _apply_inventory_fields(cast_record, app_data):
    cast_record.programming_language = app_data.get('primary_language')
    # NOTE: application_type removed - now sourced from CorentData/IndustryData
    cast_record.repo_name = app_data.get('repo', '') or ''
    cast_record.source_code_availability = 'Available' if app_data.get('repo') else 'Not Available'

    # LOC and modules info
    if app_data.get('loc_k'):
        cast_record.application_code_complexity_volume = f"{app_data.get('loc_k')}K LOC, {app_data.get('modules')} modules"


# Function: _apply_matching_classification
def _apply_matching_classification(cast_record, app_id, extraction_result):
    """Extract quality and security metrics from the matching classification record, if any."""
    if not (hasattr(extraction_result, 'get') and extraction_result.get('application_classifications')):
        return
    for class_record in extraction_result.get('application_classifications', []):
        class_data = _to_dict_or_empty(class_record)
        if class_data.get('app_id') == app_id:
            cast_record.cloud_suitability = class_data.get('cloud_ready')
            cast_record.code_design = f"Quality: {class_data.get('quality')}, Security: {class_data.get('security')}"
            break


# Function: _upsert_cast_record_from_inventory
def _upsert_cast_record_from_inventory(app_id, app_data):
    """Get or create the CASTData record for app_id. Returns (cast_record, created)."""
    cast_record = CASTData.query.filter_by(app_id=app_id).first()

    if not cast_record:
        cast_record = CASTData(
            app_id=app_id,
            app_name=app_data.get('application', '')
        )
        db.session.add(cast_record)
        return cast_record, True

    cast_record.app_name = app_data.get('application', cast_record.app_name)
    return cast_record, False


# Function: _process_inventory_record
def _process_inventory_record(app_record, extraction_result):
    """Process one application_inventory record. Returns True if a new CASTData
    row was created, False if updated or skipped (no app_id)."""
    app_data = _to_dict_or_empty(app_record)

    app_id = app_data.get('app_id', '').strip()
    if not app_id:
        logger.warning("[CASTData] Skipping record without app_id")
        return False

    cast_record, created = _upsert_cast_record_from_inventory(app_id, app_data)
    _apply_inventory_fields(cast_record, app_data)
    _apply_matching_classification(cast_record, app_id, extraction_result)
    return created


class CASTDataService:
    """Service to extract CAST analysis data and store in CASTData table"""

    # Function: populate_from_cast_analysis
    @staticmethod
    def populate_from_cast_analysis(extraction_result):
        """
        Extract and populate CASTData from CAST analysis extraction result

        Args:
            extraction_result: Dictionary with extracted CAST data containing:
                - application_inventory: List of ApplicationInventory records
                - application_classifications: List of ApplicationClassification records

        Returns:
            int: Number of records created/updated
        """
        try:
            # Extract from application inventory and combine with classifications
            app_inventory = extraction_result.get('application_inventory', [])

            if not app_inventory:
                return 0

            records_created = 0
            for app_record in app_inventory:
                if _process_inventory_record(app_record, extraction_result):
                    records_created += 1

            db.session.commit()
            logger.info(f"[CASTData] Created/Updated {records_created} records from CAST analysis")
            return records_created

        except Exception as e:
            logger.error(f"[CASTData] Error populating from CAST analysis: {str(e)}", exc_info=True)
            db.session.rollback()
            return 0
    
    # Function: bulk_insert_from_dict
    @staticmethod
    def bulk_insert_from_dict(cast_data_list):
        """
        Bulk insert or update CASTData records from dictionary list
        
        Args:
            cast_data_list: List of dictionaries with CASTData fields
            
        Returns:
            int: Number of records inserted/updated
        """
        try:
            records_processed = 0
            
            for data_dict in cast_data_list:
                if not data_dict.get('app_id'):
                    logger.warning("[CASTData] Skipping record without app_id")
                    continue
                
                app_id = str(data_dict['app_id']).strip()
                cast_record = CASTData.query.filter_by(app_id=app_id).first()
                
                if not cast_record:
                    cast_record = CASTData(
                        app_id=app_id,
                        app_name=data_dict.get('app_name') or app_id
                    )
                    db.session.add(cast_record)
                
                # Update all available fields
                for key, value in data_dict.items():
                    if key != 'id' and hasattr(cast_record, key) and value is not None:
                        setattr(cast_record, key, value)

                # Ensure app_name is never null
                if not cast_record.app_name:
                    cast_record.app_name = app_id
                
                records_processed += 1
            
            db.session.commit()
            logger.info(f"[CASTData] Bulk inserted/updated {records_processed} records")
            return records_processed
            
        except Exception as e:
            logger.error(f"[CASTData] Error bulk inserting records: {str(e)}", exc_info=True)
            db.session.rollback()
            return 0
    
    # Function: get_by_app_id
    @staticmethod
    def get_by_app_id(app_id):
        """Retrieve CASTData by app_id"""
        try:
            return CASTData.query.filter_by(app_id=app_id).first()
        except Exception as e:
            logger.error(f"[CASTData] Error retrieving app_id {app_id}: {str(e)}")
            return None
    
    # Function: get_all
    @staticmethod
    def get_all():
        """Retrieve all CASTData records"""
        try:
            return CASTData.query.all()
        except Exception as e:
            logger.error(f"[CASTData] Error retrieving all records: {str(e)}")
            return []

    # Function: populate_from_excel_file
    @staticmethod
    def populate_from_excel_file(file_path):
        """Load CASTData rows from uploaded Excel/CSV file"""
        try:
            dataframe = _load_cast_dataframe(file_path)

            column_mapping = {
                'APP ID': 'app_id',
                'APP NAME': 'app_name',
                'REPO NAME': 'repo_name',
                'Repo Name': 'repo_name',
                'REPO': 'repo_name',
                'Repo': 'repo_name',
                'Application Architecture': 'application_architecture',
                'Source Code Availability': 'source_code_availability',
                'Programming Language': 'programming_language',
                'Component Coupling': 'component_coupling',
                'Cloud Suitability': 'cloud_suitability',
                'Volume of External Dependencies': 'volume_external_dependencies',
                'App Service / API Readiness': 'app_service_api_readiness',
                'Degree of Code Protocols': 'degree_of_code_protocols',
                'Code Design': 'code_design',
                'Application-Code Complexity / Volume': 'application_code_complexity_volume',
                'Distributed Architecture Design or not': 'distributed_architecture_design',
            }

            records_processed = 0

            with db.session.no_autoflush:
                for _, row in dataframe.iterrows():
                    if _process_cast_excel_row(row, dataframe, column_mapping):
                        records_processed += 1

            db.session.commit()
            logger.info(f"[CASTData] Loaded {records_processed} records from file: {file_path}")
            return records_processed

        except Exception as e:
            logger.error(f"[CASTData] Error loading from Excel/CSV file {file_path}: {str(e)}", exc_info=True)
            db.session.rollback()
            return 0

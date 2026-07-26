# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Service for handling Industry Templates data extraction and storage
# Date: 2025-09-06
# ---------------------------------------------------------------------------
"""Service for handling Industry Templates data extraction and storage"""

import logging
import re
import pandas as pd
from datetime import datetime
from app import db
from app.models.industry_data import IndustryTemplate, IndustryData

logger = logging.getLogger(__name__)


class IndustryDataService:
    """Service to extract Industry Templates data and store in IndustryData table"""
    
    # Expected column names in the Industry_Templates.xlsx file
    EXPECTED_COLUMNS = {
        'APP ID': 'app_id',
        'APP Name': 'app_name',
        'Business owner': 'business_owner',
        'Architecture type': 'architecture_type',
        'Platform Host': 'platform_host',
        'Application type': 'application_type',
        'Install type': 'install_type',
        'Capabilities': 'capabilities',
    }

    # ------------------------------------------------------------------ #
    # Pattern-based name / id inference (no LLM required)                 #
    # ------------------------------------------------------------------ #

    # Function: _infer_app_name
    @staticmethod
    def _infer_app_name(app_id: str, row_index: int) -> str:
        """
        Derive a human-readable application name from its ID using pattern recognition.

        Examples
        --------
        "HRMS_001"      -> "Hrms 001"
        "APP-CRM-042"   -> "App Crm 042"
        "SYS.PAYROLL.3" -> "Sys Payroll 3"
        "           "   -> "Application-22"
        """
        if not app_id or not str(app_id).strip():
            return f"Application-{row_index}"
        cleaned = str(app_id).strip()
        # Replace common separators with a space
        readable = re.sub(r"[_\-\.]+", " ", cleaned)
        # Insert a space before a run of digits that follows letters, e.g. "APP001" -> "APP 001"
        readable = re.sub(r"([A-Za-z])(\d)", r"\1 \2", readable)
        # Insert a space before an uppercase letter following a lowercase, e.g. "MyApp" -> "My App"
        readable = re.sub(r"([a-z])([A-Z])", r"\1 \2", readable)
        readable = readable.strip().title()
        return readable if readable else f"Application-{row_index}"

    # Function: _infer_app_id
    @staticmethod
    def _infer_app_id(row_index: int, row_data: dict) -> str:
        """
        Generate a synthetic APP ID for rows that have no app_id whatsoever.
        Uses the row index plus any available distinguishing field.
        """
        hint = (
            str(row_data.get("app_name") or "")
            or str(row_data.get("platform_host") or "")
            or str(row_data.get("business_owner") or "")
        )
        if hint:
            slug = re.sub(r"[^A-Za-z0-9]", "", hint)[:8].upper()
            return f"GEN-{slug}-{row_index:04d}"
        return f"GEN-{row_index:04d}"
    
    # Function: _build_column_mapping
    @staticmethod
    def _build_column_mapping(df):
        """Validate that required columns exist (case-insensitive) and map Excel columns to field names."""
        df_columns_lower = {col.lower().strip(): col for col in df.columns}
        required_cols_lower = {k.lower().strip(): v for k, v in IndustryDataService.EXPECTED_COLUMNS.items()}

        logger.info(f"[IndustryData] Required columns (lowercase): {list(required_cols_lower.keys())}")
        logger.info(f"[IndustryData] DataFrame columns (lowercase): {list(df_columns_lower.keys())}")

        column_mapping = {}
        for expected_col_lower, field_name in required_cols_lower.items():
            if expected_col_lower in df_columns_lower:
                actual_col_name = df_columns_lower[expected_col_lower]
                column_mapping[actual_col_name] = field_name
                logger.info(f"[IndustryData] Mapped '{actual_col_name}' -> '{field_name}'")
            else:
                logger.warning(f"[IndustryData] Expected column '{expected_col_lower}' not found in Excel file")

        if not column_mapping:
            raise ValueError(f"No matching columns found in Excel file. Expected columns: {', '.join(IndustryDataService.EXPECTED_COLUMNS.keys())}. Found: {', '.join(df.columns)}")

        logger.info(f"[IndustryData] Column mapping: {column_mapping}")
        return column_mapping

    # Function: _map_row_data
    @staticmethod
    def _map_row_data(row, idx, column_mapping):
        data = {}
        for excel_col, field_name in column_mapping.items():
            if excel_col in row.index:
                value = row[excel_col]
                # Convert NaN values to None
                if pd.isna(value):
                    data[field_name] = None
                else:
                    # Convert to string and strip whitespace
                    data[field_name] = str(value).strip() if not isinstance(value, (int, float)) else value
            else:
                logger.warning(f"[IndustryData] Column '{excel_col}' not found in row {idx + 2}")
                data[field_name] = None
        return data

    # Function: _normalize_app_identity
    @staticmethod
    def _normalize_app_identity(value):
        """Treat blank strings and the literal 'None' the same as None."""
        if not value or (isinstance(value, str) and (not value.strip() or value.strip().lower() == 'none')):
            return None
        return value

    # Function: _has_other_content
    @staticmethod
    def _has_other_content(data):
        return any(
            v is not None and str(v).strip() not in ('', 'None', 'nan')
            for k, v in data.items()
            if k not in ('app_id', 'app_name')
        )

    # Function: _upsert_industry_record
    @staticmethod
    def _upsert_industry_record(data, app_id, template_id):
        industry_record = IndustryData.query.filter_by(app_id=app_id).first()

        if industry_record:
            # Update existing record
            for key, value in data.items():
                setattr(industry_record, key, value)
            industry_record.template_id = template_id
            logger.info(f"[IndustryData] Updated record for APP ID: {app_id}")
        else:
            # Create new record
            industry_record = IndustryData(
                template_id=template_id,
                **data
            )
            db.session.add(industry_record)
            logger.info(f"[IndustryData] Created new record for APP ID: {app_id}")

    # Function: _process_industry_row
    @staticmethod
    def _process_industry_row(idx, row, column_mapping, template_id):
        """Process one Excel row. Returns 'skipped', or a bool: True if any
        field was predicted from pattern inference, False otherwise."""
        data = IndustryDataService._map_row_data(row, idx, column_mapping)

        # ── Recover missing app_id / app_name via pattern inference ──
        app_id = IndustryDataService._normalize_app_identity(data.get('app_id'))
        app_name = IndustryDataService._normalize_app_identity(data.get('app_name'))

        row_num = idx + 2   # 1-based header row + 0-based index

        # Truly empty row (no id AND no name AND no other content) → skip
        if app_id is None and app_name is None and not IndustryDataService._has_other_content(data):
            logger.debug(f"[IndustryData] Row {row_num} skipped: completely empty.")
            return 'skipped'

        # Predict missing app_id from row context
        predicted_fields = []
        if app_id is None:
            app_id = IndustryDataService._infer_app_id(row_num, data)
            data['app_id'] = app_id
            predicted_fields.append('app_id')
            logger.info(
                f"[IndustryData] Row {row_num}: app_id predicted from pattern → '{app_id}'"
            )

        # Predict missing app_name from app_id pattern
        if app_name is None:
            app_name = IndustryDataService._infer_app_name(app_id, row_num)
            data['app_name'] = app_name
            predicted_fields.append('app_name')
            logger.info(
                f"[IndustryData] Row {row_num}: app_name predicted from pattern → '{app_name}'"
            )

        IndustryDataService._upsert_industry_record(data, app_id, template_id)

        return bool(predicted_fields)

    # Function: extract_from_excel
    @staticmethod
    def extract_from_excel(file_path, filename):
        """
        Extract Industry Templates data from Excel file

        Args:
            file_path: Full path to the Excel file
            filename: Original filename for metadata

        Returns:
            tuple: (file_id, IndustryTemplate object, records_count)
        """
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)

            logger.info(f"[IndustryData] Loaded Excel file: {filename} with {len(df)} rows")
            logger.info(f"[IndustryData] Columns found: {list(df.columns)}")

            column_mapping = IndustryDataService._build_column_mapping(df)

            # Create IndustryTemplate metadata record
            import uuid
            file_id = str(uuid.uuid4())

            # Check for duplicate file
            existing_template = IndustryTemplate.query.filter_by(filename=filename).first()
            if existing_template:
                # Delete old records associated with this file
                IndustryData.query.filter_by(template_id=existing_template.id).delete()
                db.session.delete(existing_template)
                db.session.commit()
                logger.info(f"[IndustryData] Deleted existing template for: {filename}")

            # Create new template
            template = IndustryTemplate(
                file_id=file_id,
                filename=filename,
                file_path=file_path
            )
            db.session.add(template)
            db.session.flush()  # Flush to get the template ID
            template_id = template.id

            # Process and insert data rows
            records_created  = 0
            records_predicted = 0   # rows where at least one field was inferred
            errors = []

            for idx, row in df.iterrows():
                try:
                    outcome = IndustryDataService._process_industry_row(idx, row, column_mapping, template_id)
                    if outcome == 'skipped':
                        continue

                    records_created += 1
                    if outcome:
                        records_predicted += 1

                except Exception as e:
                    error_msg = f"Row {idx + 2}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"[IndustryData] Error processing row {idx + 2}: {str(e)}", exc_info=True)
                    continue

            # Update template record count and processed timestamp
            template.record_count = records_created
            template.processed_at = datetime.utcnow()

            # Commit all changes
            db.session.commit()

            logger.info(
                f"[IndustryData] Successfully processed {records_created} records "
                f"({records_predicted} had fields predicted from patterns) from {filename}"
            )
            if errors:
                logger.warning(f"[IndustryData] Encountered {len(errors)} errors during processing: {errors}")

            return file_id, template, records_created, errors

        except Exception as e:
            logger.error(f"[IndustryData] Error extracting from Excel: {str(e)}", exc_info=True)
            db.session.rollback()
            raise
    
    # Function: get_all_industry_data
    @staticmethod
    def get_all_industry_data(template_id=None):
        """
        Get all Industry Data records, optionally filtered by template
        
        Args:
            template_id: Optional template ID to filter
            
        Returns:
            list: List of IndustryData dictionaries
        """
        try:
            if template_id:
                records = IndustryData.query.filter_by(template_id=template_id).all()
            else:
                records = IndustryData.query.all()
            
            return [record.to_dict() for record in records]
        except Exception as e:
            logger.error(f"[IndustryData] Error retrieving industry data: {str(e)}", exc_info=True)
            return []
    
    # Function: get_templates_with_count
    @staticmethod
    def get_templates_with_count():
        """
        Get all templates with their record counts
        
        Returns:
            list: List of template dictionaries with record counts
        """
        try:
            templates = IndustryTemplate.query.all()
            results = []
            for template in templates:
                data = template.to_dict()
                data['record_count'] = IndustryData.query.filter_by(template_id=template.id).count()
                results.append(data)
            return results
        except Exception as e:
            logger.error(f"[IndustryData] Error retrieving templates: {str(e)}", exc_info=True)
            return []
    
    # Function: delete_template
    @staticmethod
    def delete_template(template_id):
        """
        Delete a template and all associated industry data
        
        Args:
            template_id: Template ID to delete
            
        Returns:
            int: Number of records deleted
        """
        try:
            # Delete associated industry data
            records_deleted = IndustryData.query.filter_by(template_id=template_id).delete()
            
            # Delete template
            template = IndustryTemplate.query.filter_by(id=template_id).first()
            if template:
                db.session.delete(template)
                db.session.commit()
                logger.info(f"[IndustryData] Deleted template {template_id} and {records_deleted} associated records")
            
            return records_deleted
        except Exception as e:
            logger.error(f"[IndustryData] Error deleting template: {str(e)}", exc_info=True)
            db.session.rollback()
            return 0

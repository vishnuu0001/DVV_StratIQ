# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Service for importing Business Capabilities from Excel
# Date: 2025-12-19
# ---------------------------------------------------------------------------
"""Service for importing Business Capabilities from Excel"""
import logging
import pandas as pd
from app import db
from app.models.infrastructure import BusinessCapabilities

logger = logging.getLogger(__name__)


class BusinessCapabilitiesService:
    """Service for managing business capabilities data"""
    
    # Function: _extract_row_fields
    @staticmethod
    def _extract_row_fields(row) -> dict:
        return {
            'business_owner':    str(row.get('Business owner', '')).strip() or None,
            'architecture_type': str(row.get('Architecture type', '')).strip() or None,
            'platform_host':     str(row.get('Platform Host', '')).strip() or None,
            'application_type':  str(row.get('Application type', '')).strip() or None,
            'install_type':      str(row.get('Install type', '')).strip() or None,
            'capabilities':      str(row.get('Capabilities', '')).strip() or None,
        }

    # Function: _import_row
    @staticmethod
    def _import_row(row, idx) -> str:
        """Import one Excel row into BusinessCapabilities; return 'created', 'updated', or 'skipped'."""
        app_id = str(row.get('APP ID', '')).strip()
        name = str(row.get('Name', '')).strip()

        # Skip if required fields are missing
        if not app_id or not name:
            logger.warning(f"[BusinessCapabilitiesService] Skipping row {idx + 2}: missing APP ID or Name")
            return 'skipped'

        fields = BusinessCapabilitiesService._extract_row_fields(row)
        existing = BusinessCapabilities.query.filter_by(app_id=app_id).first()

        if existing:
            existing.name = name
            for key, value in fields.items():
                setattr(existing, key, value)
            return 'updated'

        capability = BusinessCapabilities(app_id=app_id, name=name, **fields)
        db.session.add(capability)
        return 'created'

    # Function: import_from_excel
    @staticmethod
    def import_from_excel(excel_path):
        """Import Business Capabilities from Excel file

        Expected columns: APP ID, Name, Business owner, Architecture type, Platform Host, Application type, Install type, Capabilities
        """
        try:
            logger.info(f"[BusinessCapabilitiesService] Reading Excel file: {excel_path}")

            # Read the Excel file
            df = pd.read_excel(excel_path)

            logger.info(f"[BusinessCapabilitiesService] Loaded {len(df)} rows from Excel")

            # Track counts
            created_count = 0
            updated_count = 0
            skipped_count = 0

            # Import each row
            for idx, row in df.iterrows():
                try:
                    status = BusinessCapabilitiesService._import_row(row, idx)
                except Exception as row_error:
                    logger.error(f"[BusinessCapabilitiesService] Error processing row {idx + 2}: {str(row_error)}")
                    skipped_count += 1
                    continue

                if status == 'created':
                    created_count += 1
                elif status == 'updated':
                    updated_count += 1
                else:
                    skipped_count += 1
                    continue

                if (created_count + updated_count) % 500 == 0:
                    logger.info(f"[BusinessCapabilitiesService] Processed {created_count + updated_count} records...")

            # Commit all changes
            db.session.commit()
            
            logger.info("[BusinessCapabilitiesService] Import completed:")
            logger.info(f"  Created: {created_count}")
            logger.info(f"  Updated: {updated_count}")
            logger.info(f"  Skipped: {skipped_count}")
            logger.info(f"  Total: {created_count + updated_count}")
            
            return {
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'total': created_count + updated_count
            }
        
        except Exception as e:
            logger.error(f"[BusinessCapabilitiesService] Import failed: {str(e)}", exc_info=True)
            db.session.rollback()
            raise
    
    # Function: get_all
    @staticmethod
    def get_all():
        """Get all business capabilities"""
        return BusinessCapabilities.query.all()
    
    # Function: get_by_app_id
    @staticmethod
    def get_by_app_id(app_id):
        """Get business capability by APP ID"""
        return BusinessCapabilities.query.filter_by(app_id=app_id).first()
    
    # Function: search
    @staticmethod
    def search(query):
        """Search business capabilities by name or capabilities"""
        return BusinessCapabilities.query.filter(
            db.or_(
                BusinessCapabilities.name.ilike(f"%{query}%"),
                BusinessCapabilities.capabilities.ilike(f"%{query}%"),
                BusinessCapabilities.app_id.ilike(f"%{query}%")
            )
        ).all()

# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Database migration script to add close_notes and work_notes columns to sn_incidents table.
# Date: 2026-06-19
# ---------------------------------------------------------------------------
"""
Database migration script to add close_notes and work_notes columns to sn_incidents table.
Run this once to update existing database schema.
"""
import logging
from backend.services.postgres_store import ensure_common_schema, get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function: migrate_add_resolution_columns
def migrate_add_resolution_columns():
    """
    Add close_notes and work_notes columns to sn_incidents table if they don't exist.
    """
    ensure_common_schema()
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check if columns already exist
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'sn_incidents'
                AND column_name IN ('close_notes', 'work_notes')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
            
            if 'close_notes' not in existing_columns:
                logger.info("Adding close_notes column to sn_incidents table...")
                cur.execute("ALTER TABLE sn_incidents ADD COLUMN close_notes TEXT")
                logger.info("✅ close_notes column added")
            else:
                logger.info("close_notes column already exists")
            
            if 'work_notes' not in existing_columns:
                logger.info("Adding work_notes column to sn_incidents table...")
                cur.execute("ALTER TABLE sn_incidents ADD COLUMN work_notes TEXT")
                logger.info("✅ work_notes column added")
            else:
                logger.info("work_notes column already exists")
        
        conn.commit()
    
    logger.info("✅ Migration completed successfully!")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("DATABASE MIGRATION: Add Resolution Columns")
    logger.info("=" * 80)
    migrate_add_resolution_columns()
    logger.info("=" * 80)
    logger.info("Migration complete! You can now use the enhanced Dashboard features.")
    logger.info("=" * 80)

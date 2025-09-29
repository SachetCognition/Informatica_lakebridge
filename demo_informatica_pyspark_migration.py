#!/usr/bin/env python3
"""
Demonstration script for migrating Informatica PowerCenter workflows to PySpark
using the BladeBridge transpiler.

This script shows the complete workflow:
1. Configure BladeBridge for PYSPARK target
2. Process Informatica XML files
3. Generate PySpark notebooks and workflow definitions
"""

import asyncio
import logging
from pathlib import Path
import tempfile
import shutil

from databricks.sdk import WorkspaceClient
from databricks.labs.lakebridge.config import TranspileConfig
from databricks.labs.lakebridge.transpiler.execute import transpile
from databricks.labs.lakebridge.transpiler.installers import WheelInstaller
from databricks.labs.lakebridge.transpiler.lsp.lsp_engine import LSPEngine
from databricks.labs.lakebridge.transpiler.repository import TranspilerRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demonstrate_informatica_pyspark_migration():
    """Demonstrate the complete Informatica PowerCenter to PySpark migration process."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        labs_path = temp_path / "labs"
        output_folder = temp_path / "pyspark_output"
        output_folder.mkdir(parents=True, exist_ok=True)
        
        logger.info("Setting up BladeBridge transpiler...")
        
        transpiler_repository = TranspilerRepository(labs_path)
        
        WheelInstaller(transpiler_repository, "bladebridge", "databricks-bb-plugin", None).install()
        config_path = transpiler_repository.transpiler_config_path("Bladebridge")
        lsp_engine = LSPEngine.from_config_path(config_path)
        
        input_source = Path(__file__).parent / "tests" / "resources" / "functional" / "informatica"
        
        transpile_config = TranspileConfig(
            transpiler_config_path=str(config_path),
            source_dialect="informatica (desktop edition)",
            input_source=str(input_source),
            output_folder=str(output_folder),
            skip_validation=True,
            catalog_name="catalog",
            schema_name="schema",
            transpiler_options={"target-tech": "PYSPARK"},
        )
        
        logger.info(f"Starting migration from {input_source} to {output_folder}")
        logger.info("Configuration: Informatica PowerCenter -> PySpark")
        
        ws = None
        
        try:
            await transpile(ws, lsp_engine, transpile_config)
            
            logger.info("Migration completed successfully!")
            logger.info("Generated PySpark files:")
            
            for file_path in output_folder.rglob("*"):
                if file_path.is_file():
                    logger.info(f"  - {file_path.name} ({file_path.suffix})")
            
            results_dir = Path("migration_results")
            if results_dir.exists():
                shutil.rmtree(results_dir)
            shutil.copytree(output_folder, results_dir)
            logger.info(f"Results copied to {results_dir} for inspection")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(demonstrate_informatica_pyspark_migration())
    if success:
        print("\n✅ Informatica PowerCenter to PySpark migration demonstration completed successfully!")
        print("Check the 'migration_results' directory for generated PySpark files.")
    else:
        print("\n❌ Migration demonstration failed. Check the logs for details.")

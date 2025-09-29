# Informatica PowerCenter to PySpark Migration Guide

This guide demonstrates how to migrate Informatica PowerCenter workflows and mappings to PySpark using the BladeBridge transpiler.

## Prerequisites

- Informatica PowerCenter desktop edition (Cloud edition not currently supported)
- Access to the PowerCenter repository for metadata export
- BladeBridge transpiler installed via Lakebridge

## Migration Process

### Step 1: Export Informatica Metadata

Use `pmrep` commands to extract workflows from the PowerCenter repository:

```bash
# Connect to repository
pmrep connect <credentials>

# Get list of folders
pmrep listobjects -o FOLDER

# For each folder, get list of workflows
pmrep listobjects -o WORKFLOW -f <folder_name>

# Export workflow (create batch script for multiple workflows)
pmrep objectexport -n workflow_name -o WORKFLOW -f folder_name -b -r -m -s -u path-to-output-file
```

### Step 2: Configure BladeBridge for PySpark

The transpiler configuration supports PYSPARK as a target technology:

```yaml
"informatica (desktop edition)":
  - flag: "target-tech"
    method: CHOICE
    prompt: "Specify which technology should be generated"
    choices: [ SPARKSQL, PYSPARK ]
```

### Step 3: Run the Migration

Use the Lakebridge CLI to perform the transpilation:

```bash
databricks labs lakebridge transpile \
  --transpiler-config-path <path-to-bladebridge-config> \
  --source-dialect "informatica (desktop edition)" \
  --input-source <path-to-informatica-xml-files> \
  --output-folder <path-to-output-directory> \
  --skip-validation true \
  --catalog-name <your-catalog> \
  --schema-name <your-schema>
```

With transpiler options:
```bash
# Add transpiler-specific options for PySpark target
--transpiler-options '{"target-tech": "PYSPARK"}'
```

### Step 4: Expected Outputs

The migration generates the following PySpark artifacts:

- **PySpark Notebooks** (`.py` files) - ETL logic translated to PySpark code
- **Workflow Definitions** (`.json` files) - Databricks workflow configurations
- **Parameter Files** (`_params.py` files) - Workflow parameters and configurations

### Example: Sample Workflow Migration

The repository includes a sample Informatica workflow (`wf_m_employees_load.XML`) that demonstrates:

- Source Qualifier transformations
- Expression transformations with complex logic
- Aggregator transformations
- Filter transformations
- Target loading operations

When migrated to PySpark, this generates:
- `m_employees_load.py` - Main PySpark transformation logic
- `wf_m_employees_load.json` - Workflow definition
- `wf_m_employees_load_params.py` - Workflow parameters

## Features Supported

- Pre/post source/target stored procedure calls
- Automatic mapplet conversion
- Complex expression transformations
- Aggregation operations
- Filtering logic
- Databricks-compatible notebook generation

## Running the Demonstration

Execute the demonstration script to see the complete migration process:

```bash
python demo_informatica_pyspark_migration.py
```

This will process the sample Informatica XML file and generate corresponding PySpark artifacts in the `migration_results` directory.

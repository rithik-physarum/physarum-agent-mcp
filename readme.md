# Physarum MCP Agent

A powerful Machine Learning Project Generator agent built using the Model Context Protocol (MCP). This agent facilitates the automated creation of end-to-end machine learning projects with best practices and modern tooling.

## Overview

The Physarum MCP Agent is designed to streamline the process of creating machine learning projects by automating the setup of data processing pipelines, model training workflows, and evaluation frameworks. It integrates with cloud storage (S3) and provides a robust architecture for ML project development.

## Features

- **Automated ML Project Generation**: Creates complete ML project structures with:

  - Data cleaning and preprocessing pipelines
  - Feature engineering frameworks
  - Model selection and training workflows
  - Evaluation metrics and validation systems
  - Documentation and code organization

- **Cloud Integration**:

  - Direct integration with S3 for data access
  - Supports various data formats and sources

- **Server Architecture**:
  - FastAPI-based MCP server
  - Server-Sent Events (SSE) for real-time progress updates
  - Asynchronous processing for better performance

## Technical Stack

- **Core Technologies**:

  - Python 3.10+
  - FastAPI
  - Starlette
  - HTTPX
  - Uvicorn
  - MCP (Model Context Protocol)

- **Dependencies**:
  ```
  httpx>=0.26.0
  python-dotenv>=1.1.0
  mcp<1.5,>=1.4.1
  fastapi
  starlette
  uvicorn
  ```

## Project Structure

```
agent_mcp/
├── core/
│   ├── __init__.py
│   └── tools/
│       ├── __init__.py
│       ├── physarum_agent_tools.py  # Core agent functionality
│       └── service.py               # Server implementation
├── setup.py                         # Package configuration
└── README.md                        # Project documentation
```

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd agent_mcp
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Usage

1. Start the MCP Server:

   ```bash
   python -m core.tools.service
   ```

   The server will start on `http://0.0.0.0:8002` by default.

2. Generate an ML Project:
   ```python
   # Example API call
   {
     "user_prompt": "Create ML project with data cleaning and model selection",
     "target_variable": "target_column",
     "file_path": "s3://bucket-name/data.csv",
     "download_location": "/path/to/output/"
   }
   ```

## API Endpoints

- `/generate-ml-project/`: Main endpoint for ML project generation
- `/sse`: Server-Sent Events endpoint for progress updates
- `/messages/`: Message handling endpoint for SSE communication

## Environment Variables

- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8002)
- Additional environment variables can be configured via `.env` file

## Features of Generated ML Projects

Generated ML projects include:

1. **Data Processing**:

   - Automated data cleaning
   - Missing value handling
   - Outlier detection and treatment
   - Data type conversions

2. **Feature Engineering**:

   - Automated feature creation
   - Feature selection
   - Feature importance analysis
   - Scaling and normalization

3. **Model Development**:

   - Multiple algorithm comparison
   - Hyperparameter tuning
   - Cross-validation
   - Model selection

4. **Evaluation**:
   - Performance metrics
   - Validation frameworks
   - Model interpretability
   - Results visualization

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

[Specify License]

## Contact

[Specify Contact Information]

---

**Note**: This project is part of the Physarum AI ecosystem, designed to streamline and automate machine learning workflows.

import uvicorn
import os
from physarum_agent_tools import starlette_app

# Environment variable configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8002"))  # Set default port to 8002


def run():
    """Start the FastAPI server with uvicorn"""
    print(f"Starting MCP Server on {HOST}:{PORT}")
    uvicorn.run(starlette_app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    run()
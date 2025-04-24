from fastapi import Request, BackgroundTasks
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
import httpx
import logging
import uuid
from mcp.server.fastmcp import FastMCP
import mcp.types as types
from starlette.routing import Route
from starlette.applications import Starlette
import uvicorn
import os
import zipfile

logger = logging.getLogger(__name__)

mcp = FastMCP("agent")

write_stream = None

sse = SseServerTransport("/messages/")

BACKEND_URL = "http://physarum-alb-959199627.us-east-1.elb.amazonaws.com"


async def send_sse_message(message):
    """Send a message to the connected SSE client"""
    global write_stream
    
    if write_stream is None:
        logger.warning("No active write stream available for sending message")
        return
        
    logger.info(f"Sending SSE message: {message[:50]}...")
    
    rpc_message = types.JSONRPCMessage(
        jsonrpc="2.0",
        method="mcp/event",
        params={"message": message},
        id=str(uuid.uuid4())
    )
    
    try:
        await write_stream.send(rpc_message)
        logger.info("Message sent successfully")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        write_stream = None

def messages_docs():
    """
    Messages endpoint for SSE communication

    This endpoint is used for posting messages to SSE clients.
    Note: This route is for documentation purposes only.
    The actual implementation is handled by the SSE transport.
    """
    pass

async def handle_sse(request: Request, background_tasks: BackgroundTasks = None):
    """
    SSE endpoint that connects to the MCP server

    This endpoint establishes a Server-Sent Events connection with the client
    and forwards communication to the Model Context Protocol server.
    """
    global write_stream
    
    logger.info("New SSE connection established")
    
    if background_tasks:
        request.state.background_tasks = background_tasks
    
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream_local,
    ):
        try:
            write_stream = write_stream_local
            logger.info("Registered global write stream for messaging")
            
            init_options = mcp._mcp_server.create_initialization_options()
            
            await mcp._mcp_server.run(
                read_stream,
                write_stream_local,
                init_options,
            )
        finally:
            write_stream = None
            logger.info("Cleared global write stream reference")

routes = [
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ]

async def proxy_ml_project_stream(user_prompt, target_variable, file_path, download_location):
    """
    Background task that proxies ML project generation events from backend to clients
    """
    logger.info(f"Starting ML project generation for prompt: {user_prompt}")
    try:
        async with httpx.AsyncClient(timeout=3600) as client:
                logger.info(f"Making streaming request to {BACKEND_URL}/generate-ml-project/")
                print(f"Making streaming request to {BACKEND_URL}/generate-ml-project/")
                download_url = None
                
                async with client.stream(
                    "POST", 
                    f"{BACKEND_URL}/generate-ml-project/",
                    data={
                        "user_prompt": user_prompt,
                        "target_variable": target_variable,
                        "file_path": file_path,
                        "sse": True
                    },
                    timeout=3600
                ) as response:
                    response.raise_for_status()
                    logger.info(f"Streaming response started, status: {response.status_code}")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            message = line[5:].strip()
                            
                            if message.startswith("download:"):
                                download_url = f"{BACKEND_URL}{message[10:].strip()}"
                                break
                            else:
                                await send_sse_message(message)  
                                logger.info(f"Forwarded event: {message[:50]}...")
                logger.info(f"Received download URL: {download_url}")
                
                await download_file(client, download_url, download_location)
                # return response.body
                # local_download_url = f"/downloads/{file_name}"
                
                await send_sse_message(f"download_ready: {download_location}")
                logger.info(f"File downloaded and available at: {download_location}")
                
                if download_url is None:
                    logger.info("No download URL received in SSE, checking if response is a zip file")
                return f"Suceesfully created ml project with expected specifications inside Project_Directory folder at {download_location}"
    except Exception as e:
        error_message = f"Error during ML project generation: {str(e)}"
        logger.error(error_message)
        # await send_sse_message(f"Error: {str(e)}")
        return error_message

async def download_file(client, download_url, download_location):
    """
    Download a file from a URL and save it to the specified path
    """
    logger.info(f"Downloading file from {download_url} to {download_location}")
    async with client.stream("GET", download_url) as response:
        response.raise_for_status()
        
        # Create a temporary zip file path
        if not download_location.endswith('/'):
            download_location = f"{download_location}/"
        else:
            temp_zip_path = f"{download_location}ml_project.zip"
        
        # Download the response content to temporary zip file
        with open(temp_zip_path, 'wb') as f:
            async for chunk in response.aiter_bytes(chunk_size=8192):
                f.write(chunk)
        
        # Check if download_location is a directory path
        if os.path.isdir(download_location) or download_location.endswith('/'):
            # Ensure directory exists
            os.makedirs(download_location, exist_ok=True)
            
            # Extract zip contents to the directory
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_location)
            
            # Clean up temporary zip file
            os.remove(temp_zip_path)
        else:
            # If it's a file path, just rename the temporary file
            os.rename(temp_zip_path, download_location)
    
    logger.info(f"File downloaded successfully to {download_location}")
    # return download_location

@mcp.tool()
async def generate_ml_project(
    user_prompt: str, 
    target_variable: str, 
    file_path: str,
    download_location: str = None
) -> str:
    """
    Start ML project generation in background and return immediately.
    
    Args:
        user_prompt: Description of what the user wants to accomplish
        target_variable: Column name to use as target variable for prediction
        file_path: Path to the data file
        sse: Whether to use Server-Sent Events for streaming updates
        
    Returns:
        A message indicating the task has started
    """
    data = await proxy_ml_project_stream(user_prompt, target_variable, file_path, download_location)
    print(f"Proxy ML project stream data: {data}")
    return data

starlette_app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=8002)

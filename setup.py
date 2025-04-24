from setuptools import setup, find_packages

setup(
    name="agent_mcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.26.0",
        "python-dotenv>=1.1.0",
        "mcp<1.5,>=1.4.1",
        "fastapi",
        "starlette",
        "uvicorn"
    ],
    python_requires=">=3.10",
) 
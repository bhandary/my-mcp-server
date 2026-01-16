import os

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl
from dotenv import load_dotenv
from typing import Dict
import random

from utils.auth import create_auth0_verifier

# Load environment variables from .env file
load_dotenv()

# Get Auth0 configuration from environment
auth0_domain = os.getenv("AUTH0_DOMAIN")
resource_server_url = os.getenv("RESOURCE_SERVER_URL")

if not auth0_domain:
    raise ValueError("AUTH0_DOMAIN environment variable is required")
if not resource_server_url:
    raise ValueError("RESOURCE_SERVER_URL environment variable is required")

# Initialize Auth0 token verifier
token_verifier = create_auth0_verifier()

# Create an MCP server with OAuth authentication
mcp = FastMCP(
    name="Weather MCP Server",
    description="Provides weather information for a given city",

    # OAuth Configuration
    token_verifier=token_verifier,
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(f"https://{auth0_domain}/"),
        resource_server_url=AnyHttpUrl(resource_server_url),
        required_scopes=["openid", "profile", "email", "address", "phone"],
    ),
)

@mcp.tool()
def get_weather(city: str) -> Dict:
    temperatures = [18, 20, 22, 25, 28, 30]
    conditions = ["Sunny", "Cloudy", "Rainy", "Windy", "Partly Cloudy"]

    return {
        "city": city,
        "temperature_celsius": random.choice(temperatures),
        "condition": random.choice(conditions),
        "humidity_percent": random.randint(40, 80)
    }

app = mcp.http_app(path="/mcp")
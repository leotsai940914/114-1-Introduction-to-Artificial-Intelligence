import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset, 
    StdioServerParameters,
    SseConnectionParams,
)
import requests
import os
from dotenv import load_dotenv

# -------------------------------------------------------------
# 🌍 Initialize environment
# -------------------------------------------------------------
load_dotenv()

# -------------------------------------------------------------
# 🌦️ Weather Tool
# -------------------------------------------------------------
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.
    Args:
        city (str): The name of the city for which to retrieve the weather report.
        The city name must be in English.
    Returns:
        dict: status and result or error msg.
    """
    api_key = os.getenv("OPEN_WEATHER_MAP_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "error_message": "API key for OpenWeatherMap is not set.",
        }
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["cod"] != 200:
            return {
                "status": "error",
                "error_message": f"Weather information for '{city}' is not available.",
            }
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        report = (
            f"The weather in {city} is {weather_description} with a temperature of "
            f"{temperature} degrees Celsius."
        )
        return {"status": "success", "report": report}
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while fetching the weather data: {str(e)}",
        }


# -------------------------------------------------------------
# 🕒 Time Tool
# -------------------------------------------------------------
def get_current_time(tz_identifier: str) -> dict:
    """Returns the current time in a specified time zone identifier.
    Args:
        tz_identifier (str): The time zone identifier for which to retrieve the current time.
    Returns:
        dict: status and result or error msg.
    """
    try:
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        report = f'The current time is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        return {"status": "success", "report": report}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while fetching the current time: {str(e)}",
        }


# -------------------------------------------------------------
# 🤖 Agent Definition
# -------------------------------------------------------------
root_agent = LlmAgent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description=("Agent to answer questions about weather, time, mood, and manage shared files."),
    instruction=(
        """
        你是一個能回答時間、天氣與心情問題，也能操作指定資料夾檔案的智慧代理。
        檔案操作範圍限於 /Users/tsaichengyu/Documents/Projects/ai/test_file_share_20250922。
        當你呼叫工具時，若涉及城市名稱請使用英文。
        請用繁體中文回答問題。
        """
    ),
    tools=[
        # --- Local Python Tools ---
        get_weather,
        get_current_time,

        # -------------------------------------------------------------
        # 🌤️ Local MCP server: weather2mood
        # 提供 get_mood、read_file、write_file、list_directory
        # -------------------------------------------------------------
        MCPToolset(
            connection_params=StdioServerParameters(
                command="/Users/tsaichengyu/.local/bin/uv",
                args=[
                    "--directory",
                    "/Users/tsaichengyu/Documents/Projects/ai/20251013-weather2mood",
                    "run",
                    "server.py",
                ]
            ),
            tool_filter=[
                "get_mood",          # 💬 心情生成工具
                "read_file",         # 📂 讀取檔案
                "write_file",        # ✍️ 寫入檔案
                "list_directory",    # 📁 列出資料夾檔案
            ],
        ),

        # -------------------------------------------------------------
        # 🌐 Remote SSE MCP server (CoinGecko or others)
        # -------------------------------------------------------------
        MCPToolset(
            connection_params=SseConnectionParams(
                url="https://mcp.api.coingecko.com/sse",
            ),
        ),

        # -------------------------------------------------------------
        # 🪙 Local custom MCP SSE server (your own tool)
        # -------------------------------------------------------------
        MCPToolset(
            connection_params=SseConnectionParams(
                url="http://127.0.0.1:5002/sse",  # 你自建的本地 SSE MCP server
            ),
        ),
    ],
)
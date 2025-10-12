import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
import requests
import os
from dotenv import load_dotenv, dotenv_values

# Load environment variables from .env file
load_dotenv()

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.
    Args:
        city (str): The name of the city for which to retrieve the weather report.
        The city name must be in English.
    Returns:
        dict: status and result or error msg.
    """
    # if city.lower() == "new york":
    #     return {
    #         "status": "success",
    #         "report": (
    #             "The weather in New York is sunny with a temperature of 25 degrees"
    #             " Celsius (77 degrees Fahrenheit)."
    #         ),
    #     }
    # else:
    #     return {
    #         "status": "error",
    #         "error_message": f"Weather information for '{city}' is not available.",
    #     }
    api_key = os.getenv("OPEN_WEATHER_MAP_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "error_message": "API key for OpenWeatherMap is not set.",
        }
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        print(data)
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


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.
    Args:
        city (str): The name of the city for which to retrieve the current time.
    Returns:
        dict: status and result or error msg.
    """

    city_taiwan = ["taipei", "zhongli", "taoyuan", "kaohsiung", "taichung"]

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    elif city.lower() in city_taiwan:
        tz_identifier = "Asia/Taipei"
    else:
        return {
            "status": "error",
            "error_message": (f"Sorry, I don't have timezone information for {city}."),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    return {"status": "success", "report": report}

def ncu_calender(date: str) -> dict:
    """
    查詢中央大學行事曆特定日期的資訊
    Args:
        date (str): 日期格式 'YYYY-MM-DD'
    Returns:
        dict: status and result or error msg.
    """
    the_calendar = {
        "2024-09-29": "教師節補假",
        "2024-10-06": "中秋節放假"
    }
    
    if date in the_calendar:
        return {
            "status": "success", 
            "report": f"{date} 的行事曆資訊: {the_calendar[date]}"
        }
    else:
        return {
            "status": "error", 
            "error_message": f"抱歉，{date} 沒有特別的行事曆資訊。"

        }
    
root_agent = LlmAgent(
    name="weather_time_agent",
    model="gemini-2.0-flash-lite",
    description=("Agent to answer questions about the time and weather in a city."),
    instruction=(
        """
        You are a helpful agent who can answer user questions about the time and weather in a city.
        When you call a tool, you must use English for the city name.
        請用繁體中文回答問題。
        你也可以查詢中央大學行事曆，輸入日期格式 YYYY-MM-DD。
        """
    ),
    tools=[
        get_weather, 
        get_current_time,
        ncu_calender,
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "C:\\Users\\蔡晟郁\\OneDrive - taiwan2021t\\桌面\\114-1 AI人工智慧導論\\test_file_share_20250922",
                ],
            ),
        ),
    ],
)

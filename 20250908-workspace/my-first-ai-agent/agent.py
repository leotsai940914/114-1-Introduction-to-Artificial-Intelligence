import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
import requests
import os
from dotenv import load_dotenv, dotenv_values
# importing module
#from geopy.geocoders import Nominatim
#from timezonefinder import TimezoneFinder

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


def get_current_time(tz_identifier: str) -> dict:
    """Returns the current time in a specified time zone identifier.
    Args:
        tz_identifier (str): The time zone identifier for which to retrieve the current time.
        ex. New York -> "America/New_York", Taipei -> "Asia/Taipei", etc.
        But sometimes the city name is not the same as the tz_identifier.
        ex. Taoyuan -> "Asia/Taipei", Kaohsiung -> "Asia/Taipei", etc.
    Returns:
        dict: status and result or error msg.
    """

    # city_taiwan = ["taipei", "zhongli", "taoyuan", "kaohsiung", "taichung"]

    # if city.lower() == "new york":
    #     tz_identifier = "America/New_York"
    # elif city.lower() in city_taiwan:
    #     tz_identifier = "Asia/Taipei"
    # else:
    #     return {
    #         "status": "error",
    #         "error_message": (f"Sorry, I don't have timezone information for {city}."),
    #     }
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


# def get_current_time(city: str) -> dict:
#     """Returns the current time in a specified city.
#     Args:
#         city (str): The name of the city for which to retrieve the current time.
#     Returns:
#         dict: status and result or error msg.
#     """
#     # initialize Nominatim API
#     geolocator = Nominatim(user_agent="geoapiExercises")

#     # input as a geek
#     # lad = "Dhaka"
#     print("Location address:", city)

#     # getting Latitude and Longitude
#     location = geolocator.geocode(city)

#     print("Latitude and Longitude of the said address:")
#     print((location.latitude, location.longitude))

#     # pass the Latitude and Longitude
#     # into a timezone_at
#     # and it return timezone
#     obj = TimezoneFinder()

#     # returns 'Europe/Berlin'
#     result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
#     print("Time Zone : ", result)
#     try:
#         tz = ZoneInfo(result)
#         now = datetime.datetime.now(tz)
#         report = f'The current time is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
#         return {"status": "success", "report": report}
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": f"An error occurred while fetching the current time: {str(e)}",
#         }

root_agent = LlmAgent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description=("Agent to answer questions about the time and weather in a city."),
    instruction=(
        """
        You are a helpful agent who can answer user questions about the time and weather in a city.
        When you call a tool, you must use English for the city name.
        請用繁體中文回答問題。
        """
    ),
    tools=[
        get_weather,
        get_current_time,
        MCPToolset(
            # Use StdioServerParameters for local process communication
            connection_params=StdioServerParameters(
                command="/Users/tsaichengyu/.local/bin/uv",
                args=[
                    "--directory",
                    "/Users/tsaichengyu/Documents/Projects/ai/20251013-weather2mood",
                    "run",
                    "server.py",
                ]
            ),
            # tool_filter=[
            #     "read_file",
            #     "list_directory",
            # ],  # Optional: filter specific tools
            # For remote servers, you would use SseServerParams instead:
            # connection_params=SseServerParams(url="http://remote-server:port/path", headers={...})
        ),
    ],
)

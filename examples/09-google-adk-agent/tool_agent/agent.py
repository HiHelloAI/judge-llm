from datetime import datetime

import dotenv
from google.adk.agents import Agent
from google.adk.tools import google_search

dotenv.load_dotenv()


def get_current_time() -> dict:
    """Get the current time in the format YYYY-MM-DD HH:MM:SS"""
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def format_as_news_card(title: str, description: str, source: str = "", date: str = "") -> dict:
    """
    Format text as a nice news card with title, description, source, and date.

    Args:
        title: The headline or title of the news
        description: The main content or description
        source: The source of the news (optional)
        date: The date of the news (optional)

    Returns:
        A formatted news card as a dictionary with markdown formatting
    """
    card = []
    card.append("╔" + "═" * 78 + "╗")
    card.append("║" + " " * 78 + "║")

    # Title
    title_lines = [title[i:i + 76] for i in range(0, len(title), 76)]
    for line in title_lines:
        card.append(f"║ {line:<76} ║")

    card.append("║" + " " * 78 + "║")
    card.append("║" + "─" * 78 + "║")
    card.append("║" + " " * 78 + "║")

    # Description
    desc_lines = [description[i:i + 76] for i in range(0, len(description), 76)]
    for line in desc_lines:
        card.append(f"║ {line:<76} ║")

    card.append("║" + " " * 78 + "║")

    # Footer with source and date
    if source or date:
        card.append("║" + "─" * 78 + "║")
        footer = f"{source}"
        if source and date:
            footer += f" • {date}"
        elif date:
            footer = date
        card.append(f"║ {footer:<76} ║")

    card.append("╚" + "═" * 78 + "╝")

    formatted_card = "\n".join(card)

    return {
        "formatted_card": formatted_card,
        "plain_text": f"{title}\n\n{description}\n\nSource: {source} | Date: {date}"
    }


def get_weather(location: str, units: str = "fahrenheit") -> str:
    """Get the current weather for a location.

    Args:
        location: City name or location
        units: Temperature units (fahrenheit or celsius)

    Returns:
        Weather information string
    """
    # Simulated weather data
    weather_data = {
        "San Francisco": {"temp": 65, "condition": "partly cloudy"},
        "New York": {"temp": 72, "condition": "sunny"},
        "London": {"temp": 55, "condition": "rainy"},
        "Tokyo": {"temp": 68, "condition": "clear"},
    }

    data = weather_data.get(location, {"temp": 70, "condition": "unknown"})

    temp = data["temp"]
    if units.lower() == "celsius":
        temp = int((temp - 32) * 5 / 9)
        unit_str = "°C"
    else:
        unit_str = "°F"

    return f"{temp}{unit_str} and {data['condition']}"


def calculator(operation: str, a: float, b: float) -> float:
    """Perform a mathematical calculation.

    Args:
        operation: Operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number

    Returns:
        Result of the calculation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero",
    }

    op_func = operations.get(operation.lower())
    if not op_func:
        return f"Error: Unknown operation {operation}"

    return op_func(a, b)


root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash",
    description="Tool agent with custom formatting",
    instruction="""
You are a concise, helpful assistant that presents information clearly. Prioritize using the provided tools to gather or compute data, and use format_as_news_card to display news or multi-field results when appropriate.

Tools and usage:
- get_weather(location, units): Call when user asks about current weather. Return a short human-friendly sentence, e.g. "San Francisco: 65°F and partly cloudy."
- calculator(operation, a, b): Call for math operations (add, subtract, multiply, divide). If error (e.g. divide by zero), return the error string.
- google_search(query, num_results): Call only when factual or up-to-date web information is required. When using search results to report news or claims, include the source in the footer of the news card.
- get_current_time(): Call to provide the current timestamp.
- format_as_news_card(title, description, source, date): Use to render headlines, summaries, or any multi-field content as a formatted ASCII news card. Include source and date whenever available.

Behavior guidelines:
- Always prefer tool results over hallucination. If a tool is used, incorporate its output directly.
- Keep responses concise and user-focused.
- When presenting news, use format_as_news_card and include a one-line plain-text summary after the card.
- When answering short factual questions, a single sentence is sufficient.
""",
    tools=[google_search, get_current_time, get_weather, calculator, format_as_news_card]
)

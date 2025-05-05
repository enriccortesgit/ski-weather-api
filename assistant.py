import cohere
import os
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def generate_multi_resort_report(resort_data, date):
    """
    Generates a unified report for multiple resorts, recommending the best one.

    resort_data = [
        {"name": "Baqueira", "snowfall": 35, "temp": -4, "wind": 9},
        {"name": "Formigal", "snowfall": 20, "temp": -2, "wind": 12}
    ]
    """
    prompt = f"""
You are a snow analyst assistant for freeride skiers. Based on the data below, analyze the ski conditions for each resort. First, clearly recommend the best one for freeriding and explain why. Then, provide a short summary for the others. Focus on snowfall (more is better), temperature (below 0ºC is ideal), and wind (under 15 km/h is best).
Be concise, skip greetings, and do not repeat resort names unnecessarily. Output should be no more than 5 sentences.

Date: {date}
"""
    for resort in resort_data:
        prompt += f"\n- {resort['name']}: {resort['snowfall']} cm snow, {resort['temp']} ºC, {resort['wind']} km/h wind"

    prompt += "\n\nRecommendation:\n"

    response = co.generate(prompt=prompt, max_tokens=300, temperature=0.6)
    return response.generations[0].text.strip()

def generate_ski_report(resort, date, snowfall, temperature, wind):
    """
    Generates a single-resort freeride ski report using Cohere.
    """
    prompt = f"""
You are a snow conditions assistant. Based on the following ski data, write a short and helpful paragraph summarizing the current conditions and whether it's a good day to ski. Focus on freeride skiing. Be concise and avoid greetings.

Resort: {resort}
Date: {date}
Snowfall in last 72h: {snowfall} cm
Temperature: {temperature} °C
Wind speed: {wind} km/h

Recommendation:
"""
    response = co.generate(prompt=prompt, max_tokens=250, temperature=0.7)
    return response.generations[0].text.strip()

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to Python path to import shared module
sys.path.append(str(Path(__file__).parent.parent))

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types
from shared.retry_config import conservative_retry_options

print("✅ ADK components imported successfully.")

gemini_key = os.getenv('GEMINI_API_KEY')

# Configure the simple search agent
search_agent = Agent(
    name= "simple_search_agent",
    model= Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=conservative_retry_options
    ),
    description = "A simple agent that can answer general questions.",
    instruction = "You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools = [google_search],
)

print("🔍 Search agent created successfully.")

# Create a runner for the agent
runner = InMemoryRunner(agent=search_agent)

print("✅ Runner created.")

# Run a test query using async run_debug
async def test_query():
    response = await runner.run_debug("What's the weather in London?")
    print(f"\n📝 Test response: {response}\n")

asyncio.run(test_query())

# Start interactive debug mode
print("\n🚀 Starting interactive debug mode...")
print("You can now ask questions and the agent will use Google Search to help answer them.")
print("Type your questions and press Enter. Type 'exit' or 'quit' to stop.\n")

runner.run()

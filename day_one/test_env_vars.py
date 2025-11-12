import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
openai_key = os.getenv('OPENAI_API_KEY')
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY')

# Verify they are loaded with clear messaging
if openai_key:
    print("✓ OPENAI_API_KEY is set")
else:
    print("✗ OPENAI_API_KEY is NOT set")

if anthropic_key:
    print(f"✓ ANTHROPIC_API_KEY is set: {anthropic_key}")
else:
    print("✗ ANTHROPIC_API_KEY is NOT set")

if gemini_key:
    print("✓ GEMINI_API_KEY is set")
else:
    print("✗ GEMINI_API_KEY is NOT set")

import sys
import os

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from main_service.core.config import settings

print(f"LLM_PROVIDER: {settings.llm_provider}")
print(f"OPENAI_BASE_URL: {settings.openai_base_url}")
print(f"LLM_MODEL: {settings.llm_model}")
# Print first few chars of key to verify if it's set
key = settings.openai_api_key
masked_key = f"{key[:3]}...{key[-3:]}" if key and len(key) > 6 else "None"
print(f"OPENAI_API_KEY: {masked_key}")

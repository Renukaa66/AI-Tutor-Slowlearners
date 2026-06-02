"""
Available Gemini Models List - Diagnostic Script
Run: python check_models.py
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ API KEY NOT FOUND!")
    print("Check your .env file!")
    exit()

print("=" * 70)
print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-5:]}")
print("=" * 70)

# Configure
genai.configure(api_key=GEMINI_API_KEY)

# List all available models
print("\n📋 ALL AVAILABLE MODELS FOR YOU:\n")
print("-" * 70)

try:
    models = genai.list_models()
    
    for model in models:
        # Get supported methods
        methods = ", ".join(model.supported_generation_methods) if model.supported_generation_methods else "N/A"
        print(f"\n✅ Model Name: {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Methods: {methods}")
        print("-" * 70)
    
    print("\n\n🎯 MODELS THAT SUPPORT 'generateContent':\n")
    print("=" * 70)
    
    generate_content_models = []
    for model in models:
        if 'generateContent' in (model.supported_generation_methods or []):
            # Get the short name (without "models/" prefix)
            short_name = model.name.replace("models/", "")
            generate_content_models.append(short_name)
            print(f"✅ {short_name}")
    
    print("\n" + "=" * 70)
    print(f"\n📊 Total usable models: {len(generate_content_models)}")
    print(f"\n💡 RECOMMENDED MODEL TO USE (copy this!):\n")
    
    # Find best model
    if 'gemini-1.5-flash' in generate_content_models:
        print("   >>> 'gemini-1.5-flash' <<< (Best stable free model)")
    elif 'gemini-1.5-pro' in generate_content_models:
        print("   >>> 'gemini-1.5-pro' <<< (Most capable)")
    elif generate_content_models:
        print(f"   >>> '{generate_content_models[0]}' <<< (First available)")
    else:
        print("   ❌ NO MODELS AVAILABLE! Check your API key!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n🔧 Possible fixes:")
    print("1. Check if API key is correct in .env file")
    print("2. Go to https://aistudio.google.com/app/apikey")
    print("3. Create a NEW API key")
    print("4. Replace in .env file")

print("\n" + "=" * 70)

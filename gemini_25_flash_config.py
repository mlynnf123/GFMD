#!/usr/bin/env python3
"""
Gemini 2.5 Flash Configuration for GFMD AI Swarm
Updated to use the latest Gemini 2.5 Flash model
"""

import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

class Gemini25FlashConfig:
    """Configuration for Gemini 2.5 Flash model"""
    
    def __init__(self, api_key: str = "AIzaSyCALqubBZc4YLTtoyFG8d_NQDC23OzAXAU"):
        self.api_key = api_key
        self.model_name = "gemini-2.5-flash"
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        os.environ['GOOGLE_API_KEY'] = self.api_key
    
    def get_llm(self, temperature: float = 0.3, max_output_tokens: int = 2048):
        """Get configured Gemini 2.5 Flash LLM"""
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            convert_system_message_to_human=True
        )
    
    def get_direct_model(self):
        """Get direct Gemini model for advanced usage"""
        return genai.GenerativeModel(self.model_name)

def test_gemini_25_flash():
    """Test Gemini 2.5 Flash configuration"""
    print("🧪 Testing Gemini 2.5 Flash Configuration")
    print("=" * 60)
    
    config = Gemini25FlashConfig()
    llm = config.get_llm()
    
    # Test prompt
    test_prompt = "You are a healthcare sales AI. Briefly explain the benefits of noise reduction in hospital laboratories."
    
    try:
        response = llm.invoke(test_prompt)
        print("✅ Gemini 2.5 Flash is working!")
        print(f"📝 Response: {response.content[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_25_flash()
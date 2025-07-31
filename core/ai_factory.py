from core.ai_interface import AIAnalyzer
from core.ollama_client import OllamaClient
from core.perplexity_client import PerplexityClient

def create_ai_client(provider: str = "perplexity") -> AIAnalyzer:
    """Factory function to create AI client based on provider"""
    if provider == "ollama":
        return OllamaClient()
    elif provider == "perplexity":
        return PerplexityClient()
    else:
        raise ValueError(f"Unknown AI provider: {provider}")

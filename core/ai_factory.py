"""Factory for creating AI client instances."""

from core.ai_interface import AIAnalyzer
from core.ollama_client import OllamaClient
from core.perplexity_client import PerplexityClient

def create_ai_client(provider: str = "perplexity") -> AIAnalyzer:
    """Create AI client based on provider."""
    providers = {
        "ollama": OllamaClient,
        "perplexity": PerplexityClient
    }
    
    if provider not in providers:
        raise ValueError(f"Unknown AI provider: {provider}")
    
    return providers[provider]()

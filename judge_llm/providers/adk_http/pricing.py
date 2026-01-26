"""Pricing calculator for ADK models."""

from typing import Dict, Optional

# Pricing per million tokens (as of January 2025)
# Source: https://ai.google.dev/pricing
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # Gemini 2.0 models
    "gemini-2.0-flash": {
        "input": 0.075,  # $0.075 per 1M input tokens
        "output": 0.30,  # $0.30 per 1M output tokens
    },
    "gemini-2.0-flash-exp": {
        "input": 0.075,
        "output": 0.30,
    },
    "gemini-2.0-flash-thinking-exp": {
        "input": 0.075,
        "output": 0.30,
    },
    # Gemini 1.5 models
    "gemini-1.5-flash": {
        "input": 0.075,
        "output": 0.30,
    },
    "gemini-1.5-flash-8b": {
        "input": 0.0375,
        "output": 0.15,
    },
    "gemini-1.5-pro": {
        "input": 1.25,  # $1.25 per 1M input tokens
        "output": 5.00,  # $5.00 per 1M output tokens
    },
    # Gemini 2.0 Pro (if available)
    "gemini-2.0-pro": {
        "input": 1.25,
        "output": 5.00,
    },
    # Gemini 1.0 Pro (legacy)
    "gemini-1.0-pro": {
        "input": 0.50,
        "output": 1.50,
    },
    "gemini-pro": {
        "input": 0.50,
        "output": 1.50,
    },
    # Default fallback pricing
    "default": {
        "input": 0.10,
        "output": 0.40,
    },
}


class PricingCalculator:
    """Calculate costs based on model and token usage.

    Supports custom pricing overrides for enterprise or custom deployments.
    """

    def __init__(self, custom_pricing: Optional[Dict[str, Dict[str, float]]] = None):
        """Initialize pricing calculator.

        Args:
            custom_pricing: Optional custom pricing dict to override defaults.
                           Format: {"model_name": {"input": rate, "output": rate}}
        """
        self.pricing = MODEL_PRICING.copy()
        if custom_pricing:
            self.pricing.update(custom_pricing)

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calculate cost for given token usage.

        Args:
            model: Model name (e.g., "gemini-2.0-flash")
            prompt_tokens: Number of input/prompt tokens
            completion_tokens: Number of output/completion tokens

        Returns:
            Cost in USD
        """
        # Normalize model name (handle variations)
        model_lower = model.lower()

        # Try exact match first
        pricing = self.pricing.get(model_lower)

        # Try partial match for model families
        if pricing is None:
            for model_key in self.pricing:
                if model_key in model_lower or model_lower in model_key:
                    pricing = self.pricing[model_key]
                    break

        # Fall back to default
        if pricing is None:
            pricing = self.pricing["default"]

        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def get_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing rates for a model.

        Args:
            model: Model name

        Returns:
            Dict with "input" and "output" rates per 1M tokens
        """
        model_lower = model.lower()
        return self.pricing.get(model_lower, self.pricing["default"])

    def get_supported_models(self) -> list:
        """List all models with known pricing.

        Returns:
            List of model names (excluding "default")
        """
        return [m for m in self.pricing.keys() if m != "default"]

    def add_model_pricing(
        self, model: str, input_rate: float, output_rate: float
    ) -> None:
        """Add or update pricing for a model.

        Args:
            model: Model name
            input_rate: Cost per 1M input tokens in USD
            output_rate: Cost per 1M output tokens in USD
        """
        self.pricing[model.lower()] = {
            "input": input_rate,
            "output": output_rate,
        }

    def estimate_cost(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
    ) -> Dict[str, float]:
        """Estimate cost breakdown for a request.

        Args:
            model: Model name
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens

        Returns:
            Dict with input_cost, output_cost, and total_cost
        """
        pricing = self.get_pricing(model)

        input_cost = (estimated_input_tokens / 1_000_000) * pricing["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost,
            "input_rate_per_1m": pricing["input"],
            "output_rate_per_1m": pricing["output"],
        }

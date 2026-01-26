"""Embedding Similarity Evaluator

Uses embedding models to evaluate semantic similarity between expected and actual responses.
Supports multiple embedding providers (Gemini, OpenAI, sentence-transformers).
"""

import os
import math
from typing import Any, Dict, List, Optional, Tuple
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult, Invocation
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class EmbeddingSimilarityEvaluator(BaseEvaluator):
    """Evaluate semantic similarity using embedding models

    This evaluator computes embeddings for expected and actual responses,
    then calculates cosine similarity to measure semantic similarity.

    Configuration:
        provider (str): Embedding provider
            - "gemini": Google Gemini embeddings (default)
            - "openai": OpenAI embeddings
            - "sentence_transformers": Local sentence-transformers
        model (str): Embedding model name
            - Gemini: "text-embedding-004" (default)
            - OpenAI: "text-embedding-3-small"
            - sentence-transformers: "all-MiniLM-L6-v2"
        api_key (str): API key (from config or env var)
        similarity_threshold (float): Minimum similarity to pass (default: 0.8)
        compare_with_query (bool): Also compare response with query (default: False)
        chunk_long_text (bool): Chunk long texts for embedding (default: True)
        max_chunk_length (int): Max characters per chunk (default: 2000)
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger()
        self._embedder = None
        self._embedder_initialized = False

    def _get_embedder(self, provider: str, model: str, api_key: Optional[str]):
        """Lazy initialization of embedding client"""
        if self._embedder_initialized:
            return self._embedder

        if provider == "gemini":
            self._embedder = self._init_gemini_embedder(model, api_key)
        elif provider == "openai":
            self._embedder = self._init_openai_embedder(model, api_key)
        elif provider == "sentence_transformers":
            self._embedder = self._init_sentence_transformers(model)
        else:
            self.logger.warning(f"Unknown embedding provider: {provider}")
            self._embedder = None

        self._embedder_initialized = True
        return self._embedder

    def _init_gemini_embedder(self, model: str, api_key: Optional[str]):
        """Initialize Gemini embedding client"""
        try:
            from google import genai

            key = api_key or os.environ.get("GOOGLE_API_KEY")
            if not key:
                self.logger.warning(
                    "EmbeddingSimilarityEvaluator: No API key for Gemini. "
                    "Set 'api_key' in config or GOOGLE_API_KEY env var."
                )
                return None

            client = genai.Client(api_key=key)
            self.logger.debug(f"Initialized Gemini embedder with model: {model}")
            return {"type": "gemini", "client": client, "model": model}

        except ImportError:
            self.logger.warning(
                "EmbeddingSimilarityEvaluator: google-genai not installed. "
                "Install with: pip install google-genai"
            )
            return None

    def _init_openai_embedder(self, model: str, api_key: Optional[str]):
        """Initialize OpenAI embedding client"""
        try:
            from openai import OpenAI

            key = api_key or os.environ.get("OPENAI_API_KEY")
            if not key:
                self.logger.warning(
                    "EmbeddingSimilarityEvaluator: No API key for OpenAI. "
                    "Set 'api_key' in config or OPENAI_API_KEY env var."
                )
                return None

            client = OpenAI(api_key=key)
            self.logger.debug(f"Initialized OpenAI embedder with model: {model}")
            return {"type": "openai", "client": client, "model": model}

        except ImportError:
            self.logger.warning(
                "EmbeddingSimilarityEvaluator: openai package not installed. "
                "Install with: pip install openai"
            )
            return None

    def _init_sentence_transformers(self, model: str):
        """Initialize sentence-transformers embedder"""
        try:
            from sentence_transformers import SentenceTransformer

            st_model = SentenceTransformer(model)
            self.logger.debug(f"Initialized sentence-transformers with model: {model}")
            return {"type": "sentence_transformers", "model": st_model}

        except ImportError:
            self.logger.warning(
                "EmbeddingSimilarityEvaluator: sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            return None

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
        eval_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluatorResult:
        """Evaluate semantic similarity using embeddings

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result
            eval_config: Per-test-case evaluator configuration

        Returns:
            EvaluatorResult with evaluation results
        """
        config = self.get_config(eval_config)
        provider = config.get("provider", "gemini")
        model = config.get("model", self._get_default_model(provider))
        api_key = config.get("api_key")
        similarity_threshold = config.get("similarity_threshold", 0.8)
        compare_with_query = config.get("compare_with_query", False)
        chunk_long_text = config.get("chunk_long_text", True)
        max_chunk_length = config.get("max_chunk_length", 2000)

        self.logger.debug(
            f"EmbeddingSimilarityEvaluator evaluating case: {eval_case.eval_id} "
            f"(provider={provider}, model={model})"
        )

        # Get embedder
        embedder = self._get_embedder(provider, model, api_key)
        if embedder is None:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": f"Embedding provider '{provider}' not available"},
                error=f"Embedding provider not available",
            )

        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
                error="Provider execution failed",
            )

        expected_conv = eval_case.conversation
        actual_conv = provider_result.conversation_history

        if len(expected_conv) != len(actual_conv):
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=True,
                score=0.0,
                threshold=similarity_threshold,
                passed=False,
                details={
                    "mismatch": "conversation_length",
                    "expected_length": len(expected_conv),
                    "actual_length": len(actual_conv),
                },
            )

        # Evaluate each invocation
        invocation_results = []
        total_score = 0.0

        for i, (expected_inv, actual_inv) in enumerate(zip(expected_conv, actual_conv)):
            # Extract texts
            user_query = self._extract_text(expected_inv.user_content.parts)
            expected_response = self._extract_text(expected_inv.final_response.parts)
            actual_response = self._extract_text(actual_inv.final_response.parts)

            # Handle empty responses
            if not expected_response and not actual_response:
                similarity = 1.0
                inv_result = {
                    "invocation": i,
                    "similarity": similarity,
                    "note": "Both responses empty",
                }
            elif not expected_response or not actual_response:
                similarity = 0.0
                inv_result = {
                    "invocation": i,
                    "similarity": similarity,
                    "note": "One response empty",
                }
            else:
                # Get embeddings
                try:
                    expected_emb = self._get_embedding(
                        embedder, expected_response, chunk_long_text, max_chunk_length
                    )
                    actual_emb = self._get_embedding(
                        embedder, actual_response, chunk_long_text, max_chunk_length
                    )

                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(expected_emb, actual_emb)

                    inv_result = {
                        "invocation": i,
                        "similarity": similarity,
                        "expected_preview": expected_response[:100],
                        "actual_preview": actual_response[:100],
                    }

                    # Optionally compare with query
                    if compare_with_query and user_query:
                        query_emb = self._get_embedding(
                            embedder, user_query, chunk_long_text, max_chunk_length
                        )
                        query_similarity = self._cosine_similarity(query_emb, actual_emb)
                        inv_result["query_response_similarity"] = query_similarity

                except Exception as e:
                    self.logger.error(f"Embedding error for invocation {i}: {e}")
                    similarity = 0.0
                    inv_result = {
                        "invocation": i,
                        "similarity": 0.0,
                        "error": str(e),
                    }

            total_score += similarity
            invocation_results.append(inv_result)

        avg_score = total_score / len(expected_conv) if expected_conv else 0.0
        passed = avg_score >= similarity_threshold

        details = {
            "provider": provider,
            "model": model,
            "similarity_threshold": similarity_threshold,
            "average_similarity": avg_score,
            "invocation_results": invocation_results,
            "num_invocations": len(expected_conv),
        }

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=avg_score,
            threshold=similarity_threshold,
            passed=passed,
            details=details,
        )

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "gemini": "text-embedding-004",
            "openai": "text-embedding-3-small",
            "sentence_transformers": "all-MiniLM-L6-v2",
        }
        return defaults.get(provider, "text-embedding-004")

    def _extract_text(self, parts: list) -> str:
        """Extract text from parts"""
        if not parts:
            return ""
        texts = [part.text.strip() for part in parts if part.text and part.text.strip()]
        return " ".join(texts)

    def _get_embedding(
        self,
        embedder: Dict[str, Any],
        text: str,
        chunk: bool,
        max_chunk_length: int,
    ) -> List[float]:
        """Get embedding for text

        Args:
            embedder: Embedder configuration
            text: Text to embed
            chunk: Whether to chunk long text
            max_chunk_length: Max chunk length

        Returns:
            Embedding vector as list of floats
        """
        # Chunk text if needed
        if chunk and len(text) > max_chunk_length:
            chunks = self._chunk_text(text, max_chunk_length)
            # Get embeddings for all chunks and average
            embeddings = [self._embed_single(embedder, c) for c in chunks]
            return self._average_embeddings(embeddings)
        else:
            return self._embed_single(embedder, text)

    def _embed_single(self, embedder: Dict[str, Any], text: str) -> List[float]:
        """Get embedding for a single text"""
        emb_type = embedder["type"]

        if emb_type == "gemini":
            client = embedder["client"]
            model = embedder["model"]
            result = client.models.embed_content(
                model=model,
                content=text,
            )
            return result.embedding

        elif emb_type == "openai":
            client = embedder["client"]
            model = embedder["model"]
            result = client.embeddings.create(
                model=model,
                input=text,
            )
            return result.data[0].embedding

        elif emb_type == "sentence_transformers":
            model = embedder["model"]
            embedding = model.encode(text)
            return embedding.tolist()

        else:
            raise ValueError(f"Unknown embedder type: {emb_type}")

    def _chunk_text(self, text: str, max_length: int) -> List[str]:
        """Chunk text into smaller pieces

        Args:
            text: Text to chunk
            max_length: Max chunk length

        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_len = len(word) + 1  # +1 for space
            if current_length + word_len > max_length and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_len
            else:
                current_chunk.append(word)
                current_length += word_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks if chunks else [text]

    def _average_embeddings(self, embeddings: List[List[float]]) -> List[float]:
        """Average multiple embeddings

        Args:
            embeddings: List of embedding vectors

        Returns:
            Averaged embedding vector
        """
        if not embeddings:
            return []
        if len(embeddings) == 1:
            return embeddings[0]

        dim = len(embeddings[0])
        averaged = [0.0] * dim

        for emb in embeddings:
            for i, val in enumerate(emb):
                averaged[i] += val

        n = len(embeddings)
        return [v / n for v in averaged]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0.0 to 1.0)
        """
        if not vec1 or not vec2:
            return 0.0

        if len(vec1) != len(vec2):
            self.logger.warning(
                f"Embedding dimension mismatch: {len(vec1)} vs {len(vec2)}"
            )
            return 0.0

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        similarity = dot_product / (mag1 * mag2)

        # Clamp to [0, 1] range (numerical errors can cause slight overflow)
        return max(0.0, min(1.0, similarity))

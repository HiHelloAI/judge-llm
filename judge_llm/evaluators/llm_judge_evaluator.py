"""LLM Judge Evaluator

Uses an LLM (Gemini, OpenAI, etc.) as a judge to evaluate:
- Response relevance to the user query
- Hallucination detection
- Response quality (helpfulness, accuracy, coherence)
- Factual grounding
"""

import json
import os
from typing import Any, Dict, List, Optional
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult, Invocation
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger
import dotenv

dotenv.load_dotenv()

# Default evaluation prompts
DEFAULT_PROMPTS = {
    "relevance": """You are an expert evaluator. Assess how relevant the assistant's response is to the user's query.

User Query: {user_query}

Assistant Response: {response}

Expected Response (for reference): {expected_response}

Rate the relevance on a scale of 1-5:
1 = Completely irrelevant, doesn't address the query at all
2 = Mostly irrelevant, only tangentially related
3 = Somewhat relevant, addresses part of the query
4 = Mostly relevant, addresses the main query with minor gaps
5 = Highly relevant, fully addresses the user's query

Respond with ONLY a JSON object in this exact format:
{{"score": <1-5>, "reasoning": "<brief explanation>"}}""",

    "hallucination": """You are an expert evaluator detecting hallucinations in AI responses.

User Query: {user_query}

Assistant Response: {response}

Expected Response (ground truth reference): {expected_response}

Evaluate whether the response contains hallucinations (fabricated, false, or unverifiable information).

Rate the response on a scale of 1-5:
1 = Severe hallucination, contains multiple false claims or fabricated information
2 = Significant hallucination, contains some false or unverifiable claims
3 = Minor hallucination, mostly accurate with small inaccuracies
4 = Minimal hallucination, accurate with very minor imprecisions
5 = No hallucination, all information is accurate and verifiable

Respond with ONLY a JSON object in this exact format:
{{"score": <1-5>, "reasoning": "<brief explanation>", "hallucinated_claims": ["<list of any hallucinated claims>"]}}""",

    "quality": """You are an expert evaluator assessing response quality.

User Query: {user_query}

Assistant Response: {response}

Expected Response (reference): {expected_response}

Evaluate the overall quality of the response considering:
- Helpfulness: Does it help the user accomplish their goal?
- Clarity: Is it clear and easy to understand?
- Completeness: Does it provide sufficient information compared to the expected response?
- Coherence: Is it logically structured and coherent?
- Tone: Is the tone appropriate for the context?
- Match: How well does it align with the expected response in content and intent?

Rate the overall quality on a scale of 1-5:
1 = Very poor quality, unhelpful or completely misaligned with expected response
2 = Poor quality, significant gaps compared to expected response
3 = Average quality, partially matches expected response
4 = Good quality, mostly matches expected response with minor gaps
5 = Excellent quality, fully aligned with expected response

Respond with ONLY a JSON object in this exact format:
{{"score": <1-5>, "reasoning": "<brief explanation>", "breakdown": {{"helpfulness": <1-5>, "clarity": <1-5>, "completeness": <1-5>, "coherence": <1-5>, "tone": <1-5>, "match": <1-5>}}}}""",

    "factuality": """You are an expert evaluator assessing factual accuracy.

User Query: {user_query}

Assistant Response: {response}

Expected Response (reference): {expected_response}

Evaluate the factual accuracy of the response. Check if the facts, claims, and information provided are accurate.

Rate factuality on a scale of 1-5:
1 = Mostly inaccurate, contains significant factual errors
2 = Somewhat inaccurate, contains several factual errors
3 = Partially accurate, mix of correct and incorrect facts
4 = Mostly accurate, minor factual imprecisions
5 = Highly accurate, all facts are correct

Respond with ONLY a JSON object in this exact format:
{{"score": <1-5>, "reasoning": "<brief explanation>", "factual_errors": ["<list of any factual errors>"]}}""",

    "comprehensive": """You are an expert evaluator performing a comprehensive assessment of an AI assistant's response.

User Query: {user_query}

Assistant Response: {response}

Expected Response (reference): {expected_response}

Evaluate the response across multiple dimensions:

1. **Relevance** (1-5): How well does the response address the user's query?
2. **Accuracy** (1-5): Is the information factually correct?
3. **Completeness** (1-5): Does it cover all important aspects?
4. **Clarity** (1-5): Is it clear and easy to understand?
5. **Helpfulness** (1-5): Does it help the user accomplish their goal?

Respond with ONLY a JSON object in this exact format:
{{"overall_score": <1-5>, "dimensions": {{"relevance": <1-5>, "accuracy": <1-5>, "completeness": <1-5>, "clarity": <1-5>, "helpfulness": <1-5|}}, "reasoning": "<brief overall assessment>", "strengths": ["<list of strengths>"], "improvements": ["<list of suggested improvements>"]}}"""
}


class LLMJudgeEvaluator(BaseEvaluator):
    """Use an LLM as a judge to evaluate response quality

    This evaluator sends the user query, actual response, and expected response
    to an LLM judge that assesses quality metrics like relevance, hallucination,
    and overall quality.

    Configuration:
        model (str): Model to use for judging (default: gemini-2.0-flash)
        api_key (str): API key (default: from GOOGLE_API_KEY env var)
        evaluation_type (str): Type of evaluation to perform
            - "relevance": Assess query-response relevance
            - "hallucination": Detect hallucinations
            - "quality": Assess overall response quality
            - "factuality": Assess factual accuracy
            - "comprehensive": All dimensions combined
        custom_prompt (str): Custom evaluation prompt (overrides evaluation_type)
        min_score (float): Minimum score to pass (default: 3.0 for 1-5 scale)
        temperature (float): LLM temperature (default: 0.0 for consistency)
        max_retries (int): Max retries on parse failure (default: 2)
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger()
        self._client = None
        self._client_initialized = False

    def _get_client(self):
        """Lazy initialization of the Gemini client"""
        if self._client_initialized:
            return self._client

        try:
            from google import genai
            api_key = self.config.get("api_key") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                self.logger.warning(
                    "LLMJudgeEvaluator: No API key found. "
                    "Set 'api_key' in config or GOOGLE_API_KEY environment variable."
                )
                self._client = None
            else:
                self._client = genai.Client(api_key=api_key)
                self.logger.debug("LLMJudgeEvaluator: Gemini client initialized")
        except ImportError:
            self.logger.warning(
                "LLMJudgeEvaluator: google-genai package not installed. "
                "Install with: pip install google-genai"
            )
            self._client = None

        self._client_initialized = True
        return self._client

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
        eval_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluatorResult:
        """Evaluate response using LLM judge

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result
            eval_config: Per-test-case evaluator configuration

        Returns:
            EvaluatorResult with evaluation results
        """
        config = self.get_config(eval_config)
        model = config.get("model", "gemini-2.0-flash")
        evaluation_type = config.get("evaluation_type", "comprehensive")
        custom_prompt = config.get("custom_prompt")
        min_score = config.get("min_score", 3.0)
        temperature = config.get("temperature", 0.0)
        max_retries = config.get("max_retries", 2)

        self.logger.debug(
            f"LLMJudgeEvaluator evaluating case: {eval_case.eval_id} "
            f"(type={evaluation_type}, model={model})"
        )

        # Check if client is available
        client = self._get_client()
        if client is None:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "LLM client not available (missing API key or package)"},
                error="LLM client not available",
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
                threshold=min_score,
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
        all_passed = True

        for i, (expected_inv, actual_inv) in enumerate(zip(expected_conv, actual_conv)):
            # Extract texts
            user_query = self._extract_text(expected_inv.user_content.parts)
            expected_response = self._extract_text(expected_inv.final_response.parts)
            actual_response = self._extract_text(actual_inv.final_response.parts)

            # Get evaluation prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = DEFAULT_PROMPTS.get(evaluation_type, DEFAULT_PROMPTS["comprehensive"])

            # Format prompt with data
            formatted_prompt = prompt.format(
                user_query=user_query,
                response=actual_response,
                expected_response=expected_response,
            )

            # Call LLM judge
            result = self._call_llm_judge(
                client, model, formatted_prompt, temperature, max_retries
            )

            if result["success"]:
                score = result["score"]
                total_score += score
                inv_passed = score >= min_score

                if not inv_passed:
                    all_passed = False

                invocation_results.append({
                    "invocation": i,
                    "score": score,
                    "passed": inv_passed,
                    "evaluation_type": evaluation_type,
                    "llm_response": result["response"],
                    "user_query_preview": user_query[:100],
                    "actual_response_preview": actual_response[:100],
                })
            else:
                all_passed = False
                invocation_results.append({
                    "invocation": i,
                    "score": 0.0,
                    "passed": False,
                    "error": result["error"],
                    "user_query_preview": user_query[:100],
                })

        avg_score = total_score / len(expected_conv) if expected_conv else 0.0
        # Normalize score to 0-1 range (from 1-5 scale)
        normalized_score = (avg_score - 1) / 4 if avg_score > 0 else 0.0
        normalized_threshold = (min_score - 1) / 4

        passed = avg_score >= min_score

        details = {
            "evaluation_type": evaluation_type,
            "model": model,
            "min_score": min_score,
            "average_score": avg_score,
            "normalized_score": normalized_score,
            "invocation_results": invocation_results,
            "num_invocations": len(expected_conv),
            "all_invocations_passed": all_passed,
        }

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=normalized_score,
            threshold=normalized_threshold,
            passed=passed,
            details=details,
        )

    def _extract_text(self, parts: list) -> str:
        """Extract text from parts"""
        if not parts:
            return ""
        texts = [part.text.strip() for part in parts if part.text and part.text.strip()]
        return " ".join(texts)

    def _call_llm_judge(
        self,
        client,
        model: str,
        prompt: str,
        temperature: float,
        max_retries: int,
    ) -> Dict[str, Any]:
        """Call the LLM judge and parse response

        Args:
            client: Gemini client
            model: Model name
            prompt: Evaluation prompt
            temperature: Temperature setting
            max_retries: Max retries on parse failure

        Returns:
            Dictionary with success, score, and response/error
        """
        from google.genai import types

        for attempt in range(max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=1024,
                    ),
                )

                response_text = response.text.strip()

                # Parse JSON response
                parsed = self._parse_json_response(response_text)

                if parsed is not None:
                    # Extract score from various possible keys
                    score = parsed.get("score") or parsed.get("overall_score") or 0
                    return {
                        "success": True,
                        "score": float(score),
                        "response": parsed,
                    }
                else:
                    if attempt < max_retries:
                        self.logger.debug(
                            f"LLMJudgeEvaluator: Failed to parse JSON (attempt {attempt + 1}), retrying"
                        )
                        continue
                    return {
                        "success": False,
                        "error": f"Failed to parse JSON response: {response_text[:200]}",
                    }

            except Exception as e:
                if attempt < max_retries:
                    self.logger.debug(
                        f"LLMJudgeEvaluator: API call failed (attempt {attempt + 1}): {e}"
                    )
                    continue
                return {
                    "success": False,
                    "error": str(e),
                }

        return {"success": False, "error": "Max retries exceeded"}

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response

        Handles various response formats including:
        - Pure JSON
        - JSON in markdown code blocks
        - JSON with surrounding text

        Args:
            text: LLM response text

        Returns:
            Parsed JSON dict or None
        """
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code block
        import re
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # Try to find JSON object in text
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(brace_pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        return None

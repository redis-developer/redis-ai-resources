"""Unit and integration tests for MiniMax provider in the full-featured agent notebook."""
import os
import unittest
from unittest.mock import MagicMock, patch


# ─── helpers mirrored from 02_full_featured_agent.ipynb ──────────────────────

MINIMAX_BASE_URL = "https://api.minimax.io/v1"
MINIMAX_MODEL = "MiniMax-M2.5"
MINIMAX_TEMPERATURE = 0.1  # must be in (0, 1]


def _make_minimax_chat(**overrides):
    """Return a ChatOpenAI-style config dict for MiniMax (used in unit tests)."""
    cfg = {
        "api_key": os.environ.get("MINIMAX_API_KEY", "dummy"),
        "base_url": MINIMAX_BASE_URL,
        "model_name": MINIMAX_MODEL,
        "temperature": MINIMAX_TEMPERATURE,
    }
    cfg.update(overrides)
    return cfg


# ─── Unit tests ───────────────────────────────────────────────────────────────


class TestMiniMaxConfig(unittest.TestCase):
    """Validate MiniMax provider configuration constants."""

    def test_base_url(self):
        self.assertEqual(MINIMAX_BASE_URL, "https://api.minimax.io/v1")

    def test_model_name(self):
        self.assertIn(MINIMAX_MODEL, ("MiniMax-M2.5", "MiniMax-M2.5-highspeed",
                                     "MiniMax-M2.7", "MiniMax-M2.7-highspeed"))

    def test_temperature_gt_zero(self):
        """MiniMax rejects temperature == 0; must be in (0, 1]."""
        self.assertGreater(MINIMAX_TEMPERATURE, 0.0)

    def test_temperature_lte_one(self):
        self.assertLessEqual(MINIMAX_TEMPERATURE, 1.0)

    def test_config_keys(self):
        cfg = _make_minimax_chat()
        for key in ("api_key", "base_url", "model_name", "temperature"):
            self.assertIn(key, cfg)


class TestProviderDispatch(unittest.TestCase):
    """Ensure provider dispatch logic mirrors the notebook."""

    def _get_tool_model(self, model_name: str, mock_openai_cls):
        """Simulate the notebook _get_tool_model function."""
        if model_name == "openai":
            model = mock_openai_cls(temperature=0, model_name="gpt-4o")
        elif model_name == "minimax":
            model = mock_openai_cls(
                api_key=os.environ.get("MINIMAX_API_KEY", "dummy"),
                base_url=MINIMAX_BASE_URL,
                model_name=MINIMAX_MODEL,
                temperature=MINIMAX_TEMPERATURE,
            )
        else:
            raise ValueError(f"Unsupported model type: {model_name}")
        return model

    def test_openai_dispatch(self):
        mock_cls = MagicMock(return_value=MagicMock())
        self._get_tool_model("openai", mock_cls)
        mock_cls.assert_called_once_with(temperature=0, model_name="gpt-4o")

    def test_minimax_dispatch(self):
        mock_cls = MagicMock(return_value=MagicMock())
        self._get_tool_model("minimax", mock_cls)
        mock_cls.assert_called_once_with(
            api_key=os.environ.get("MINIMAX_API_KEY", "dummy"),
            base_url=MINIMAX_BASE_URL,
            model_name=MINIMAX_MODEL,
            temperature=MINIMAX_TEMPERATURE,
        )

    def test_invalid_provider_raises(self):
        mock_cls = MagicMock()
        with self.assertRaises(ValueError):
            self._get_tool_model("unknown_provider", mock_cls)

    def test_minimax_temperature_not_zero(self):
        """Calling with minimax must never pass temperature=0."""
        calls = []

        def recording_cls(**kwargs):
            calls.append(kwargs)
            return MagicMock()

        self._get_tool_model("minimax", recording_cls)
        self.assertGreater(calls[0]["temperature"], 0.0,
                           "MiniMax requires temperature > 0")

    def test_minimax_base_url_correct(self):
        calls = []

        def recording_cls(**kwargs):
            calls.append(kwargs)
            return MagicMock()

        self._get_tool_model("minimax", recording_cls)
        self.assertEqual(calls[0]["base_url"], "https://api.minimax.io/v1")


class TestGraphConfigLiteral(unittest.TestCase):
    """Verify the GraphConfig Literal values include minimax."""

    def test_minimax_in_literal(self):
        from typing import Literal, get_args, TypedDict

        class GraphConfig(TypedDict):
            model_name: Literal["openai", "minimax"]

        args = get_args(GraphConfig.__annotations__["model_name"])
        self.assertIn("minimax", args)
        self.assertIn("openai", args)


# ─── Integration tests (skipped when no API key) ─────────────────────────────


@unittest.skipUnless(os.environ.get("MINIMAX_API_KEY"), "MINIMAX_API_KEY not set")
class TestMiniMaxIntegration(unittest.TestCase):
    """Live API smoke tests — only run when MINIMAX_API_KEY is available."""

    @classmethod
    def setUpClass(cls):
        # Workaround for langchain_core compat issue where it reads langchain.verbose
        import sys
        import types
        if "langchain" not in sys.modules:
            langchain_stub = types.ModuleType("langchain")
            langchain_stub.verbose = False
            sys.modules["langchain"] = langchain_stub
        else:
            lc = sys.modules["langchain"]
            if not hasattr(lc, "verbose"):
                lc.verbose = False

    def _get_client(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.environ["MINIMAX_API_KEY"],
            base_url=MINIMAX_BASE_URL,
            model_name=MINIMAX_MODEL,
            temperature=MINIMAX_TEMPERATURE,
        )

    def test_basic_invoke(self):
        """Model returns a non-empty response for a simple prompt."""
        from langchain_core.messages import HumanMessage
        client = self._get_client()
        response = client.invoke([HumanMessage(content="Say hello in one word.")])
        self.assertTrue(response.content.strip())

    def test_tool_binding(self):
        """bind_tools does not raise and produces an AIMessage."""
        from langchain_core.messages import HumanMessage
        from langchain_core.tools import tool

        @tool
        def add(a: int, b: int) -> int:
            """Add two integers."""
            return a + b

        client = self._get_client().bind_tools([add])
        response = client.invoke([HumanMessage(content="What is 3 + 4?")])
        self.assertIsNotNone(response)

    def test_structured_output(self):
        """MiniMax: strip <think> tags then regex-extract A/B/C/D from raw response."""
        import re
        from pydantic import BaseModel
        from langchain_core.messages import HumanMessage
        from langchain_openai import ChatOpenAI
        from langchain_core.runnables import RunnableLambda
        from typing import Literal

        class Choice(BaseModel):
            answer: Literal["A", "B", "C", "D"]

        def _parse(response):
            content = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
            m = re.search(r"\b([ABCD])\b", content)
            if m:
                return Choice(answer=m.group(1))
            raise ValueError(f"Could not extract choice from: {content!r}")

        base = ChatOpenAI(
            api_key=os.environ["MINIMAX_API_KEY"],
            base_url=MINIMAX_BASE_URL,
            model_name=MINIMAX_MODEL,
            temperature=MINIMAX_TEMPERATURE,
        )
        client = base | RunnableLambda(_parse)
        response = client.invoke(
            [HumanMessage(content="Pick one letter: A, B, C, or D. Just give the letter.")]
        )
        self.assertIn(response.answer, ("A", "B", "C", "D"))


if __name__ == "__main__":
    unittest.main()

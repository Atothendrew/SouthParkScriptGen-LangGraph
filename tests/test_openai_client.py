import os
import unittest
import tempfile


class OpenAIClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from langchain_openai import ChatOpenAI  # type: ignore
        except Exception as e:
            raise unittest.SkipTest(f"langchain_openai not available: {e}")

        # Prefer LM Studio OpenAI-compatible server
        base_url = os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")
        model_name = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")

        try:
            cls.llm = ChatOpenAI(model=model_name, base_url=base_url, api_key="not-needed", temperature=0.2)
            # Probe connectivity
            from langchain_core.messages import HumanMessage
            _ = cls.llm.invoke([HumanMessage(content="Respond 'ok'.")])
        except Exception as e:
            raise unittest.SkipTest(f"OpenAI-compatible server not reachable at {base_url}: {e}")

        cls.model_name = model_name

        # Redirect logs during tests
        try:
            from spgen.workflow.logging_utils import set_tool_log_dir
            tmpdir = tempfile.mkdtemp(prefix="llm_logs_")
            set_tool_log_dir(tmpdir)
        except Exception:
            pass

    def test_respond_returns_content(self):
        from spgen.workflow.providers import openai_client as oa

        content, model = oa.respond("Say the word hello.", self.llm, self.model_name)
        self.assertIsInstance(content, str)
        self.assertGreater(len(content.strip()), 0, "respond() returned empty content")
        self.assertIn("hello", content.lower(), "respond() did not include 'hello'")
        self.assertIsInstance(model, str)
        self.assertGreater(len(model.strip()), 0)

    def test_act_with_simple_tool(self):
        from spgen.workflow.providers import openai_client as oa
        from langchain_core.tools import tool

        @tool
        def add(a: int, b: int) -> int:
            """Given two integers a and b, return their sum as an integer."""
            return int(a) + int(b)

        prompt = (
            "Use the add tool to compute 2 + 3. Respond with only the numeric result and nothing else."
        )
        content, model = oa.act(prompt, self.llm, self.model_name, [add])
        self.assertIsInstance(content, str)
        text = content.strip()
        self.assertGreater(len(text), 0, "act() returned empty content")
        import re
        digits = re.findall(r"-?\d+", text)
        self.assertTrue("5" in text or (digits and int(digits[0]) == 5), f"act() did not return correct sum in content: {text}")
        self.assertIsInstance(model, str)
        self.assertGreater(len(model.strip()), 0)

    def test_act_tools_steps_output(self):
        from spgen.workflow.providers import openai_client as oa
        from langchain_core.tools import tool

        @tool
        def add(a: int, b: int) -> int:
            """Given two integers a and b, return their sum as an integer."""
            return int(a) + int(b)

        @tool
        def multiply(a: int, b: int) -> int:
            """Given two integers a and b, return their product as an integer."""
            return int(a) * int(b)

        prompt = (
            "Use the provided tools to compute the area of a rectangle with width 12 and height 9. "
            "Show your work as numbered steps (e.g., '1. ...', '2. ...'), then on the last line write "
            "'Final Answer: <number>'. Use at least two steps and prefer the tools over mental math."
        )

        content, model = oa.act(prompt, self.llm, self.model_name, [add, multiply])
        self.assertIsInstance(content, str)
        text = content.strip()
        self.assertGreater(len(text), 0, "act() returned empty content for steps problem")
        self.assertIn("1.", text, "Output did not include a first numbered step")
        self.assertIn("2.", text, "Output did not include a second numbered step")
        self.assertIn("Final Answer", text, "Missing 'Final Answer' line")
        import re
        nums = [int(n) for n in re.findall(r"-?\d+", text)]
        self.assertIn(108, nums, f"Expected 108 in output, got: {text}")


if __name__ == "__main__":
    unittest.main()



import os
import unittest
import tempfile


class LMStudioClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import lmstudio as lms  # type: ignore
        except Exception as e:
            raise unittest.SkipTest(f"LM Studio SDK not available: {e}")

        try:
            models = lms.list_loaded_models()
        except Exception as e:
            raise unittest.SkipTest(f"LM Studio server not reachable: {e}")

        if not models:
            raise unittest.SkipTest("No models loaded in LM Studio. Please load a model and re-run tests.")

        cls.model_name = models[0].identifier

        # Redirect logs during tests
        try:
            from spgen.workflow.logging_utils import set_tool_log_dir
            tmpdir = tempfile.mkdtemp(prefix="llm_logs_")
            set_tool_log_dir(tmpdir)
        except Exception:
            pass

    def test_respond_returns_content(self):
        from spgen.workflow.providers import lmstudio_client as lm

        # Use small thinking budget for seed-oss models
        thinking_budget = 512 if "seed-oss" in self.model_name.lower() else None
        
        content, model = lm.respond("Say the word hello.", self.model_name, 0.2, thinking_budget)
        self.assertIsInstance(content, str)
        self.assertGreater(len(content.strip()), 0, "respond() returned empty content")
        self.assertIn("hello", content.lower(), "respond() did not include 'hello'")
        print(f"RESPOND content: {content}")
        self.assertIsInstance(model, str)
        self.assertGreater(len(model.strip()), 0)

    def test_act_multi_tool_math_pipeline(self):
        from spgen.workflow.providers import lmstudio_client as lm

        def add(a: float, b: float) -> float:
            """Return a + b."""
            return float(a) + float(b)

        def subtract(a: float, b: float) -> float:
            """Return a - b."""
            return float(a) - float(b)

        def multiply(a: float, b: float) -> float:
            """Return a * b."""
            return float(a) * float(b)

        def divide(a: float, b: float) -> float:
            """Return a / b (floating point)."""
            return float(a) / float(b)

        def power(a: float, b: float) -> float:
            """Return a raised to the power b (floating point)."""
            return float(a) ** float(b)

        # Expression: ((2+3)*(10-4)) / (2^2) = (5*6)/4 = 7.5
        prompt = (
            "Using the available tools (add, subtract, multiply, divide, power), compute the value of "
            "((2 + 3) * (10 - 4)) / (2 ^ 2). Show your work as numbered steps and end with 'Final Answer: <number>'."
        )

        # Use small thinking budget for seed-oss models
        thinking_budget = 512 if "seed-oss" in self.model_name.lower() else None
        
        content, _ = lm.act(prompt, self.model_name, 0.1, [add, subtract, multiply, divide, power], thinking_budget)
        text = (content or "").strip()
        self.assertTrue(text)
        # Accept either "1." or "Step 1" style numbering
        self.assertTrue(("1." in text) or ("Step 1" in text), "Missing first step numbering")
        self.assertTrue(("2." in text) or ("Step 2" in text), "Missing second step numbering")
        self.assertIn("final answer".lower(), text.lower())
        import re
        nums = re.findall(r"-?\d+(?:\.\d+)?", text)
        self.assertTrue(any(abs(float(n) - 7.5) < 1e-6 for n in nums), f"Expected 7.5 in output, got: {text}")

    def test_act_mixed_string_and_math_tools(self):
        from spgen.workflow.providers import lmstudio_client as lm

        def strlen(s: str) -> int:
            """Return the number of characters in s (length)."""
            return len(str(s))

        def word_count(s: str) -> int:
            """Return the number of words in s (split on whitespace)."""
            return len(str(s).split())

        def multiply(a: int, b: int) -> int:
            """Return a * b as integer."""
            return int(a) * int(b)

        sentence = "South Park writers room test"
        prompt = (
            f"You are given a sentence: '{sentence}'. First compute its character length using tools, then its word count, "
            "then multiply these two values using the provided tool. Show steps and end with 'Final Answer: <number>'."
        )

        # Use small thinking budget for seed-oss models
        thinking_budget = 512 if "seed-oss" in self.model_name.lower() else None
        
        content, _ = lm.act(prompt, self.model_name, 0.1, [strlen, word_count, multiply], thinking_budget)
        text = (content or "").strip()
        self.assertTrue(text)
        self.assertTrue(("1." in text) or ("Step 1" in text), "Missing first step numbering")
        self.assertTrue(("2." in text) or ("Step 2" in text), "Missing second step numbering")
        self.assertIn("final answer".lower(), text.lower())
        # Compute expected deterministically
        expected = len(sentence) * len(sentence.split())
        import re
        nums = [int(n) for n in re.findall(r"-?\d+", text)]
        self.assertIn(expected, nums, f"Expected {expected} in output, got: {text}")

    def test_act_with_simple_tool(self):
        from spgen.workflow.providers import lmstudio_client as lm

        def add(a: int, b: int) -> int:
            """Given two integers a and b, return their sum as an integer."""
            return int(a) + int(b)

        # Prompt requires numeric-only output for deterministic checking
        prompt = (
            "Use the add tool to compute 2 + 3. Respond with only the numeric result and nothing else."
        )
        # Use small thinking budget for seed-oss models
        thinking_budget = 512 if "seed-oss" in self.model_name.lower() else None
        
        content, model = lm.act(prompt, self.model_name, 0.2, [add], thinking_budget)
        self.assertIsInstance(content, str)
        self.assertGreater(len(content.strip()), 0, "act() returned empty content")
        # Be robust: accept '5' anywhere or extract first integer
        import re
        digits = re.findall(r"-?\d+", content)
        self.assertTrue("5" in content or (digits and int(digits[0]) == 5), f"act() did not return correct sum in content: {content}")
        print(f"ACT content: {content}")
        self.assertIsInstance(model, str)
        self.assertGreater(len(model.strip()), 0)

    def test_act_tools_steps_output(self):
        from spgen.workflow.providers import lmstudio_client as lm

        def add(a: int, b: int) -> int:
            """Given two integers a and b, return their sum as an integer."""
            return int(a) + int(b)

        def multiply(a: int, b: int) -> int:
            """Given two integers a and b, return their product as an integer."""
            return int(a) * int(b)

        prompt = (
            "Use the provided tools to compute the area of a rectangle with width 12 and height 9. "
            "Show your work as numbered steps (e.g., '1. ...', '2. ...'), then on the last line write "
            "'Final Answer: <number>'. Use at least two steps and prefer the tools over mental math."
        )

        # Use small thinking budget for seed-oss models
        thinking_budget = 512 if "seed-oss" in self.model_name.lower() else None
        
        content, model = lm.act(prompt, self.model_name, 0.1, [add, multiply], thinking_budget)
        self.assertIsInstance(content, str)
        text = content.strip()
        print(f"ACT content: {content}")
        self.assertGreater(len(text), 0, "act() returned empty content for steps problem")
        # Must include at least two numbered steps
        self.assertIn("1.", text, "Output did not include a first numbered step")
        self.assertIn("2.", text, "Output did not include a second numbered step")
        # Must include a final answer of 108
        self.assertIn("Final Answer", text, "Missing 'Final Answer' line")
        import re
        nums = [int(n) for n in re.findall(r"-?\d+", text)]
        self.assertIn(108, nums, f"Expected 108 in output, got: {text}")


if __name__ == "__main__":
    unittest.main()



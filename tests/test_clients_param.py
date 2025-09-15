import os
import unittest
import tempfile


class ParamClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.providers = []
        # Redirect logs during tests
        try:
            from spgen.workflow.logging_utils import set_tool_log_dir
            tmpdir = tempfile.mkdtemp(prefix="llm_logs_")
            set_tool_log_dir(tmpdir)
        except Exception:
            pass

        # LM Studio SDK provider
        try:
            import lmstudio as lms  # type: ignore
            from spgen.workflow.providers import lmstudio_client as lm

            models = lms.list_loaded_models()
            if models:
                model_name = models[0].identifier
                cls.providers.append({
                    "name": "lmstudio_sdk",
                    "respond": lambda prompt: lm.respond(prompt, model_name, 0.2),
                    "act": lambda prompt, tools: lm.act(prompt, model_name, 0.2, tools),
                })
        except Exception:
            pass

        # OpenAI-compatible provider (via LM Studio server)
        try:
            from langchain_openai import ChatOpenAI  # type: ignore
            from spgen.workflow.providers import openai_client as oa
            from langchain_core.messages import HumanMessage

            base_url = os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")
            model_name = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")
            llm = ChatOpenAI(model=model_name, base_url=base_url, api_key="not-needed", temperature=0.2)
            # probe
            _ = llm.invoke([HumanMessage(content="ok")])

            cls.providers.append({
                "name": "openai_compatible",
                "respond": lambda prompt: oa.respond(prompt, llm, model_name),
                "act": lambda prompt, tools: oa.act(prompt, llm, model_name, tools),
            })
        except Exception:
            pass

        if not cls.providers:
            raise unittest.SkipTest("No providers available for parameterized tests.")

    def test_respond_hello_all_providers(self):
        for p in self.providers:
            print(f"Testing {p['name']}")
            with self.subTest(provider=p["name"]):
                content, model = p["respond"]("Say the word hello.")
                self.assertIsInstance(content, str)
                self.assertIn("hello", content.lower())
                self.assertIsInstance(model, str)

    def test_act_add_5_all_providers(self):
        for p in self.providers:
            print(f"Testing {p['name']}")
            with self.subTest(provider=p["name"]):
                def add(a: int, b: int) -> int:
                    """Given two integers a and b, return their sum as an integer."""
                    return int(a) + int(b)

                content, model = p["act"](
                    "Use the add tool to compute 2 + 3. Respond with only the numeric result and nothing else.",
                    [add],
                )
                text = (content or "").strip()
                self.assertTrue(text)
                import re
                digits = re.findall(r"-?\d+", text)
                self.assertTrue("5" in text or (digits and int(digits[0]) == 5), f"Wrong sum: {text}")

    def test_act_steps_area_all_providers(self):
        for p in self.providers:
            print(f"Testing {p['name']}")
            with self.subTest(provider=p["name"]):
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
                content, model = p["act"](prompt, [add, multiply])
                text = (content or "").strip()
                self.assertTrue(text)
                self.assertIn("1.", text)
                self.assertIn("2.", text)
                self.assertIn("Final Answer", text)
                import re
                nums = [int(n) for n in re.findall(r"-?\d+", text)]
                self.assertIn(108, nums, f"Expected 108, got: {text}")


if __name__ == "__main__":
    unittest.main()



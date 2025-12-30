
import os
import unittest
import unittest
from dotenv import load_dotenv
from env_setup import substitute_env_vars
from langchain.agents import create_agent

load_dotenv()
from langchain_core.tools import tool

# Mock tool
@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

class TestEnhancements(unittest.TestCase):
    def test_env_substitution(self):
        os.environ["TEST_SECRET"] = "my_secret_token"
        config = {
            "server": {
                "headers": {
                    "Authorization": "Bearer ${TEST_SECRET}"
                },
                "url": "http://example.com/${TEST_SECRET}"
            },
            "list": ["val", "${TEST_SECRET}"]
        }
        
        expected = {
            "server": {
                "headers": {
                    "Authorization": "Bearer my_secret_token"
                },
                "url": "http://example.com/my_secret_token"
            },
            "list": ["val", "my_secret_token"]
        }
        
        result = substitute_env_vars(config)
        self.assertEqual(result, expected)
        print("✅ Env Substitution Verified")

    def test_system_prompt_integration(self):
        # We can't easily mock the 'client.py' main loop, but we can verify 
        # that create_agent accepts system_prompt without error.
        
        prompt = "You are a verification agent."
        
        # This checks if the API signature is correct, which was the main risk
        try:
            agent = create_agent(
                model="openai:gpt-4o", # Mock model string, won't be called
                tools=[add],
                system_prompt=prompt
            )
            print("✅ create_agent accepted system_prompt parameter")
        except Exception as e:
            self.fail(f"create_agent failed with system_prompt parameter: {e}")

if __name__ == "__main__":
    unittest.main()

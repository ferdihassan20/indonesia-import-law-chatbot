
import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.prompt.input_decomposition_prompt import INPUT_DECOMPOSER_PROMPT
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

class LLMRuntime:
    def __init__(self, api_provider="groq"):
        self.api_provider = api_provider.lower()
        if self.api_provider == "openai":
            self.openai_api_key = open("openai_api.txt", "r").read().strip()
            self.client = ChatOpenAI(openai_api_key=self.openai_api_key, model_name="gpt-4o-mini", temperature=0.3)
        elif self.api_provider == "groq":
            self.groq_api_key = open("groq_api.txt", "r").read().strip()
            self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"  # Example endpoint, adjust as needed
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")

    def generate(self, prompt):
        if self.api_provider == "openai":
            # If prompt is a string, wrap it in messages list
            if isinstance(prompt, str):
                messages = [HumanMessage(content=prompt)]
            elif isinstance(prompt, list):
                # Convert dicts to message objects
                messages = []
                for m in prompt:
                    role = m.get("role", "")
                    content = m.get("content", "")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "system":
                        messages.append(SystemMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))
                    else:
                        raise ValueError(f"Unknown role in message: {role}")
            else:
                raise TypeError(f"Unsupported prompt type: {type(prompt)}")
            response = self.client(messages=messages)
            return response.content
        elif self.api_provider == "groq":
            # Prepare the payload for GROQ API
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            elif isinstance(prompt, list):
                messages = prompt
            else:
                raise TypeError(f"Unsupported prompt type: {type(prompt)}")
            payload = {
                "model": "deepseek-r1-distill-llama-70b",  # Adjust model name if needed
                "messages": messages,
                "temperature": 0.3
            }
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            response = requests.post(self.groq_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Assuming the response structure is similar to OpenAI's
            return data["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")

class InputDecomposer(LLMRuntime):
    def decompose(self, user_input):
        prompt = INPUT_DECOMPOSER_PROMPT.replace("{user_input}", user_input)
        return self.generate(prompt)

if __name__ == "__main__":
    decomposer = InputDecomposer()
    custom_input = "impor China"
    output = decomposer.decompose(custom_input)
    print(output)

import openai
import requests

class LLMRuntime:
    def __init__(self):
        # Load API Key dari file
        self.openai_api_key = open("openai_api.txt", "r").read().strip()
        self.client = openai.OpenAI(api_key=self.openai_api_key)  

    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, 
        )
        return response.choices[0].message.content

class GroqRuntime:
    def __init__(self):
        # Load Groq API Key dari file
        self.groq_api_key = open("groq_api.txt", "r").read().strip()
        self.api_url = "https://api.groq.ai/v1/chat/completions"  # Placeholder URL, adjust as needed

    def generate(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "groq-model",  # Placeholder model name, adjust as needed
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            # Adjust the path to the content based on Groq API response structure
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Groq API request failed with status {response.status_code}: {response.text}")

# # Contoh penggunaan
# if __name__ == "__main__":
#     groq = GroqRuntime()
#     result = groq.generate("Apa itu machine learning?")
#     print(result)

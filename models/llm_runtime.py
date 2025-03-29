import sys 
import os
import groq

from groq import Groq

# print(api_key)
# sys.exit()

# agar memudahkan untuk memanggil API
class LLMRuntime ():

    def __init__(self):
        # groq
        self.groq_api_key = open("groq_api.txt", "r").read()
        self.groq_client = Groq(
            api_key = self.groq_api_key,
        )

    
    def generate(self, prompt):
        chat_completion = self.groq_client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="llama-3.3-70b-versatile",
    # Makin rendah makin hati-hati
    temperature = 0.3,
    )
        return chat_completion.choices[0].message.content
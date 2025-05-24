import os 
import time
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


class AICaller:
    def __init__(self):
        load_dotenv(override=True)

        self.models = [
            'gpt-4o-mini',
            'gpt-4o',
            'gpt-4.1'
        ]

        self.json_format = { "type": "json_object" }

        self.load_openai_env()
  

    def load_openai_env(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key
        )



    def chat_openai(self,model: str, messages: list, temperature: float, response_format: str | None) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format
        )

        return response.choices[0].message.content

    def show_models(self):
        for model in self.models:
            print(model)



if __name__ == '__main__':
    messages = [
        {"role": "system", "content": '''You are a science teacher'''},
        {"role": "user", "content": '''Why is the sky blue? Provide the output in JSON format.'''}
    ]

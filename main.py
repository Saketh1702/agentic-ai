import google.generativeai as genai
import requests
import json
import datetime
import os
import sys
from dotenv import load_dotenv
from typing import List, Dict, Any

# load environemtn variables

load_dotenv()

# configure our gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#define our agent class
class Agent:
    def __init__(self, model: str='gemini-pro', memory=[]):
        self.model = model
        self.gemini = genai.GenerativeModel(self.model)
        

    # def _manage_memory(self):
    #     pass

    def ask_gemini(self, prompt: str) -> str:
        try:
            chat = self.gemini.start_chat()
            response = chat.send_message(prompt)
            response = response.text
            return response
        
        except Exception as ex:
            raise Exception(f"Error: {ex}")
    
    def fetch_wikipedia_summary(self, topic: str) -> str:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
            response = requests.get(url, timeout=10)
            data = response.json()
            summary = data.get('extract')
            return summary
        
        except Exception as ex:
            raise Exception(f"Error: {ex}")

    def fetch_news(self, keyword: str) -> str:
        try:
            api_key = os.getenv('NEWS_API_KEY')
            if not api_key:
                raise ValueError("NEWS API key not found")
            url = f'https://newsapi.org/v2/everything?q={keyword}&apiKey={api_key}&pageSize=5'
            response = requests.get(url, timeout=10)
            data = response.json()
            articles = data.get('articles')

            if not articles:
                return 'No articles found'
            
            formatted_articles = [
                f"{i+1} {article.get('title')} - {article.get('source').get('name')}" for i, article in enumerate(articles)
            ]

            return '\n'.join(formatted_articles)

        
        except Exception as ex:
            print(f'Error: {ex}')


    def execute_task(self, task: str) -> str:
        if not task:
            raise Exception('Task cannot be empty')
        
        task = task.lower()

        try:
            if 'wikipedia' in task:
                parts = task.split('wikipedia')
                if len(parts) < 2:
                    raise Exception('Please provide a topic to search for')
                
                topic = task.split('wikipedia')[1].strip()
                return self.fetch_wikipedia_summary(topic)
            
            elif 'news' in task:
                parts = task.split('news')
                if len(parts) < 2:
                    raise Exception('Please provide a topic to search for')
                
                topic = task.split('news')[1].strip()
                return self.fetch_news(topic)
            
            else:
                return self.ask_gemini(task)
            
        except Exception as ex:
            raise Exception(f"Error: {ex}")



    def show_task_history(self):
        pass


def main():
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("trying")
            raise Exception('GOOGLE_API_KEY not found in .env file')
        
        agent = Agent()

        while True:
            try:
                task = input('What would you like me to do?\n').strip()
                if task == 'exit':
                    print('Goodbye')
                    break

                elif task == "history":
                    agent.show_task_history()

                else:
                    response = agent.execute_task(task)
                    print(response)

            except Exception as ex:
                print(f'Error: {ex}')
                continue

    except Exception as ex:
            print(f'Error: {ex}')
            sys.exit(1)

if __name__ == "__main__":
    main()

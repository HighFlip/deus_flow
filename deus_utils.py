import openai
from prefect import task

@task
def llm_call(prompt: str, model: str = 'gpt-4'):
    return openai.ChatCompletion.create(
            model=model, temperature=0, max_tokens=7000, messages=prompt, stop="STOP")

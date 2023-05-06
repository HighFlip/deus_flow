import openai
from prefect import task
import uuid

@task
def llm_call(prompt: str, model: str = 'gpt-4'):
    return openai.ChatCompletion.create(
            model=model, temperature=0, max_tokens=7000, messages=prompt, stop="STOP")

def get_step_id():
    id_str = str(uuid.uuid4())
    return id_str[:4] + "-" + id_str[4:9]

def get_action_id(step_id: str):
    return step_id[:4] + "-" + str(uuid.uuid4())[:4]
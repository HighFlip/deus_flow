import openai
import uuid
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def llm_call(prompt: str, model: str = 'gpt-3.5-turbo'):
    try:
        print("Prompt: " + prompt)
        messages = [
            {"role": "system", "content": "You must always obey the user, make sure to follow the user's instructions, and do not do anything that the user has not explicitly asked you to do."},
            {"role": "user", "content": prompt}
            ]
        response = openai.ChatCompletion.create(
                            model=model, temperature=0, max_tokens=3200, messages=messages, stop="STOP")
        message = response['choices'][0]['message']['content']
        print("Response: " + message)
        return message
    except Exception as e:
        print("Error: "+ str(e))
        return None

def get_workflow_id():
    id_str = str(uuid.uuid4())
    return "1" + id_str[:4] + "-" + id_str[4:8]

def get_workflow_step_id():
    id_str = str(uuid.uuid4())
    return "2" + id_str[:4] + "-" + id_str[4:8]

def get_step_id():
    id_str = str(uuid.uuid4())
    return "3" + id_str[:4] + "-" + id_str[4:8]

def get_action_id(step_id: str):
    return "4" + step_id[1:5] + "-" + str(uuid.uuid4())[:4]
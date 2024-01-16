"""
A module of CodeBuddy for sending requests and receiving responses from ChatGPT AI.
"""

# Important imports for proper work of this module
import yaml
from openai import OpenAI

# Load the YAML file
with open('configuration/config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Setting up the OpenAI profile with proper api_key
client = OpenAI(api_key=config['setup'][0]['ChatGPT_API'])

def receive_task(PROMPT: str, MaxToken: int) -> str:
    """
    A function to send a request to OpenAI and get a response from AI with ready task of the given difficulty
    """
    response = client.chat.completions.create(
        model = config['setup'][2]['ChatGPT_model'],
        messages = [{"role": "system", "content": config['prompts']['ChatGPT_setup_prompt']['content_giver']}, {"role": "user", "content": PROMPT}],
        max_tokens = MaxToken,
        temperature= config['setup'][3]['ChatGPT_temperature'],
        top_p= config['setup'][4]['ChatGPT_top_p'],
        frequency_penalty= config['setup'][5]['ChatGPT_frequency_penalty'],
        presence_penalty= config['setup'][6]['ChatGPT_presence_penalty']

    )
    return response.choices[0].message.content

def check_task(PROMPT: str, MaxToken: int):
    """
    A function to send a request to OpenAI and get a response from AI with ready responce to the user's request with a task and a solution
    """
    response = client.chat.completions.create(
        model = config['setup'][2]['ChatGPT_model'],
        messages = [{"role": "system", "content": config['prompts']['ChatGPT_setup_prompt']['content_receiver']}, {"role": "user", "content": PROMPT}],
        max_tokens = MaxToken,
        temperature= config['setup'][3]['ChatGPT_temperature'],
        top_p= config['setup'][4]['ChatGPT_top_p'],
        frequency_penalty= config['setup'][5]['ChatGPT_frequency_penalty'],
        presence_penalty= config['setup'][6]['ChatGPT_presence_penalty']
    )
    return response.choices[0].message.content

def call_task(num_task: int) -> str:
    """
    A bridge between TelegramBot_handler and recieve_task function.
    """
    if num_task == 0:
        return receive_task(config['prompts']['PROMPT_easy_task'], MaxToken=config['tokens'][0]['easy'])
    elif num_task == 1:
        return receive_task(config['prompts']['PROMPT_medium_task'], MaxToken=config['tokens'][1]['medium'])
    return receive_task(config['prompts']['PROMPT_difficult_task'], MaxToken=config['tokens'][2]['hard'])


def call_check_task(task_solution: str, task: str) -> str:
    """
    A bridge between TelegramBot_handler and check_task.
    """
    prompt = config['prompts']['PROMPT_give_code_feedback'] + "TASK GIVEN FOR THE USER: " + task + " "  + "USER SOLUTION: " + task_solution
    return check_task(prompt, 2000)

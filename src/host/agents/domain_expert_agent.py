

from tqdm import tqdm
import logging

import openai
import logging

def run_gpt_chat(config):
    # print(config)
    user_query = config['user_query']
   
    API_KEY = config['openai_api_key']
    model = config['model']
    SEED = config.get('seed', 42)  # Default seed value if not provided

    openai.api_key = API_KEY

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": user_query}
        ],
        temperature=0,          # Makes output deterministic
        seed=SEED               # Ensures repeatability across runs
    )

    return response['choices'][0]['message']['content'].split('\n')

def get_gpt_information(gpt_info):
    logging.info(f"Reading GPT information from {gpt_info}...")

    try:

        openai_api_key = gpt_info["openai_api_key"]

        if not openai_api_key:
            raise ValueError(f"The file {gpt_info} does not contain a valid 'openai_api_key' field.")
        gpt_role = gpt_info['gpt_role']

        model = gpt_info['model']


    except FileNotFoundError:
        raise FileNotFoundError(f"The file {gpt_info} does not exist.")

    return openai_api_key, gpt_role, model

def compentency_question_base(contextual_text):
    """
    Generates a competency question based on the provided contextual text.
    
    Args:
        contextual_text (str): The contextual text to base the question on.
        
    Returns:
        str: The generated competency question.
    """
    return f"Based on the following context, Please prepare competency questions for ontology development? Context: {contextual_text}"



def run_gpt_based_cq_generation(input_context, gpt_information_file):
    """
    Runs the GPT-based contextual question generation.
    
    Args:
        input_context (json): The JSON object containing contextual information.
        gpt_information_file (str): Path to the file containing GPT role and model information.
    """


    cq_results = []
    
    for query in tqdm(input_context, desc="Running GPT-based contextual question generation from text"):
        # print(f"Generated questions:")
        contextual_text = query['content']
        user_query = compentency_question_base(contextual_text)
        gpt_information_file['user_query'] = user_query
        questions = run_gpt_chat(gpt_information_file)
        query['competency_questions'] = questions
        
        cq_results.append(query)

    return cq_results

def cq_generation(input_context, gpt_information_file):
    """
    Main function to run the GPT-based contextual question generation.
    
    Args:
        input_context (json): The JSON object containing contextual information.
        gpt_information_file (str): Path to the file containing GPT role and model information.
    """
    try:
        
        compentency_questions = run_gpt_based_cq_generation(input_context, gpt_information_file)
        logging.info("GPT-based contextual question generation completed.")
        return compentency_questions
    except Exception as e:
        logging.error(f"Error occurred during GPT-based contextual question generation: {e}")
        return None
  

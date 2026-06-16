

from asyncio import run

from tqdm import tqdm
import logging
import json
import openai
import logging
import re


def run_gpt_chat(config):
  
    user_query = config['user_query']
   
    API_KEY = config['api_key']
    print(f"Using OpenAI API key: {API_KEY}")
    model = config['model']
    print(f"Using GPT model: {model}")
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
    gpt = gpt_info['gpt']
    try:

        openai_api_key = gpt["api_key"]

        if not openai_api_key:
            raise ValueError(f"The file {gpt_info} does not contain a valid 'api_key' field.")
        gpt_role = gpt['competency_question_prompt']

        model = gpt['model']


    except FileNotFoundError:
        raise FileNotFoundError(f"The file {gpt_info} does not exist.")

    return openai_api_key, gpt_role, model

def compentency_question_base(contextual_text, gpt_information):
    """
    Generates a competency question based on the provided contextual text.
    
    Args:
        contextual_text (str): The contextual text to base the question on.
        
    Returns:
        str: The generated competency question.
    """
    compentency_question_text_base_path = gpt_information['competency_question_prompt']
    compentency_question_text_base = open(compentency_question_text_base_path, 'r').read()

    print(f"Generating competency question with base prompt: {compentency_question_text_base}")
    return f"{compentency_question_text_base} Context: {contextual_text}"



def run_gpt_based_cq_generation(input_context, gpt_information):
    """
    Runs the GPT-based contextual question generation.
    
    Args:
        input_context (json): The JSON object containing contextual information.
        gpt_information (dict): Dictionary containing GPT role and model information.
    """

    contextual_text = input_context
    user_query = compentency_question_base(contextual_text, gpt_information)
    gpt_information['user_query'] = user_query
    print(f"User query for GPT")
    questions = run_gpt_chat(gpt_information)
    print(f"Generated competency questions: {questions}")

    return questions




def cq_generation(input_context, config):
    """
    Main function to run the GPT-based contextual question generation.
    
    Args:
        input_context (json): The JSON object containing contextual information.
        gpt_information_file (str): Path to the file containing GPT role and model information.
    """
    try:

        gpt_information = json.load(open(config, 'r'))['gpt']

        print("Loading GPT information...")
        compentency_questions = run_gpt_based_cq_generation(input_context, gpt_information)
        logging.info("GPT-based contextual question generation completed.")

        return compentency_questions
    
    except Exception as e:
        logging.error(f"Error occurred during GPT-based contextual question generation: {e}")
        return None
  

MAX_CHARS = 35000  # safe for 16k context models; reduce to 25000 if needed


def safe_to_string(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(map(str, value))
    return str(value)


def truncate_text(text, max_chars=MAX_CHARS):
    text = safe_to_string(text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[TRUNCATED: input was too long]"


def chunk_text(text, max_chars=MAX_CHARS):
    text = safe_to_string(text)
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()



def chunks(items, size=500):
    for i in range(0, len(items), size):
        yield items[i:i + size]
def run_full_ttl_ontology(
    concepts,
    config,
):
    try:
        print("Loading GPT information...")

        with open(config, "r", encoding="utf-8") as f:
            gpt_information = json.load(f)["gpt"]

        triple_generation_prompt = read_file(gpt_information["triple_generation_prompt"])
        ontology_generation_prompt = read_file(gpt_information["ontology_generation_prompt"])
        domain_range_prompt = read_file(gpt_information["domain_range_prompt"])
        data_type_prompt = read_file(gpt_information["data_type_prompt"])
        axioms_prompt = read_file(gpt_information["axioms_prompt"])
        rdf_comments_prompt = read_file(gpt_information["rdf_comments"])
        individuals_prompt = read_file(gpt_information["individuals_prompt"])
        

        print("Generating triples in chunks...")
        gpt_information["user_query"] = f"{triple_generation_prompt}\n\nConcepts:{concepts}"
        all_triples = run_gpt_chat(gpt_information)


        triples_text = "\n".join(all_triples)

        print("Generating domain and range info...")
        gpt_information['user_query'] = f"{domain_range_prompt}\n\nConcepts:\n{concepts}"
        domain_range_text = run_gpt_chat(gpt_information)


        print("Generating data type info...")
        gpt_information['user_query'] = f"{data_type_prompt}\n\nTriples:\n{triples_text}"
        data_type_text = run_gpt_chat(gpt_information)
        print("Generating axioms...")
        gpt_information['user_query'] = f"{axioms_prompt}\n\nConcepts:\n{concepts}"
        axioms_text = run_gpt_chat(gpt_information)
        print("Generating RDF comments...")
        gpt_information['user_query'] = f"{rdf_comments_prompt}\n\nConcepts:\n{concepts}"
        rdf_comments_text = run_gpt_chat(gpt_information)

        print("Generating individuals...")
        gpt_information['user_query'] = f"{individuals_prompt}\n\nConcepts:\n{concepts}"
        individuals_text = run_gpt_chat(gpt_information)
        print("Generating final TTL in chunks...")

        gpt_information['user_query'] = f"""
                "Follow this: {ontology_generation_prompt}\n
                Concepts: {concepts}\n
                Triples: {triples_text}\n
                Domain and Range Info: {domain_range_text}\n
                Properties: {data_type_text}\n
                Axioms: {axioms_text}\n
                RDF Comments: {rdf_comments_text}\n
                Individuals: {individuals_text}\n
                Do not include another text, only return the turtle content of the ontology.
                """
        turtle = run_gpt_chat(gpt_information)
        turtle = "\n".join(turtle)

        return turtle

    except Exception as e:
        logging.exception(f"Error occurred while generating ontology: {e}")
        return None

def get_borrows_from_mappings(turtle, mappings, config):
    try:
        print("Loading GPT information...")

        with open(config, "r", encoding="utf-8") as f:
            gpt_information = json.load(f)["gpt"]

        borrows_from_mappings_prompt = read_file(gpt_information["borrows_from_prompt"])

        gpt_information['user_query'] = f"""
                                        Following this: {borrows_from_mappings_prompt}\n\n
                                        Ontology: {turtle}\n\n
                                        Mappings: {mappings}.\n\n
                                        Do not include another text, only return the turtle content of the ontology.
                                        """
        new_turtle = run_gpt_chat(gpt_information)
        new_turtle = "\n".join(new_turtle)


        return new_turtle

    except Exception as e:
        logging.exception(f"Error occurred while generating borrows from mappings: {e}")
        return None

def run_gpt_based_concept_extraction(questions, config):
    """
    Runs the GPT-based concept extraction.
    
    Args:
        questions (list): The list of competency questions.

        gpt_information (dict): Dictionary containing GPT role and model information.
    """
    try:
        gpt_information = json.load(open(config, 'r'))['gpt']

        print("Loading GPT information...")
        
        prompt = open(gpt_information['concept_extraction_prompt'], 'r').read()
        
        print(f"Generating concepts with base prompt: {prompt}")
        gpt_information['user_query'] = f"{prompt} Competency Questions: {questions}"
        concepts = run_gpt_chat(gpt_information)
        logging.info("GPT-based concept extraction completed.")
        return concepts
    except Exception as e:
        logging.error(f"Error occurred during GPT-based concept extraction: {e}")
        return None




def run_gpt_based_mapping_to_existing_ontologies(
    domain_entities,
    domain_properties,
    existing_classes,
    existing_properties,
    config
):
    try:
        with open(config, "r") as f:
            gpt_config = json.load(f)["gpt"]

        with open(gpt_config["mapping_to_existing_ontologies_prompt"], "r") as f:
            base_prompt = f.read()

        gpt_config["user_query"] = f"""{base_prompt}. existing_properties: {existing_properties}, Domain properties: {domain_properties}. Do not include any thing other than the mapping results in your response. Return the mapping results in a JSON format."""
        property_mappings = run_gpt_chat(gpt_config)
        gpt_config["user_query"] = f"""{base_prompt}. existing_classes: {existing_classes}, Domain classes: {domain_entities}. Do not include any thing other than the mapping results in your response. Return the mapping results in a JSON format."""
        class_mappings = run_gpt_chat(gpt_config)
        

        return {
            "corresponding_classes": class_mappings,
            "corresponding_properties": property_mappings
        }

    except Exception as e:
        logging.error(
            f"Error occurred during GPT-based mapping to existing ontologies: {e}"
        )
        return None
    


def fix_mapping_output(data):
    fixed = {
        "corresponding_classes": [],
        "corresponding_properties": []
    }

    for block in data:
       
        if isinstance(block, list):
            block = "\n".join(block)

        block = block.strip()
        block = re.sub(r"^```json\s*", "", block)
        block = re.sub(r"^```\s*", "", block)
        block = re.sub(r"\s*```$", "", block)

        parsed = json.loads(block)

        for item in parsed.get("corresponding_classes", []):
            if "alignment" in item:
                item["relation"] = item["alignment"].get("relation")
                item["measure"] = item["alignment"].get("measure")
                del item["alignment"]

            fixed["corresponding_classes"].append(item)

        for item in parsed.get("corresponding_properties", []):
            if "alignment" in item:
                item["relation"] = item["alignment"].get("relation")
                item["measure"] = item["alignment"].get("measure")
                del item["alignment"]

            fixed["corresponding_properties"].append(item)

    return fixed

def  fix_syntax_errors_in_turtle(data, config):
    try:
        gpt_information = json.load(open(config, 'r'))['gpt']
        prompt = open(gpt_information['turtle_syntax_fix_prompt'], 'r').read()
        gpt_information['user_query'] = f"{prompt} Turtle content: {data}"
        fixed_turtle = run_gpt_chat(gpt_information)
        return "\n".join(fixed_turtle)
    except Exception as e:
        logging.error(f"Error occurred during fixing syntax errors in turtle: {e}")
        return data

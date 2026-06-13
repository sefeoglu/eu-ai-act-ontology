

from tqdm import tqdm
import logging
import json
import openai
import logging

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




def cq_generation(input_context, config="/Users/sefika/projects/eu-ai-act-ontology/config/api_configs.json"):
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
  
def run_full_ttl_ontology(concepts, mappings, config="/Users/sefika/projects/eu-ai-act-ontology/config/api_configs.json"):
    """Run full pipleline from question to concept extraction."""
    """
    Args:
        concepts (list): The list of extracted concepts.
        mappings (dict): The dictionary containing mappings to existing ontologies.
        config (str): Path to the file containing GPT role and model information.
    
    Returns:
        str: The generated ontology in TTL format."""
    """
        1. prompt 3
        2. prompt 4
        3. prompt 5
        4. prompt 6
        5. prompt 7
        6. prompt 8
        7. prompt 9
    """
    try:
        gpt_information = json.load(open(config, 'r'))['gpt']
        triple_generation_prompt = open(gpt_information['triple_generation_prompt'], 'r').read()
        ontology_generation_prompt = open(gpt_information['ontology_generation_prompt'], 'r').read()
        domain_range_prompt = open(gpt_information['domain_range_prompt'], 'r').read()
        data_type_prompt = open(gpt_information['data_type_prompt'], 'r').read()
        axioms_prompt = open(gpt_information['axioms_prompt'], 'r').read()
        rdf_comments_prompt = open(gpt_information['rdf_comments'], 'r').read()
        individuals_prompt = open(gpt_information['individuals_prompt'], 'r').read()
        print("Generating ontology with GPT...")
        # Step 1: Generate triples from concepts
        gpt_information['user_query'] = f"{triple_generation_prompt} Concepts: {concepts}"
        triples = run_gpt_chat(gpt_information)
        print(f"Generated triples: {triples}")
        # Step 2: Generate domain and range for properties
        gpt_information['user_query'] = f"{domain_range_prompt} Triples: {triples}"
        domain_range_info = run_gpt_chat(gpt_information)
        print(f"Generated domain and range info: {domain_range_info}")
        # Step 3: Generate data types for properties
        gpt_information['user_query'] = f"{data_type_prompt} Triples: {triples}"
        data_type_info = run_gpt_chat(gpt_information)
        print(f"Generated data type info: {data_type_info}")
        # Step 4: Generate axioms
        gpt_information['user_query'] = f"{axioms_prompt} Triples: {triples}"
        axioms = run_gpt_chat(gpt_information)
        print(f"Generated axioms: {axioms}")
        # Step 5: Generate RDF comments
        gpt_information['user_query'] = f"{rdf_comments_prompt} Triples: {triples}"
        rdf_comments = run_gpt_chat(gpt_information)
        print(f"Generated RDF comments: {rdf_comments}")
        # Step 6: Generate individuals
        gpt_information['user_query'] = f"{individuals_prompt} Triples: {triples}"
        individuals = run_gpt_chat(gpt_information)
        print(f"Generated individuals: {individuals}")
        # Step 7: Generate final ontology in TTL format
        gpt_information['user_query'] = f"{ontology_generation_prompt} Triples: {triples} Domain and Range Info: {domain_range_info} Data Type Info: {data_type_info} Axioms: {axioms} RDF Comments: {rdf_comments} Individuals: {individuals} Mappings: {mappings}"
        ontology_content = run_gpt_chat(gpt_information)
        print(f"Generated ontology content: {ontology_content}")    
        ontology_content_str = "\n".join(ontology_content)
        print(f"Final ontology content: {ontology_content_str}")
        return ontology_content_str


    except Exception as e:
        logging.error(f"Error occurred while loading GPT information: {e}")
        return None




def run_gpt_based_concept_extraction(questions, config="/Users/sefika/projects/eu-ai-act-ontology/config/api_configs.json"):
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



def chunk_list(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def compact_items(items, max_items=50, max_chars_each=300):
    compacted = []
    for item in items[:max_items]:
        text = str(item)
        compacted.append(text[:max_chars_each])
    return compacted

def run_gpt_based_mapping_to_existing_ontologies(
    concepts,
    classes,
    properties,
    config="/Users/sefika/projects/eu-ai-act-ontology/config/api_configs.json",
):
    try:
        with open(config, "r") as f:
            gpt_config = json.load(f)["gpt"]

        with open(gpt_config["mapping_to_existing_ontologies_prompt"], "r") as f:
            base_prompt = f.read()[:3000]   # prevent huge prompt file

        all_mappings = []

        for concept in concepts:
            
            candidate_classes = compact_items(classes, max_items=30)
            candidate_properties = compact_items(properties, max_items=30)

            user_query = f"""
{base_prompt}

Map this concept to existing ontology terms.

Concept:
{str(concept)[:500]}

Candidate classes:
{json.dumps(candidate_classes, ensure_ascii=False)}

Candidate properties:
{json.dumps(candidate_properties, ensure_ascii=False)}

Return JSON only.
"""

            batch_config = {
                **gpt_config,
                "user_query": user_query,
            }

            result = run_gpt_chat(batch_config)
            if result:
                result_str = "\n".join(result)
                result = json.loads(result_str)
                all_mappings.append(result)

        return all_mappings

    except Exception as e:
        logging.error(
            f"Error occurred during GPT-based mapping to existing ontologies: {e}"
        )
        return None

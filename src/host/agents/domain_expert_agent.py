import logging
import json
import openai
import os
import sys

from pathlib import Path

PACKAGE_PARENT = '..'

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

PREFIX = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-4]) + "/"
def run_openai_chat_completion(config):
  
    user_query = config['user_query']
   
    api_key = config['api_key']
    print("Using configured OpenAI API credentials")
    model = config['model']
    print(f"Using GPT model: {model}")
    seed_value = config.get('seed', 42)  # Default seed value if not provided

    openai.api_key = api_key

    completion_response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": user_query}
        ],
        temperature=0,          # Makes output deterministic
        seed=seed_value         # Ensures repeatability across runs
    )
    return completion_response['choices'][0]['message']['content'].split('\n')

def build_competency_question_prompt(contextual_text, gpt_information):
    """
    Generates a competency question based on the provided contextual text.
    
    Args:
        contextual_text (str): The contextual text to base the question on.
        gpt_information (dict): Dictionary containing GPT role and model information.
    Returns:
        str: The generated competency question.
    """
    competency_question_prompt_path = PREFIX + gpt_information['competency_question_prompt']
    competency_question_prompt = read_text_file(competency_question_prompt_path)

    print(f"Generating competency question with base prompt: {competency_question_prompt}")
    return f"{competency_question_prompt} Context: {contextual_text}"



def generate_competency_questions_with_gpt(input_context, gpt_information):
    """
    Runs the GPT-based contextual question generation.
    
    Args:
        input_context (json): The JSON object containing contextual information.
        gpt_information (dict): Dictionary containing GPT role and model information.
    """

    contextual_text = input_context
    prompt_text = build_competency_question_prompt(contextual_text, gpt_information)
    gpt_information['user_query'] = prompt_text
    print(f"User query for GPT")
    generated_questions = run_openai_chat_completion(gpt_information)
    print(f"Generated competency questions: {generated_questions}")

    return generated_questions




def generate_competency_questions(input_context, config):
    """
    Main function to run the GPT-based contextual question generation.
    
    Args:
        input_context (json): The JSON object containing contextual information.
        gpt_information_file (str): Path to the file containing GPT role and model information.
    """
    try:
        gpt_information, _ = load_gpt_config(config)

        print("Loading GPT information...")
        competency_questions = generate_competency_questions_with_gpt(input_context, gpt_information)
        logging.info("GPT-based contextual question generation completed.")

        return competency_questions
    
    except Exception as e:
        logging.error(f"Error occurred during GPT-based contextual question generation: {e}")
        return None


def read_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def resolve_config_resource_path(config_path, resource_path):
    resource_candidate = Path(resource_path)
    if resource_candidate.is_absolute() or resource_candidate.exists():
        return resource_candidate

    config_dir = Path(config_path).resolve().parent
    repo_root = config_dir.parent
    resource_parts = resource_candidate.parts

    if resource_parts and resource_parts[0] == repo_root.name:
        repo_relative_candidate = repo_root.joinpath(*resource_parts[1:])
        if repo_relative_candidate.exists():
            return repo_relative_candidate

    repo_root_candidate = repo_root / resource_candidate
    if repo_root_candidate.exists():
        return repo_root_candidate

    return config_dir / resource_candidate


def load_gpt_config(config_path):
    resolved_config_path = Path(config_path).resolve()
    with open(resolved_config_path, "r", encoding="utf-8") as f:
        gpt_information = json.load(f)["gpt"]
    return gpt_information, resolved_config_path


def load_gpt_prompt(config_path, prompt_key):
    gpt_information, resolved_config_path = load_gpt_config(config_path)
    prompt_path = resolve_config_resource_path(
        resolved_config_path,
        PREFIX + gpt_information[prompt_key],
    )
    return gpt_information, read_text_file(prompt_path)


def generate_full_turtle_ontology(
    concepts,
    config,
):
    try:
        print("Loading GPT information...")

        gpt_information, resolved_config_path = load_gpt_config(config)
        triple_generation_prompt = read_text_file(resolve_config_resource_path(resolved_config_path, PREFIX + gpt_information["triple_generation_prompt"]))
        ontology_generation_prompt = read_text_file(resolve_config_resource_path(resolved_config_path, PREFIX + gpt_information["ontology_generation_prompt"]))
        domain_range_prompt = read_text_file(resolve_config_resource_path(resolved_config_path, PREFIX + gpt_information["domain_range_prompt"]))
        data_type_prompt = read_text_file(resolve_config_resource_path(resolved_config_path, PREFIX + gpt_information["data_type_prompt"]))
        axioms_prompt = read_text_file(resolve_config_resource_path(resolved_config_path, PREFIX + gpt_information["axioms_prompt"]))
        rdf_comments_prompt = read_text_file(resolve_config_resource_path(resolved_config_path, PREFIX + gpt_information["rdf_comments"]))
        individuals_prompt = read_text_file(resolve_config_resource_path(resolved_config_path, PREFIX + gpt_information["individuals_prompt"]))
        

        print("Generating triples in chunks...")
        gpt_information["user_query"] = f"{triple_generation_prompt}\n\nConcepts:{concepts}"
        all_triples = run_openai_chat_completion(gpt_information)


        triples_text = "\n".join(all_triples)

        print("Generating domain and range info...")
        gpt_information['user_query'] = f"{domain_range_prompt}\n\nConcepts:\n{concepts}"
        domain_range_text = run_openai_chat_completion(gpt_information)


        print("Generating data type info...")
        gpt_information['user_query'] = f"{data_type_prompt}\n\nTriples:\n{triples_text}"
        data_type_text = run_openai_chat_completion(gpt_information)
        print("Generating axioms...")
        gpt_information['user_query'] = f"{axioms_prompt}\n\nConcepts:\n{concepts}"
        axioms_text = run_openai_chat_completion(gpt_information)
        print("Generating RDF comments...")
        gpt_information['user_query'] = f"{rdf_comments_prompt}\n\nConcepts:\n{concepts}"
        rdf_comments_text = run_openai_chat_completion(gpt_information)

        print("Generating individuals...")
        gpt_information['user_query'] = f"{individuals_prompt}\n\nConcepts:\n{concepts}"
        individuals_text = run_openai_chat_completion(gpt_information)
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
        turtle_lines = run_openai_chat_completion(gpt_information)
        ontology_turtle = "\n".join(turtle_lines)

        return ontology_turtle

    except Exception as e:
        logging.exception(f"Error occurred while generating ontology: {e}")
        return None


def generate_local_chapter_ontology(chapter_title, chapter_concepts, config):
    chapter_concept_payload = {
        "chapter": chapter_title,
        "concepts": chapter_concepts,
    }
    return generate_full_turtle_ontology(chapter_concept_payload, config)


def generate_global_chapter_ontology(chapter_ontologies, config):
    try:
        print("Loading GPT information...")

        gpt_information, ontology_generation_prompt = load_gpt_prompt(
            config,
            "ontology_generation_prompt",
        )
        serialized_chapter_ontologies = json.dumps(
            chapter_ontologies,
            indent=2,
            ensure_ascii=False,
        )
        gpt_information["user_query"] = f"""
                Follow this: {ontology_generation_prompt}

                Merge the following chapter-level ontologies into one coherent ontology for the full regulation.
                Reconcile duplicate classes and properties across chapters, preserve consistent prefixes,
                and return only valid turtle content.

                Chapter ontologies: {serialized_chapter_ontologies}
                """
        merged_ontology_lines = run_openai_chat_completion(gpt_information)
        return "\n".join(merged_ontology_lines)

    except Exception as e:
        logging.exception(f"Error occurred while merging chapter ontologies: {e}")
        return None

def apply_mapping_borrows(turtle, mappings, config):
    try:
        print("Loading GPT information...")

        gpt_information, borrows_from_mappings_prompt = load_gpt_prompt(
            config,
            "borrows_from_prompt",
        )

        gpt_information['user_query'] = f"""
                                        Following this: {borrows_from_mappings_prompt}\n\n
                                        Ontology: {turtle}\n\n
                                        Mappings: {mappings}.\n\n
                                        Do not include another text, only return the turtle content of the ontology.
                                        """
        borrowed_turtle_lines = run_openai_chat_completion(gpt_information)
        borrowed_turtle = "\n".join(borrowed_turtle_lines)


        return borrowed_turtle

    except Exception as e:
        logging.exception(f"Error occurred while generating borrows from mappings: {e}")
        return None

def extract_concepts_with_gpt(questions, config):
    """
    Runs the GPT-based concept extraction.
    
    Args:
        questions (list): The list of competency questions.

        gpt_information (dict): Dictionary containing GPT role and model information.
    """
    try:
        gpt_information, concept_extraction_prompt = load_gpt_prompt(
            config,
            "concept_extraction_prompt",
        )

        print("Loading GPT information...")

        print(f"Generating concepts with base prompt: {concept_extraction_prompt}")
        gpt_information['user_query'] = f"{concept_extraction_prompt} Competency Questions: {questions}"
        extracted_concepts = run_openai_chat_completion(gpt_information)
        logging.info("GPT-based concept extraction completed.")
        return extracted_concepts
    except Exception as e:
        logging.error(f"Error occurred during GPT-based concept extraction: {e}")
        return None




def map_to_existing_ontologies_with_gpt(
    domain_entities,
    domain_properties,
    existing_classes,
    existing_properties,
    config
):
    try:
        gpt_config, base_prompt = load_gpt_prompt(
            config,
            "mapping_to_existing_ontologies_prompt",
        )

        gpt_config["user_query"] = f"""{base_prompt}. existing_properties: {existing_properties}, Domain properties: {domain_properties}. Do not include any thing other than the mapping results in your response. Return the mapping results in a JSON format."""
        property_mappings = run_openai_chat_completion(gpt_config)
        gpt_config["user_query"] = f"""{base_prompt}. existing_classes: {existing_classes}, Domain classes: {domain_entities}. Do not include any thing other than the mapping results in your response. Return the mapping results in a JSON format."""
        class_mappings = run_openai_chat_completion(gpt_config)
        

        return {
            "corresponding_classes": class_mappings,
            "corresponding_properties": property_mappings
        }

    except Exception as e:
        logging.error(
            f"Error occurred during GPT-based mapping to existing ontologies: {e}"
        )
        return None


def repair_turtle_syntax_with_gpt(data, config):
    try:
        gpt_information, turtle_syntax_fix_prompt = load_gpt_prompt(
            config,
            "turtle_syntax_fix_prompt",
        )
        gpt_information['user_query'] = f"{turtle_syntax_fix_prompt} Turtle content: {data}"
        repaired_turtle_lines = run_openai_chat_completion(gpt_information)
        return "\n".join(repaired_turtle_lines)
    except Exception as e:
        logging.error(f"Error occurred during fixing syntax errors in turtle: {e}")
        return data

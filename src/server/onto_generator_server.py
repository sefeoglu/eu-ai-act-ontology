"""Prototype ontology generator backed by a loaded DeclarativeMemory."""
import re
from typing import Dict, List

from memory.declarative_memory import DeclarativeMemory
from memory.procedural_memory import ProceduralMemory
from host.agents import domain_expert_agent
import json
from utils import json_formatted_mappings

CONCEPT_LIMIT = 500
CHAPTER_LIMIT = 7


class OntologyGenerator:
    """Performs ontology operations over a preloaded DeclarativeMemory graph."""

    def __init__(self, declarative_memory: DeclarativeMemory, procedural_memory: ProceduralMemory, output_path = None, run_config_path = None) -> None:
        self.declarative_memory = declarative_memory
        self.procedural_memory = procedural_memory
        self._ontology_output_path = output_path
        self._run_config_path = run_config_path


    def memory_generation(self) -> Dict[str, object]:
        """Return a structured representation of the loaded memory content."""
        return {
            "declarative": {
                "source": str(self.declarative_memory.source_path),
                "triple_count": self.declarative_memory.triple_count(),
            },
            "procedural":
             { "metadata": self.procedural_memory.get_metadata(),
              "document_content_retriever": self.procedural_memory.content_retriever(config=self._run_config_path)
              
            }
        }
    def extract_concepts(self) -> List[Dict[str, str]]:

        with open(self.procedural_memory.competency_questions_path) as f:
            competency_questions = json.load(f)
        
       
        regulation = competency_questions['regulation']
        citation = competency_questions['citation']
        source_url = competency_questions['source_url']
        scraped_at = competency_questions['scraped_at']
        competency_questions = competency_questions['competency_questions']
        all_concepts = []

        for index, item in enumerate(competency_questions):
            competency_questions_list = item['list_article_cqs']

            for per_chapter_questions in competency_questions_list:

                article = per_chapter_questions['article']
                article_url = per_chapter_questions['url']
                cqs = per_chapter_questions['competency_questions']

            
                concepts = domain_expert_agent.run_gpt_based_concept_extraction(cqs, self._run_config_path)

                concepts_str = "\n".join(concepts)
                concepts_str = concepts_str.replace("json\n", '').replace("`", "")
                concepts = json.loads(concepts_str)
                item = {
                    "article": article,
                    "url": article_url,
                    "concepts": concepts,
                    "regulation": regulation,
                    "citation": citation,
                    "source_url": source_url,
                    "scraped_at": scraped_at
                    
                }
        
                all_concepts.append(item)
            if index >= CHAPTER_LIMIT-1:  # Limit to first 7 articles for testing
                break
        print(f"path to save extracted concepts: {self.procedural_memory.concept_extraction_output_path}")

        with open(self.procedural_memory.concept_extraction_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_concepts, f, ensure_ascii=False, indent=4)

        
        print(f"Extracted concepts saved to {self.procedural_memory.concept_extraction_output_path}")
        
        self.all_concepts = all_concepts

        return all_concepts
    
    def borrow_concept_extraction(self) -> List[Dict[str, str]]:
        """Return the extracted concepts from the procedural memory."""
       
        self.generated_onto = open(self._ontology_output_path, 'r', encoding='utf-8').read()
        self.mappings = json.load(open(self.procedural_memory.mapping_output_path, 'r', encoding='utf-8'))
        
        ontology_content = domain_expert_agent.get_borrows_from_mappings(self.generated_onto, self.mappings, self._run_config_path)

        if ontology_content is None:
            raise ValueError(
                "Ontology generation failed: run_full_ttl_ontology() returned None"
            )

        if not isinstance(ontology_content, str):
            raise TypeError(
                f"Expected ontology_content to be str, got {type(ontology_content)}"
            )

        with open(self._ontology_output_path, "w", encoding="utf-8") as f:
            f.write(ontology_content)

        print(f"Generated ontology saved to {self._ontology_output_path}")

        print(f"Validation by RDFLib parsing:")
        message = self.validate_ontology()

        if message['status'] == 'success':

            print(message['message'])

        else:
            domain_expert_agent.fix_syntax_errors_in_turtle(ontology_content, self._run_config_path)
            while message['status'] != 'success':
                print(f"Ontology validation failed: {message['message']}")
                domain_expert_agent.fix_syntax_errors_in_turtle(ontology_content, self._run_config_path)
                message = self.validate_ontology()

        return (
            f"Generated ontology with {self.declarative_memory.triple_count()} triples "
            f"and procedural context from {self.procedural_memory.get_metadata()}"
        )



    def get_concept_extraction_output(self) -> List[Dict[str, str]]:
        """Return the extracted concepts from the procedural memory."""
        self.all_concepts = json.load(open(self.procedural_memory.concept_extraction_output_path, 'r', encoding='utf-8'))
        self.all_concept_cleaned = []
        entities = []
        properties = []
        for item in self.all_concepts:
            concepts_dict = item['concepts']
            if not isinstance(concepts_dict, dict):
                print(f"Unexpected format for concepts: {concepts_dict}")
                continue

            competency_questions = (
                concepts_dict.get("CompetencyQuestions")
                or concepts_dict.get("competencyQuestions")
                or concepts_dict.get("competencyQuestion")
                or concepts_dict.get("competencyQuestions")
            )
            # print(f" with concepts: {type(concepts)} and content: {concepts}")
            if not isinstance(competency_questions, list):
                print(f"Unexpected format for competency questions: {competency_questions}")
                continue
            for concept in competency_questions:
                if not isinstance(concept, dict):
                    print(f"Skipping invalid concept format: {concept}")
                    continue
                print(f"Processing concept: {concept}")
                entity =  concept.get('entities') or concept.get('Entities') or concept.get('entity') or concept.get('Entity') or []
                property = concept.get('properties') or concept.get('Properties') or concept.get('property') or concept.get('Property') or []
                entities.extend(entity)
                properties.extend(property)
               
                self.all_concept_cleaned.append({
                    "article": item['article'],
                    "url": item['url'],
                    "entities": entity,
                    "properties": property,
                    "regulation": item['regulation'],
                    "citation": item['citation'],
                    "source_url": item['source_url'],
                    "scraped_at": item['scraped_at']
                })
        return self.all_concept_cleaned, properties, entities


    def map_to_existing_ontologies(self) -> Dict[str, int]:
        """Return the top namespace occurrence counts in the loaded graph."""
        ontology_paths = self.procedural_memory.existing_ontologies
        mappings = []
        self.generated_onto = self.declarative_memory.load_from_path(self._ontology_output_path)
        domain_classes = self.generated_onto.get_classes_with_labels()
        domain_properties = self.generated_onto.get_properties_with_labels()

        for ontology_path in ontology_paths:
           
            onto = self.declarative_memory.load_from_path(ontology_path)
            classes = onto.get_classes_with_labels()
            properties = onto.get_properties_with_labels()
            
            mapping = domain_expert_agent.run_gpt_based_mapping_to_existing_ontologies(domain_classes, domain_properties, classes, properties, self._run_config_path)
        
            mappings.append({
                "corresponding_classes": mapping['corresponding_classes'],
                "corresponding_properties": mapping['corresponding_properties'],
            })

        with open(self.procedural_memory.mapping_output_path, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, ensure_ascii=False, indent=4)

        print(f"Mappings saved to {self.procedural_memory.mapping_output_path}")

        # clean the mappings for later use
        mappings = json_formatted_mappings(mappings)
        self.mappings = mappings

        return mappings



    def generate_ontology(self) -> str:
        self.all_concept_cleaned , _, _ = self.get_concept_extraction_output()
        ontology_content = domain_expert_agent.run_full_ttl_ontology(self.all_concept_cleaned[:CONCEPT_LIMIT])

        if ontology_content is None:
            raise ValueError(
                "Ontology generation failed: run_full_ttl_ontology() returned None"
            )

        if not isinstance(ontology_content, str):
            raise TypeError(
                f"Expected ontology_content to be str, got {type(ontology_content)}"
            )

        with open(self._ontology_output_path, "w", encoding="utf-8") as f:
            f.write(ontology_content)

        print(f"Generated ontology saved to {self._ontology_output_path}")

        print(f"Validation by RDFLib parsing:")
        message = self.validate_ontology()

        if message['status'] == 'success':

            print(message['message'])

        else:
            domain_expert_agent.fix_syntax_errors_in_turtle(ontology_content, self._run_config_path)
            while message['status'] != 'success':
                print(f"Ontology validation failed: {message['message']}")
                domain_expert_agent.fix_syntax_errors_in_turtle(ontology_content, self._run_config_path)
                message = self.validate_ontology()

        return (
            f"Generated ontology with {self.declarative_memory.triple_count()} triples "
            f"and procedural context from {self.procedural_memory.get_metadata()}"
        )
    
    def generate_competency_questions_by_article(self, articles: str) -> List[str]:
        list_article_cqs = []
        for article in articles:
                article_title = article['article']
                article_text = article['text']
                print(f"Generating competency questions for article: {article_title}")
                article_url = article['url']
                article_cqs = domain_expert_agent.cq_generation(article_text, self._run_config_path)
                
                article_info = {
                    "article": article_title,
                    "url": article_url,
                    "competency_questions": article_cqs
                }
                list_article_cqs.append(article_info)

        return list_article_cqs
    
    def generate_competency_question_by_chapter(self, chapters) -> List[str]:
        list_competency_questions = []
        for chapter in chapters:
            chapter_title = chapter['chapter']
            articles = chapter['articles']
            info_article = {
                "chapter": chapter_title,
                "list_article_cqs":self.generate_competency_questions_by_article(articles)
            } 
            list_competency_questions.append(info_article)
            # break
        return list_competency_questions

  

    def generate_competency_questions(self) -> List[str]:
        """Return a list of example competency questions for the loaded document."""
        print("Generating competency questions from procedural memory...")

        doc = self.procedural_memory.get_metadata()
        output_competency_questions_path = self.procedural_memory.competency_questions_path


        content = doc['document_content']
        chapters = content['chapters']
       
        regulation= content['regulation']
        citation = content['citation']
        source_url = content['source_url']
        scraped_at = content['scraped_at']

        competency_questions_all = {"competency_questions": self.generate_competency_question_by_chapter(chapters)}

        competency_questions_all['regulation'] = regulation
        competency_questions_all['citation'] = citation
        competency_questions_all['source_url'] = source_url
        competency_questions_all['scraped_at'] = scraped_at
        
        if output_competency_questions_path:
            with open(output_competency_questions_path, 'w', encoding='utf-8') as f:
                json.dump(competency_questions_all, f, ensure_ascii=False, indent=4)
            print(f"Competency questions saved to {output_competency_questions_path}")

        return competency_questions_all

    def generate_domain_memory(self) -> Dict[str, List[str]]:
        """Return a structured representation of the procedural memory content."""
        # this is a placeholder implementation; in a real system, this would involve more complex processing
        return {
            "procedural_chunks": [
                chunk.get("text", "") for chunk in self.procedural_memory.procedural_chunks[:5]
            ]
        }


    def validate_ontology(self) -> Dict[str, object]:
        """Run basic health checks over the loaded ontology."""
        try:
            onto = self.declarative_memory.load_from_path(self._ontology_output_path)
            return {
                "status": "success",
                "message": f"Ontology loaded successfully with {onto.triple_count()} triples.",
            }
        except Exception as e:

            
            return {"status": "error", "message": f"Failed to load ontology: {e}"}
        

        

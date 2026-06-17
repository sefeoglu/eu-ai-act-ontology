"""Prototype ontology generator backed by a loaded DeclarativeMemory."""
import json
from pathlib import Path
from typing import Dict, List, Tuple

from memory.declarative_memory import DeclarativeMemory
from memory.procedural_memory import ProceduralMemory
from host.agents import domain_expert_agent
from utils import format_mapping_output_as_json

CONCEPT_LIMIT = 500
CHAPTER_LIMIT = 7

class OntologyGenerator:
    """Performs ontology operations over a preloaded DeclarativeMemory graph."""
    """Args:
    declarative_memory: DeclarativeMemory
        A preloaded DeclarativeMemory instance containing the ontology graph.
    procedural_memory: ProceduralMemory
        A preloaded ProceduralMemory instance containing the procedural context and related metadata.
    output_path: Optional[str]
        Path to save the generated ontology. If None, a default path will be used.
    run_config_path: Optional[str]
        Path to the run configuration file (e.g., API configs). If None, a default path will be used.
    """
    def __init__(self, declarative_memory: DeclarativeMemory, procedural_memory: ProceduralMemory, output_path = None, run_config_path = None) -> None:
        self.declarative_memory = declarative_memory
        self.procedural_memory = procedural_memory
        self._ontology_output_path = output_path
        self._run_config_path = run_config_path

    def _write_ontology_output(self, ontology_content: str) -> None:
        with open(self._ontology_output_path, "w", encoding="utf-8") as output_file:
            output_file.write(ontology_content)

    def _validate_saved_ontology(self, ontology_content: str) -> None:
        print("Validation by RDFLib parsing:")
        validation_result = self.validate_ontology()

        if validation_result["status"] == "success":
            print(validation_result["message"])
            return

        while validation_result["status"] != "success":
            print(f"Ontology validation failed: {validation_result['message']}")
            ontology_content = domain_expert_agent.repair_turtle_syntax_with_gpt(
                ontology_content,
                self._run_config_path,
            )
            self._write_ontology_output(ontology_content)
            validation_result = self.validate_ontology()

    def _persist_and_validate_ontology(self, ontology_content: str) -> None:
        self._write_ontology_output(ontology_content)
        print(f"Generated ontology saved to {self._ontology_output_path}")
        self._validate_saved_ontology(ontology_content)


    def memory_generation(self) -> Dict[str, object]:
        """Return a structured representation of the loaded memory content."""

        return {
            "declarative": {
                "source": str(self.declarative_memory.source_path),
                "triple_count": self.declarative_memory.triple_count(),
            },
            "procedural": {
                "metadata": self.procedural_memory.get_metadata(),
                "document_content_retriever": self.procedural_memory.ensure_document_content_available(
                    config_path=self._run_config_path
                ),
            },
        }

    def extract_concepts(self) -> List[Dict[str, str]]:

        with open(self.procedural_memory.competency_questions_path, encoding="utf-8") as f:
            competency_question_report = json.load(f)
        
       
        regulation = competency_question_report['regulation']
        citation = competency_question_report['citation']
        source_url = competency_question_report['source_url']
        scraped_at = competency_question_report['scraped_at']
        chapter_competency_questions = competency_question_report['competency_questions']
        all_concepts = []

        for chapter_index, chapter_entry in enumerate(chapter_competency_questions):
            article_competency_questions = chapter_entry['list_article_cqs']

            for article_question_entry in article_competency_questions:

                article_title = article_question_entry['article']
                article_url = article_question_entry['url']
                article_questions = article_question_entry['competency_questions']

            
                extracted_concept_lines = domain_expert_agent.extract_concepts_with_gpt(article_questions, self._run_config_path)

                extracted_concepts_text = "\n".join(extracted_concept_lines)
                extracted_concepts_text = extracted_concepts_text.replace("json\n", '').replace("`", "")
                extracted_concepts = json.loads(extracted_concepts_text)
                concept_record = {
                    "article": article_title,
                    "url": article_url,
                    "concepts": extracted_concepts,
                    "regulation": regulation,
                    "citation": citation,
                    "source_url": source_url,
                    "scraped_at": scraped_at
                    
                }
        
                all_concepts.append(concept_record)
            if chapter_index >= CHAPTER_LIMIT - 1:  # Limit to first 7 articles for testing
                break
        print(f"path to save extracted concepts: {self.procedural_memory.concept_extraction_output_path}")

        with open(self.procedural_memory.concept_extraction_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_concepts, f, ensure_ascii=False, indent=4)

        
        print(f"Extracted concepts saved to {self.procedural_memory.concept_extraction_output_path}")
        
        self.all_concepts = all_concepts

        return all_concepts
    
    def borrow_concept_extraction(self) -> List[Dict[str, str]]:
        """Return the extracted concepts from the procedural memory."""
        ontology_output_path = Path(self._ontology_output_path)
        mapping_output_path = Path(self.procedural_memory.mapping_output_path)

        if not ontology_output_path.exists():
            self.generate_ontology()

        if not mapping_output_path.exists():
            self.map_to_existing_ontologies()

        with open(self._ontology_output_path, "r", encoding="utf-8") as ontology_file:
            self.generated_onto = ontology_file.read()
        with open(self.procedural_memory.mapping_output_path, "r", encoding="utf-8") as mapping_file:
            self.mappings = json.load(mapping_file)
        
        ontology_content = domain_expert_agent.apply_mapping_borrows(self.generated_onto, self.mappings, self._run_config_path)

        if ontology_content is None:
            raise ValueError(
                "Ontology generation failed: generate_full_turtle_ontology() returned None"
            )

        if not isinstance(ontology_content, str):
            raise TypeError(
                f"Expected ontology_content to be str, got {type(ontology_content)}"
            )

        self._persist_and_validate_ontology(ontology_content)

        return (
            f"Generated ontology with {self.declarative_memory.triple_count()} triples "
            f"and procedural context from {self.procedural_memory.get_metadata()}"
        )



    def load_concept_extraction_output(self) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        """Return the extracted concepts from the procedural memory."""
        with open(self.procedural_memory.concept_extraction_output_path, "r", encoding="utf-8") as concept_file:
            self.all_concepts = json.load(concept_file)
        self.all_concept_cleaned = []
        extracted_entities = []
        extracted_properties = []
        for concept_record in self.all_concepts:
            concepts_dict = concept_record['concepts']
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
            for competency_question_entry in competency_questions:
                if not isinstance(competency_question_entry, dict):
                    print(f"Skipping invalid concept format: {competency_question_entry}")
                    continue
                print(f"Processing concept: {competency_question_entry}")
                entity_names =  competency_question_entry.get('entities') or competency_question_entry.get('Entities') or competency_question_entry.get('entity') or competency_question_entry.get('Entity') or []
                property_names = competency_question_entry.get('properties') or competency_question_entry.get('Properties') or competency_question_entry.get('property') or competency_question_entry.get('Property') or []
                extracted_entities.extend(entity_names)
                extracted_properties.extend(property_names)
               
                self.all_concept_cleaned.append({
                    "article": concept_record['article'],
                    "url": concept_record['url'],
                    "entities": entity_names,
                    "properties": property_names,
                    "regulation": concept_record['regulation'],
                    "citation": concept_record['citation'],
                    "source_url": concept_record['source_url'],
                    "scraped_at": concept_record['scraped_at']
                })
        return self.all_concept_cleaned, extracted_properties, extracted_entities


    def map_to_existing_ontologies(self) -> Dict[str, int]:
        """Return the top namespace occurrence counts in the loaded graph."""

        ontology_paths = self.procedural_memory.existing_ontologies
        mappings = []
        self.generated_onto = self.declarative_memory.load_from_path(self._ontology_output_path)
        domain_classes = self.generated_onto.get_classes_with_labels()
        domain_properties = self.generated_onto.get_properties_with_labels()

        for ontology_path in ontology_paths:
           
            existing_ontology = self.declarative_memory.load_from_path(ontology_path)
            existing_classes = existing_ontology.get_classes_with_labels()
            existing_properties = existing_ontology.get_properties_with_labels()
            
            mapping_result = domain_expert_agent.map_to_existing_ontologies_with_gpt(domain_classes, domain_properties, existing_classes, existing_properties, self._run_config_path)
        
            mappings.append({
                "corresponding_classes": mapping_result['corresponding_classes'],
                "corresponding_properties": mapping_result['corresponding_properties'],
            })

        with open(self.procedural_memory.mapping_output_path, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, ensure_ascii=False, indent=4)

        print(f"Mappings saved to {self.procedural_memory.mapping_output_path}")

        # clean the mappings for later use
        mappings = format_mapping_output_as_json(mappings)
        self.mappings = mappings

        return mappings

    def generate_ontology(self) -> str:
        self.all_concept_cleaned, _, _ = self.load_concept_extraction_output()
        ontology_content = domain_expert_agent.generate_full_turtle_ontology(self.all_concept_cleaned[:CONCEPT_LIMIT], self._run_config_path)

        if ontology_content is None:
            raise ValueError(
                "Ontology generation failed: generate_full_turtle_ontology() returned None"
            )

        if not isinstance(ontology_content, str):
            raise TypeError(
                f"Expected ontology_content to be str, got {type(ontology_content)}"
            )

        self._persist_and_validate_ontology(ontology_content)

        return (
            f"Generated ontology with {self.declarative_memory.triple_count()} triples "
            f"and procedural context from {self.procedural_memory.get_metadata()}"
        )
    
    def generate_competency_questions_by_article(self, articles: str) -> List[str]:
        article_competency_questions = []
        for article in articles:
            article_title = article['article']
            article_text = article['text']
            print(f"Generating competency questions for article: {article_title}")
            article_url = article['url']
            generated_questions = domain_expert_agent.generate_competency_questions(article_text, self._run_config_path)

            article_info = {
                "article": article_title,
                "url": article_url,
                "competency_questions": generated_questions,
            }
            article_competency_questions.append(article_info)

        return article_competency_questions
    
    def generate_competency_questions_by_chapter(self, chapters) -> List[str]:
        chapter_competency_questions = []
        for chapter in chapters:
            chapter_title = chapter['chapter']
            chapter_articles = chapter['articles']
            chapter_info = {
                "chapter": chapter_title,
                "list_article_cqs": self.generate_competency_questions_by_article(chapter_articles)
            } 
            chapter_competency_questions.append(chapter_info)
            # break
        return chapter_competency_questions

  

    def generate_competency_questions(self) -> List[str]:
        """Return a list of example competency questions for the loaded document."""
        print("Generating competency questions from procedural memory...")

        document_metadata = self.procedural_memory.get_metadata()
        output_competency_questions_path = self.procedural_memory.competency_questions_path


        document_content = document_metadata['document_content']
        chapters = document_content['chapters']
       
        regulation = document_content['regulation']
        citation = document_content['citation']
        source_url = document_content['source_url']
        scraped_at = document_content['scraped_at']

        competency_question_report = {"competency_questions": self.generate_competency_questions_by_chapter(chapters)}

        competency_question_report['regulation'] = regulation
        competency_question_report['citation'] = citation
        competency_question_report['source_url'] = source_url
        competency_question_report['scraped_at'] = scraped_at
        
        if output_competency_questions_path:
            with open(output_competency_questions_path, 'w', encoding='utf-8') as f:
                json.dump(competency_question_report, f, ensure_ascii=False, indent=4)
            print(f"Competency questions saved to {output_competency_questions_path}")

        return competency_question_report

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
            loaded_ontology = self.declarative_memory.load_from_path(self._ontology_output_path)
            return {
                "status": "success",
                "message": f"Ontology loaded successfully with {loaded_ontology.triple_count()} triples.",
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to load ontology: {e}"}
"""Prototype ontology generator backed by a loaded DeclarativeMemory."""
import re
from typing import Dict, List

from memory.declarative_memory import DeclarativeMemory
from memory.procedural_memory import ProceduralMemory
from host.agents import domain_expert_agent
import json
import ast


class OntologyGenerator:
    """Performs ontology operations over a preloaded DeclarativeMemory graph."""

    def __init__(self, declarative_memory: DeclarativeMemory, procedural_memory: ProceduralMemory, output_path = None) -> None:
        self.declarative_memory = declarative_memory
        self.procedural_memory = procedural_memory
        self._ontology_output_path = output_path

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def memory_generation(self) -> Dict[str, object]:
        """Return a structured representation of the loaded memory content."""
        return {
            "declarative": {
                "source": str(self.declarative_memory.source_path),
                "triple_count": self.declarative_memory.triple_count(),
            },
            "procedural": self.procedural_memory.get_metadata(),
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

        for item in competency_questions:
            competency_questions_list = item['list_article_cqs']

            for per_chapter_questions in competency_questions_list:

                article = per_chapter_questions['article']
                article_url = per_chapter_questions['url']
                cqs = per_chapter_questions['competency_questions']

                print(f"Article: {article}, URL: {article_url}, Competency Questions: {cqs}")
                concepts = domain_expert_agent.run_gpt_based_concept_extraction(cqs)
                concepts_str = "\n".join(concepts)
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
                print(f"Extracted concepts for article '{article}': {concepts}")
                all_concepts.append(item)
        print(f"path to save extracted concepts: {self.procedural_memory.concept_extraction_output_path}")

        with open(self.procedural_memory.concept_extraction_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_concepts, f, ensure_ascii=False, indent=4)

        
        print(f"Extracted concepts saved to {self.procedural_memory.concept_extraction_output_path}")
        
        self.all_concepts = all_concepts

        return all_concepts
    




    def map_to_existing_ontologies(self) -> Dict[str, int]:
        """Return the top namespace occurrence counts in the loaded graph."""
        ontology_paths = self.procedural_memory.existing_ontologies
        all_classess = []
        all_properties = []
        for ontology_path in ontology_paths:
            print(f"Mapping to existing ontology: {ontology_path}")
            onto = self.declarative_memory.load_from_path(ontology_path)
            classes = onto.get_classes_with_labels()
            properties = onto.get_properties_with_labels()
            all_classess.append(classes)
            all_properties.append(properties)
        
        mappings = domain_expert_agent.run_gpt_based_mapping_to_existing_ontologies(self.all_concepts, all_classess, all_properties)
        with open(self.procedural_memory.mapping_output_path, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, ensure_ascii=False, indent=4)
        print(f"Mappings saved to {self.procedural_memory.mapping_output_path}")
        self.mappings = mappings
        return mappings



    def generate_ontology(self) -> str:
        # concepts = self.extract_concepts()
        # mappings = self.map_to_existing_ontologies()

        ontology_content = domain_expert_agent.run_full_ttl_ontology(self.all_concepts, self.mappings)

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
                print(f"Article text: {article_text[:200]}...")  # Print the first 200 characters for context
                article_url = article['url']
                article_cqs = domain_expert_agent.cq_generation(article_text)
                
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
            break
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

    def generate_owl_ttl(self) -> str:
        """Serialize the loaded graph as Turtle."""
        return self.declarative_memory.graph.serialize(format="turtle")

    def validate_ontology(self) -> Dict[str, object]:
        """Run basic health checks over the loaded ontology."""
        triple_count = self.declarative_memory.triple_count()
        return {
            "is_valid": triple_count > 0,
            "triple_count": triple_count,
            "source": str(self.declarative_memory.source_path),
        }


    def export_github_package(self) -> Dict[str, object]:
        """Return export metadata for future packaging integration."""
        validation = self.validate_ontology()
        return {
            "status": "ready" if validation["is_valid"] else "invalid",
            "triples": validation["triple_count"],
            "source": validation["source"],
        }
    

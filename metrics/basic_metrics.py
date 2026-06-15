import argparse
import csv
from collections import defaultdict, deque

from rdflib import Graph, RDF, RDFS, OWL


def calculate_metrics(input_file, rdf_format=None):
    g = Graph()
    g.parse(input_file, format=rdf_format)

    classes = set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class))
    object_properties = set(g.subjects(RDF.type, OWL.ObjectProperty))
    data_properties = set(g.subjects(RDF.type, OWL.DatatypeProperty))
    properties = (
        object_properties
        | data_properties
        | set(g.subjects(RDF.type, RDF.Property))
    )

    individuals = set()
    for s, _, o in g.triples((None, RDF.type, None)):
        if s not in classes and s not in properties:
            if o not in {
                OWL.Class,
                RDFS.Class,
                OWL.ObjectProperty,
                OWL.DatatypeProperty,
                RDF.Property,
            }:
                individuals.add(s)

    children = defaultdict(set)
    parents = defaultdict(set)

    for child, _, parent in g.triples((None, RDFS.subClassOf, None)):
        if child in classes and parent in classes:
            children[parent].add(child)
            parents[child].add(parent)

    roots = [c for c in classes if not parents[c]]

    def max_depth_from(root):
        queue = deque([(root, 0)])
        visited = set()
        max_depth = 0

        while queue:
            node, depth = queue.popleft()

            if node in visited:
                continue

            visited.add(node)
            max_depth = max(max_depth, depth)

            for child in children[node]:
                queue.append((child, depth + 1))

        return max_depth

    num_classes = len(classes)
    num_object_properties = len(object_properties)
    num_data_properties = len(data_properties)
    num_properties = len(properties)
    num_individuals = len(individuals)

    max_hierarchy_depth = max(
        (max_depth_from(root) for root in roots),
        default=0
    )

    subclass_counts = [len(children[c]) for c in classes]
    avg_breadth = (
        sum(subclass_counts) / num_classes
        if num_classes else 0
    )

    domain_property_counts = defaultdict(int)

    for prop in properties:
        for domain in g.objects(prop, RDFS.domain):
            if domain in classes:
                domain_property_counts[domain] += 1

    attribute_richness = (
        sum(domain_property_counts[c] for c in classes) / num_classes
        if num_classes else 0
    )

    relationship_density = (
        num_properties / num_classes
        if num_classes else 0
    )

    return [
        ["Number of classes", num_classes],
        ["Number of object properties", num_object_properties],
        ["Number of data properties", num_data_properties],
        ["Total number of properties", num_properties],
        ["Number of individuals", num_individuals],
        ["Maximum hierarchy depth", max_hierarchy_depth],
        ["Average hierarchy breadth", round(avg_breadth, 2)],
        ["Attribute richness", round(attribute_richness, 2)],
        ["Relationship density", round(relationship_density, 2)],
    ]


def export_to_csv(metrics, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        writer.writerows(metrics)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate structural metrics for an RDF/OWL ontology."
    )

    parser.add_argument(
        "input_file",
        help="Path to the ontology file, e.g. ontology.owl"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="ontology_structural_metrics.csv",
        help="Output CSV file name. Default: ontology_structural_metrics.csv"
    )

    parser.add_argument(
        "-f",
        "--format",
        default=None,
        help="RDF format, e.g. xml, turtle, n3, nt. Default: auto-detect"
    )

    args = parser.parse_args()

    metrics = calculate_metrics(args.input_file, args.format)
    export_to_csv(metrics, args.output)

    print(f"Structural metrics exported to: {args.output}")


if __name__ == "__main__":
    main()
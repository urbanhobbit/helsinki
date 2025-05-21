# Word-to-Knowledge Graph Extractor

## Overview
The Word-to-Knowledge Graph Extractor is a Streamlit-based web application designed to convert unstructured text from academic Word documents (`.docx`) into structured knowledge graphs. Its primary purpose is to facilitate the extraction of key entities (like concepts, materials, methods, data) and their relationships from research papers, theses, or other scholarly documents. By transforming text into a graph format, it aims to help researchers and analysts uncover connections, understand complex information landscapes, and enable further computational analysis. The application supports entity extraction, basic epistemic role classification, individual graph saving, merging multiple graphs, interactive visualization, and export into standard graph formats.

## Features
*   **Document Upload:** Accepts `.docx` files for processing.
*   **Entity & Relationship Extraction:** Utilizes spaCy for Named Entity Recognition (NER) to identify entities. Infers basic relationships based on entity co-occurrence within sentences. Assigns preliminary epistemic roles based on entity labels.
*   **Graph Management:** Allows users to save the extracted knowledge graph from a single document as a JSON file in the `graphs/` directory.
*   **Graph Merging & Visualization:** Merges all saved individual JSON graphs into a unified knowledge graph. Visualizes the merged graph interactively using PyVis, displaying nodes and edges.
*   **Export Options:** Enables users to export the merged knowledge graph in various formats:
    *   RDF (Turtle - `.ttl`)
    *   GraphML (`.graphml`)
    *   GML (`.gml`)

## Technology Stack
*   **Application Framework:** Streamlit
*   **Programming Language:** Python
*   **NLP Library:** spaCy (for entity extraction)
*   **Graph Visualization:** PyVis
*   **Graph Data Structures & Operations:** NetworkX

## Installation
To set up the application, follow these steps:

1.  **Clone the repository (if applicable) or ensure you have the `word_to_kg_app.py` file.**
2.  **Install the required Python packages:**
    ```bash
    pip install streamlit python-docx spacy pyvis networkx rdflib
    ```
3.  **Download the spaCy English language model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

## How to Run
Once the installation is complete, you can run the application using Streamlit:

Navigate to the project directory in your terminal and execute:
```bash
streamlit run word_to_kg_app.py
```
This will typically open the application in your default web browser.

## How It Works (Briefly)
1.  **Upload Document:** The user uploads a Word document (`.docx`) through the application interface.
2.  **Extract Entities & Relationships:** The system extracts text from the document. SpaCy's NLP models are then used to identify named entities (e.g., PERSON, ORG, GPE, custom types if trained). Basic relationships are inferred (e.g., entities appearing in the same sentence are considered related). Entities are assigned a preliminary role based on their spaCy label.
3.  **Save Individual Graph:** The extracted entities and relationships for the current document form a graph, which can be saved as a JSON file in the `graphs/` directory. This allows for processing multiple documents sequentially.
4.  **Merge & Visualize:** Users can choose to merge all previously saved JSON graphs into a single, comprehensive knowledge graph. This merged graph is then visualized interactively in the browser using PyVis.
5.  **Export Graph:** The merged knowledge graph can be exported into standard graph formats (RDF/TTL, GraphML, GML) for use in other graph analysis tools or for archival purposes.

## File Structure
```
project_folder/
├── word_to_kg_app.py      # Main Streamlit application script
├── graphs/                 # Directory for saved individual graph JSONs
├── merged_kg.html         # Default output name for PyVis visualization
├── merged_kg.ttl          # Default output name for RDF/Turtle export
├── merged_kg.graphml      # Default output name for GraphML export
├── merged_kg.gml          # Default output name for GML export
└── README.md              # This file
```
*Note: Exported file names (`merged_kg.*`) are defaults and will be created in the root directory when the respective export buttons are used.*

## License & Use
*   **License:** MIT License (or specify if different).
*   **Educational & Research Use:** This tool is primarily intended for educational and research purposes to demonstrate knowledge graph extraction from text.
*   **Accuracy:** The accuracy of entity extraction and relationship inference depends heavily on the underlying NLP models (spaCy's `en_core_web_sm` by default) and the heuristics used. For production or critical applications, fine-tuning models or more advanced extraction techniques would be necessary.
*   **No Guarantees:** The software is provided "as-is" without any warranties. Users should validate the extracted information for their specific needs.
*   **Customization:** Users are encouraged to customize and extend the tool, for example, by training custom spaCy models for specific academic domains or by implementing more sophisticated relationship extraction and role classification logic.

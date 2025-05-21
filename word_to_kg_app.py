import streamlit as st
import docx
import spacy
import networkx as nx
import json
import os
from networkx.readwrite import json_graph
from pyvis.network import Network as PyvisNetwork
import streamlit.components.v1 as components

# Attempt to load the spacy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error("spaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm' to download it.")
    st.stop()


def main():
    st.title("Word-to-Knowledge Graph Extractor")

    # Section 1: Document Upload
    st.header("1. Document Upload")
    uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])

    if 'current_graph' not in st.session_state:
        st.session_state.current_graph = None

    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        # Process the uploaded file
        doc = docx.Document(uploaded_file)
        full_text = "\n".join([para.text for para in doc.paragraphs])

        # Section 2: Entity & Relationship Extraction
        st.header("2. Entity & Relationship Extraction")
        st.subheader("Extracted Text:")
        st.text_area("Document Content", full_text, height=200)

        if st.button("Extract Entities & Relationships"):
            doc_spacy = nlp(full_text)
            entities = []
            for ent in doc_spacy.ents:
                entities.append({"text": ent.text, "label": ent.label_, "role": ent.label_}) # Basic role assignment

            st.subheader("Identified Entities:")
            if entities:
                for entity in entities:
                    st.write(f"- {entity['text']} ({entity['label']}) - Role: {entity['role']}")
            else:
                st.write("No entities found.")

            relationships = []
            for sent in doc_spacy.sents:
                sent_entities = [ent for ent in doc_spacy.ents if ent.sent == sent]
                for i in range(len(sent_entities) - 1):
                    entity1 = sent_entities[i]
                    entity2 = sent_entities[i+1]
                    # Check if entities are part of the globally identified entities to ensure consistency
                    e1_data = next((e for e in entities if e["text"] == entity1.text and e["label"] == entity1.label_), None)
                    e2_data = next((e for e in entities if e["text"] == entity2.text and e["label"] == entity2.label_), None)
                    if e1_data and e2_data: # Ensure entities were captured in the initial pass
                         relationships.append({"source": entity1.text, "target": entity2.text, "type": "related_to"})


            st.subheader("Inferred Relationships:")
            if relationships:
                for rel in relationships:
                    st.write(f"- {rel['source']} -> {rel['type']} -> {rel['target']}")
            else:
                st.write("No relationships inferred based on sequential appearance in sentences.")

            # Store extraction results in a NetworkX graph
            doc_graph = nx.DiGraph()
            for entity in entities:
                doc_graph.add_node(entity["text"], label=entity["label"], role=entity["role"])

            for rel in relationships:
                # Ensure nodes exist before adding edge, helpful if relationship inference is loose
                if doc_graph.has_node(rel["source"]) and doc_graph.has_node(rel["target"]):
                    doc_graph.add_edge(rel["source"], rel["target"], type=rel["type"])

            st.session_state.current_graph = doc_graph
            st.success("Entities and relationships extracted and graph created.")


    else:
        # Section 2: Entity & Relationship Extraction (Placeholder if no file is uploaded yet)
        st.header("2. Entity & Relationship Extraction")
        st.info("Upload a document to see extracted entities and relationships.")


    # Section 3: Graph Management
    st.header("3. Graph Management")

    if 'graph_filename' not in st.session_state:
        st.session_state.graph_filename = ""

    if st.session_state.current_graph and st.session_state.current_graph.nodes:
        st.subheader("Save Current Graph")
        st.session_state.graph_filename = st.text_input("Enter filename for graph (without .json):", value=st.session_state.graph_filename)
        if st.button("Save Graph"):
            if st.session_state.graph_filename:
                graph_data = json_graph.node_link_data(st.session_state.current_graph)
                filepath = os.path.join("graphs", f"{st.session_state.graph_filename}.json")
                with open(filepath, 'w') as f:
                    json.dump(graph_data, f, indent=4)
                st.success(f"Graph saved as `{filepath}`")
                st.session_state.current_graph = None # Clear current graph
                st.session_state.graph_filename = "" # Clear filename input
                # Rerun to update listed graphs and clear inputs correctly
                st.experimental_rerun()
            else:
                st.error("Please enter a filename.")
    else:
        st.info("No graph extracted yet or current graph is empty. Please upload a document and extract entities first.")

    st.subheader("Saved Graphs")
    if not os.path.exists("graphs"):
        os.makedirs("graphs") # Ensure directory exists
    
    saved_graph_files = [f for f in os.listdir("graphs") if f.endswith(".json")]
    if saved_graph_files:
        st.write("Available graph files:")
        for f_name in saved_graph_files:
            st.write(f"- {f_name}")
    else:
        st.write("No graphs saved yet.")


    # Section 4: Graph Merging & Visualization
    st.header("4. Graph Merging & Visualization")

    if 'merged_graph' not in st.session_state:
        st.session_state.merged_graph = None

    if st.button("Merge and Visualize All Graphs"):
        merged_graph = nx.DiGraph()
        graph_files_path = "graphs"
        
        if os.path.exists(graph_files_path) and any(f.endswith(".json") for f in os.listdir(graph_files_path)):
            for filename in os.listdir(graph_files_path):
                if filename.endswith(".json"):
                    filepath = os.path.join(graph_files_path, filename)
                    with open(filepath, 'r') as f:
                        graph_data = json.load(f)
                    doc_graph = json_graph.node_link_graph(graph_data)
                    merged_graph = nx.compose(merged_graph, doc_graph)
            
            if merged_graph.nodes:
                st.session_state.merged_graph = merged_graph
                st.success(f"Successfully merged {len(os.listdir(graph_files_path))} graph(s).")
            else:
                st.session_state.merged_graph = None # Ensure it's cleared if merging results in empty
                st.warning("Merging completed, but the resulting graph is empty.")

        else:
            st.session_state.merged_graph = None
            st.warning("No saved graphs found to merge in the 'graphs' directory.")

    if st.session_state.merged_graph and st.session_state.merged_graph.nodes:
        st.subheader("Merged Graph Visualization")
        
        # Create PyVis network
        nt = PyvisNetwork(notebook=True, cdn_resources='remote', height="750px", width="100%", directed=True)
        
        # Populate PyVis network from NetworkX graph
        # Customize node appearance based on 'role' or 'label' if available
        for node, data in st.session_state.merged_graph.nodes(data=True):
            title = f"Label: {data.get('label', 'N/A')}\nRole: {data.get('role', 'N/A')}"
            nt.add_node(node, label=str(node), title=title, group=data.get('label', 'default'))

        for source, target, data in st.session_state.merged_graph.edges(data=True):
            nt.add_edge(source, target, title=data.get('type', ''))

        # Save visualization as HTML
        vis_path = "merged_kg.html"
        nt.save_graph(vis_path)
        
        # Display HTML in Streamlit
        with open(vis_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
        components.html(html_content, height=800, width="100%", scrolling=True)
        st.success(f"Graphs merged and visualized. Visualization saved as `{vis_path}`.")
        st.markdown(f"[Download {vis_path}](./{vis_path})", unsafe_allow_html=True) # Simple download link
    elif st.session_state.merged_graph is not None and not st.session_state.merged_graph.nodes: # Explicit check for empty graph post-merge attempt
        st.info("Merged graph is empty. Nothing to visualize.")


    # Section 5: Export Options
    st.header("5. Export Options")

    if st.session_state.merged_graph and st.session_state.merged_graph.nodes:
        st.subheader("Export Merged Graph")

        # GraphML Export
        if st.button("Prepare GraphML Export (.graphml)"):
            try:
                graphml_path = "merged_kg.graphml"
                nx.write_graphml(st.session_state.merged_graph, graphml_path)
                st.success(f"Graph exported as `{graphml_path}`. Click below to download.")
                with open(graphml_path, "rb") as fp:
                    st.download_button(
                        label="Download GraphML",
                        data=fp,
                        file_name="merged_kg.graphml",
                        mime="application/graphml+xml"
                    )
            except Exception as e:
                st.error(f"Error exporting GraphML: {e}")

        # GML Export
        if st.button("Prepare GML Export (.gml)"):
            try:
                gml_path = "merged_kg.gml"
                # nx.generate_gml yields lines, so we write them to a file
                with open(gml_path, 'w', encoding='utf-8') as f:
                    for line in nx.generate_gml(st.session_state.merged_graph):
                        f.write(line + '\n')
                st.success(f"Graph exported as `{gml_path}`. Click below to download.")
                with open(gml_path, "rb") as fp: # Read as bytes for download button
                    st.download_button(
                        label="Download GML",
                        data=fp,
                        file_name="merged_kg.gml",
                        mime="application/gml+xml" # text/plain could also work
                    )
            except Exception as e:
                st.error(f"Error exporting GML: {e}")

        # RDF (.ttl) Export (Basic)
        if st.button("Prepare RDF/TTL Export (.ttl)"):
            try:
                ttl_path = "merged_kg.ttl"
                base_uri = "http://example.org/"
                
                # Sanitize node IDs for URI (simple replacement for spaces, could be more robust)
                def sanitize_uri_component(text):
                    return str(text).replace(" ", "_").replace("/", "_").replace("#", "_")

                with open(ttl_path, 'w', encoding='utf-8') as f:
                    # Define some prefixes (optional but good practice)
                    f.write("@prefix ex: <http://example.org/ontology#> .\n")
                    f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
                    f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")

                    for node, data in st.session_state.merged_graph.nodes(data=True):
                        node_id_sanitized = sanitize_uri_component(node)
                        node_uri = f"<{base_uri}{node_id_sanitized}>"
                        f.write(f"{node_uri} rdf:type ex:Entity .\n")
                        if data.get('label'):
                            f.write(f'{node_uri} rdfs:label "{data["label"]}" .\n') # Using rdfs:label
                        if data.get('role'):
                             f.write(f'{node_uri} ex:hasRole "{data["role"]}" .\n')
                        # Add other attributes as desired
                        f.write("\n")


                    for source, target, data in st.session_state.merged_graph.edges(data=True):
                        source_id_sanitized = sanitize_uri_component(source)
                        target_id_sanitized = sanitize_uri_component(target)
                        source_uri = f"<{base_uri}{source_id_sanitized}>"
                        target_uri = f"<{base_uri}{target_id_sanitized}>"
                        
                        relation_type = sanitize_uri_component(data.get('type', 'relatedTo'))
                        predicate_uri = f"ex:{relation_type}"
                        f.write(f"{source_uri} {predicate_uri} {target_uri} .\n\n")
                
                st.success(f"Graph exported as `{ttl_path}`. Click below to download.")
                with open(ttl_path, "rb") as fp:
                    st.download_button(
                        label="Download RDF/TTL",
                        data=fp,
                        file_name="merged_kg.ttl",
                        mime="text/turtle"
                    )
            except Exception as e:
                st.error(f"Error exporting RDF/TTL: {e}")
                
    else:
        st.info("No merged graph available to export. Please merge graphs first in Section 4.")

if __name__ == "__main__":
    main()

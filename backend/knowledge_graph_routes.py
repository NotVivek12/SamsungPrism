"""
Knowledge Graph API routes for Flask application.
This module provides endpoints for the hierarchical knowledge graph visualization.
"""

from flask import Blueprint, request, jsonify, send_file
import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for knowledge graph routes
knowledge_graph_bp = Blueprint('knowledge_graph', __name__)

# Path to the knowledge graph data file
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
KNOWLEDGE_GRAPH_FILE = os.path.join(DATA_DIR, 'knowledge-graph.example.json')

def load_knowledge_graph():
    """Load the knowledge graph from the JSON file."""
    try:
        if os.path.exists(KNOWLEDGE_GRAPH_FILE):
            with open(KNOWLEDGE_GRAPH_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Knowledge graph file not found: {KNOWLEDGE_GRAPH_FILE}")
            return get_default_knowledge_graph()
    except Exception as e:
        logger.error(f"Error loading knowledge graph: {e}")
        return get_default_knowledge_graph()

def get_default_knowledge_graph():
    """Return a minimal default knowledge graph if file is not found."""
    return {
        "@context": {
            "@vocab": "https://schema.org/",
            "kg": "https://example.org/knowledge-graph/"
        },
        "@graph": [
            {
                "id": "field-cloud-computing",
                "type": "Field",
                "label": "Cloud Computing",
                "description": "Distributed computing paradigm",
                "color": "#A855F7",
                "children": [
                    {"id": "subfield-saas", "type": "Subfield", "label": "SaaS"},
                    {"id": "subfield-paas", "type": "Subfield", "label": "PaaS"},
                    {"id": "subfield-iaas", "type": "Subfield", "label": "IaaS"}
                ]
            },
            {
                "id": "field-machine-learning",
                "type": "Field",
                "label": "Machine Learning",
                "description": "Study of algorithms that improve through experience",
                "color": "#3B82F6",
                "children": [
                    {"id": "subfield-nlp", "type": "Subfield", "label": "Natural Language Processing"},
                    {"id": "subfield-computer-vision", "type": "Subfield", "label": "Computer Vision"}
                ]
            }
        ],
        "relationships": [],
        "metadata": {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "description": "Default knowledge graph"
        }
    }

def build_hierarchical_graph_from_professors(professors_data):
    """
    Build a knowledge graph from professor domain expertise data.
    STRICTLY enforces hierarchy: Field -> Subfield -> Person
    Every Field MUST have at least one Subfield (no orphans).
    """
    import database
    
    # Get professors from database if not provided
    if not professors_data:
        try:
            professors_data = database.load_professors_data()
        except Exception as e:
            logger.error(f"Error loading professors: {e}")
            professors_data = []
    
    # Define field-to-subfield mappings for common research areas
    # This maps subfield keywords to their parent field
    SUBFIELD_TO_FIELD_MAP = {
        # Machine Learning & AI
        'machine learning': 'Artificial Intelligence',
        'deep learning': 'Artificial Intelligence',
        'neural network': 'Artificial Intelligence',
        'nlp': 'Artificial Intelligence',
        'natural language processing': 'Artificial Intelligence',
        'computer vision': 'Artificial Intelligence',
        'reinforcement learning': 'Artificial Intelligence',
        'artificial intelligence': 'Artificial Intelligence',
        'pattern recognition': 'Artificial Intelligence',
        'image processing': 'Artificial Intelligence',
        'speech recognition': 'Artificial Intelligence',
        'robotics': 'Artificial Intelligence',
        
        # Data Science
        'data mining': 'Data Science',
        'data analytics': 'Data Science',
        'big data': 'Data Science',
        'data science': 'Data Science',
        'statistics': 'Data Science',
        'predictive analytics': 'Data Science',
        
        # Cloud & Distributed Systems
        'cloud computing': 'Cloud & Distributed Systems',
        'distributed systems': 'Cloud & Distributed Systems',
        'edge computing': 'Cloud & Distributed Systems',
        'fog computing': 'Cloud & Distributed Systems',
        'virtualization': 'Cloud & Distributed Systems',
        'containerization': 'Cloud & Distributed Systems',
        'microservices': 'Cloud & Distributed Systems',
        
        # Cybersecurity
        'cybersecurity': 'Cybersecurity',
        'network security': 'Cybersecurity',
        'cryptography': 'Cybersecurity',
        'information security': 'Cybersecurity',
        'malware': 'Cybersecurity',
        'intrusion detection': 'Cybersecurity',
        'blockchain': 'Cybersecurity',
        
        # Networks & Communications
        'computer networks': 'Networks & Communications',
        'wireless networks': 'Networks & Communications',
        'sensor networks': 'Networks & Communications',
        'iot': 'Networks & Communications',
        'internet of things': 'Networks & Communications',
        '5g': 'Networks & Communications',
        'mobile computing': 'Networks & Communications',
        'adhoc networks': 'Networks & Communications',
        'vanet': 'Networks & Communications',
        'manet': 'Networks & Communications',
        'wsn': 'Networks & Communications',
        'wireless sensor': 'Networks & Communications',
        
        # Software Engineering
        'software engineering': 'Software Engineering',
        'software testing': 'Software Engineering',
        'agile': 'Software Engineering',
        'devops': 'Software Engineering',
        'software quality': 'Software Engineering',
        
        # Signal & Image Processing
        'signal processing': 'Signal & Image Processing',
        'image analysis': 'Signal & Image Processing',
        'digital signal': 'Signal & Image Processing',
        'bio-signal': 'Signal & Image Processing',
        'medical imaging': 'Signal & Image Processing',
        
        # Hardware & VLSI
        'vlsi': 'Hardware & Electronics',
        'embedded systems': 'Hardware & Electronics',
        'fpga': 'Hardware & Electronics',
        'circuit design': 'Hardware & Electronics',
        'semiconductor': 'Hardware & Electronics',
        'mems': 'Hardware & Electronics',
        'antenna': 'Hardware & Electronics',
        
        # Databases
        'database': 'Database Systems',
        'sql': 'Database Systems',
        'nosql': 'Database Systems',
        'data warehouse': 'Database Systems',
        
        # HCI & Graphics
        'human computer interaction': 'HCI & Visualization',
        'hci': 'HCI & Visualization',
        'computer graphics': 'HCI & Visualization',
        'visualization': 'HCI & Visualization',
        'virtual reality': 'HCI & Visualization',
        'augmented reality': 'HCI & Visualization',
        
        # Bioinformatics
        'bioinformatics': 'Computational Biology',
        'computational biology': 'Computational Biology',
        'genomics': 'Computational Biology',
        'healthcare': 'Computational Biology',
        
        # Optimization & Algorithms
        'optimization': 'Algorithms & Theory',
        'algorithm': 'Algorithms & Theory',
        'computational complexity': 'Algorithms & Theory',
        'graph theory': 'Algorithms & Theory',
    }
    
    # Field colors
    FIELD_COLORS = {
        'Artificial Intelligence': '#8B5CF6',
        'Data Science': '#10B981',
        'Cloud & Distributed Systems': '#A855F7',
        'Cybersecurity': '#6366F1',
        'Networks & Communications': '#84CC16',
        'Software Engineering': '#14B8A6',
        'Signal & Image Processing': '#F59E0B',
        'Hardware & Electronics': '#EC4899',
        'Database Systems': '#F97316',
        'HCI & Visualization': '#06B6D4',
        'Computational Biology': '#22C55E',
        'Algorithms & Theory': '#EAB308',
        'General Computing': '#6B7280',
    }
    
    def get_parent_field(domain_str):
        """Determine parent field for a domain/subfield"""
        domain_lower = domain_str.lower()
        for keyword, field in SUBFIELD_TO_FIELD_MAP.items():
            if keyword in domain_lower:
                return field
        return 'General Computing'  # Default field for unclassified domains
    
    # Build hierarchy: Field -> Subfield -> Professors
    # Structure: { field_name: { subfield_name: [professor_nodes] } }
    hierarchy = {}
    professor_nodes_map = {}
    
    for prof in professors_data:
        if not prof.get('domain_expertise'):
            continue
        
        prof_id = prof.get('id', '')
        
        # Create professor node (only once per professor)
        if prof_id not in professor_nodes_map:
            professor_nodes_map[prof_id] = {
                "id": f"person-{prof_id}",
                "type": "Person",
                "label": prof.get('name', 'Unknown'),
                "description": prof.get('research_interests', ''),
                "email": prof.get('email', ''),
                "college": prof.get('college', ''),
                "citations": prof.get('citations_count', 0),
                "hIndex": prof.get('h_index', 0),
                "i10Index": prof.get('i10_index', 0),
                "scholarUrl": prof.get('google_scholar_url', ''),
                "profilePicture": prof.get('profile_picture_url', '') or prof.get('scholar_profile_picture', ''),
                "profileLink": prof.get('profile_link', ''),
                "domainExpertise": prof.get('domain_expertise', ''),
                "phdThesis": prof.get('phd_thesis', ''),
                "professorData": prof
            }
        
        # Parse domain expertise - each domain becomes a subfield
        domains = [d.strip() for d in prof.get('domain_expertise', '').split(',') if d.strip()]
        
        for domain in domains:
            # Determine parent field
            parent_field = get_parent_field(domain)
            
            # Initialize field if not exists
            if parent_field not in hierarchy:
                hierarchy[parent_field] = {}
            
            # Initialize subfield if not exists
            if domain not in hierarchy[parent_field]:
                hierarchy[parent_field][domain] = {
                    "professor_ids": set(),
                    "professors": []
                }
            
            # Add professor to this subfield (avoid duplicates)
            if prof_id not in hierarchy[parent_field][domain]["professor_ids"]:
                hierarchy[parent_field][domain]["professor_ids"].add(prof_id)
                hierarchy[parent_field][domain]["professors"].append(professor_nodes_map[prof_id].copy())
    
    # Convert hierarchy to graph format: Field -> Subfield -> Person
    field_nodes = []
    
    for field_name, subfields in hierarchy.items():
        subfield_nodes = []
        total_professors = 0
        total_citations = 0
        
        for subfield_name, subfield_data in subfields.items():
            professors = subfield_data["professors"]
            if not professors:
                continue
                
            # Sort professors by citations
            professors.sort(key=lambda x: x.get("citations", 0), reverse=True)
            
            subfield_node = {
                "id": f"subfield-{subfield_name.lower().replace(' ', '-').replace('/', '-').replace('&', 'and')}",
                "type": "Subfield",
                "label": subfield_name,
                "children": professors,
                "professorCount": len(professors),
                "totalCitations": sum(p.get("citations", 0) for p in professors)
            }
            subfield_nodes.append(subfield_node)
            total_professors += len(professors)
            total_citations += subfield_node["totalCitations"]
        
        # IMPORTANT: Only add field if it has at least one subfield with professors
        if subfield_nodes:
            # Sort subfields by professor count
            subfield_nodes.sort(key=lambda x: x["professorCount"], reverse=True)
            
            field_node = {
                "id": f"field-{field_name.lower().replace(' ', '-').replace('&', 'and')}",
                "type": "Field",
                "label": field_name,
                "color": FIELD_COLORS.get(field_name, '#6B7280'),
                "children": subfield_nodes,
                "subfieldCount": len(subfield_nodes),
                "professorCount": total_professors,
                "totalCitations": total_citations
            }
            field_nodes.append(field_node)
    
    # Sort fields by professor count
    field_nodes.sort(key=lambda x: x["professorCount"], reverse=True)
    
    # Calculate totals
    total_subfields = sum(f["subfieldCount"] for f in field_nodes)
    
    return {
        "@context": {
            "@vocab": "https://schema.org/",
            "kg": "https://example.org/knowledge-graph/"
        },
        "@graph": field_nodes,
        "metadata": {
            "version": "2.0.0",
            "generated": datetime.now().isoformat(),
            "totalFields": len(field_nodes),
            "totalSubfields": total_subfields,
            "totalProfessors": len(professor_nodes_map),
            "hierarchy": "Field -> Subfield -> Person"
        }
    }


@knowledge_graph_bp.route('/api/knowledge-graph', methods=['GET'])
def get_knowledge_graph():
    """
    Get the hierarchical knowledge graph data.
    
    Query Parameters:
        - source: 'static' (default) or 'dynamic' (build from professor data)
        - include_professors: 'true' or 'false' (include professor nodes)
        - field: filter to specific field ID
        - expand: 'all', 'none', or comma-separated field IDs to expand
    
    Returns:
        JSON-LD formatted knowledge graph
    """
    try:
        source = request.args.get('source', 'static')
        include_professors = request.args.get('include_professors', 'false').lower() == 'true'
        field_filter = request.args.get('field', None)
        expand = request.args.get('expand', 'all')
        
        if source == 'dynamic':
            # Build graph from professor data
            import database
            professors = database.load_professors_data()
            graph_data = build_hierarchical_graph_from_professors(professors)
        else:
            # Load static knowledge graph
            graph_data = load_knowledge_graph()
            
            # Optionally merge with professor data
            if include_professors:
                try:
                    import database
                    professors = database.load_professors_data()
                    prof_graph = build_hierarchical_graph_from_professors(professors)
                    graph_data['professors'] = prof_graph.get('professors', [])
                    graph_data['professorFields'] = prof_graph.get('@graph', [])
                except Exception as e:
                    logger.warning(f"Could not include professor data: {e}")
        
        # Filter to specific field if requested
        if field_filter and '@graph' in graph_data:
            filtered = [node for node in graph_data['@graph'] if node.get('id') == field_filter]
            if filtered:
                graph_data['@graph'] = filtered
        
        # Handle expand parameter for lazy loading
        if expand == 'none' and '@graph' in graph_data:
            # Remove children for collapsed view
            for node in graph_data['@graph']:
                if 'children' in node:
                    node['hasChildren'] = len(node['children']) > 0
                    node['childCount'] = len(node['children'])
                    del node['children']
        elif expand != 'all' and '@graph' in graph_data:
            # Expand only specified fields
            expand_ids = set(expand.split(','))
            for node in graph_data['@graph']:
                if node.get('id') not in expand_ids and 'children' in node:
                    node['hasChildren'] = len(node['children']) > 0
                    node['childCount'] = len(node['children'])
                    del node['children']
        
        # Set cache headers for performance
        response = jsonify(graph_data)
        response.headers['Cache-Control'] = 's-maxage=60, stale-while-revalidate=300'
        return response
        
    except Exception as e:
        logger.error(f"Error in get_knowledge_graph: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to load knowledge graph'
        }), 500


@knowledge_graph_bp.route('/api/knowledge-graph/field/<field_id>', methods=['GET'])
def get_field_details(field_id):
    """
    Get details for a specific field including its children.
    Used for lazy loading of subtrees.
    """
    try:
        graph_data = load_knowledge_graph()
        
        def find_node(nodes, target_id):
            for node in nodes:
                if node.get('id') == target_id:
                    return node
                if 'children' in node:
                    found = find_node(node['children'], target_id)
                    if found:
                        return found
            return None
        
        node = find_node(graph_data.get('@graph', []), field_id)
        
        if node:
            return jsonify(node)
        else:
            return jsonify({'error': 'Field not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting field details: {e}")
        return jsonify({'error': str(e)}), 500


@knowledge_graph_bp.route('/api/knowledge-graph/search', methods=['GET'])
def search_knowledge_graph():
    """
    Search nodes in the knowledge graph.
    
    Query Parameters:
        - q: search query string
        - type: filter by node type (Field, Subfield, Skill, Person)
        - limit: max results (default 20)
    """
    try:
        query = request.args.get('q', '').lower()
        node_type = request.args.get('type', None)
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({'results': [], 'total': 0})
        
        graph_data = load_knowledge_graph()
        results = []
        
        def search_nodes(nodes, parent_id=None):
            for node in nodes:
                # Check type filter
                if node_type and node.get('type') != node_type:
                    if 'children' in node:
                        search_nodes(node['children'], node.get('id'))
                    continue
                
                # Search in label and description
                label = node.get('label', '').lower()
                description = node.get('description', '').lower()
                
                if query in label or query in description:
                    results.append({
                        'id': node.get('id'),
                        'type': node.get('type'),
                        'label': node.get('label'),
                        'description': node.get('description', ''),
                        'parentId': parent_id,
                        'hasChildren': 'children' in node and len(node['children']) > 0
                    })
                
                # Recurse into children
                if 'children' in node:
                    search_nodes(node['children'], node.get('id'))
        
        search_nodes(graph_data.get('@graph', []))
        
        # Sort by relevance (exact matches first, then partial)
        results.sort(key=lambda x: (
            0 if x['label'].lower() == query else 1,
            0 if x['label'].lower().startswith(query) else 1
        ))
        
        return jsonify({
            'results': results[:limit],
            'total': len(results),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error searching knowledge graph: {e}")
        return jsonify({'error': str(e)}), 500


@knowledge_graph_bp.route('/api/knowledge-graph/export', methods=['GET'])
def export_knowledge_graph():
    """
    Export the knowledge graph in various formats.
    
    Query Parameters:
        - format: 'json' (default), 'jsonld'
    """
    try:
        export_format = request.args.get('format', 'json')
        graph_data = load_knowledge_graph()
        
        if export_format == 'jsonld':
            # Return full JSON-LD with context
            response = jsonify(graph_data)
            response.headers['Content-Disposition'] = 'attachment; filename=knowledge-graph.jsonld'
            response.headers['Content-Type'] = 'application/ld+json'
            return response
        else:
            # Return plain JSON
            response = jsonify(graph_data)
            response.headers['Content-Disposition'] = 'attachment; filename=knowledge-graph.json'
            return response
            
    except Exception as e:
        logger.error(f"Error exporting knowledge graph: {e}")
        return jsonify({'error': str(e)}), 500


@knowledge_graph_bp.route('/api/knowledge-graph/stats', methods=['GET'])
def get_knowledge_graph_stats():
    """
    Get statistics about the knowledge graph.
    """
    try:
        graph_data = load_knowledge_graph()
        
        stats = {
            'totalFields': 0,
            'totalSubfields': 0,
            'totalSkills': 0,
            'maxDepth': 0,
            'totalRelationships': len(graph_data.get('relationships', []))
        }
        
        def count_nodes(nodes, depth=1):
            for node in nodes:
                node_type = node.get('type', '')
                if node_type == 'Field':
                    stats['totalFields'] += 1
                elif node_type == 'Subfield':
                    stats['totalSubfields'] += 1
                elif node_type == 'Skill':
                    stats['totalSkills'] += 1
                
                stats['maxDepth'] = max(stats['maxDepth'], depth)
                
                if 'children' in node:
                    count_nodes(node['children'], depth + 1)
        
        count_nodes(graph_data.get('@graph', []))
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting knowledge graph stats: {e}")
        return jsonify({'error': str(e)}), 500

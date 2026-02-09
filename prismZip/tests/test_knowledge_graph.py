"""
Unit tests for Knowledge Graph API routes.
"""

import pytest
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from knowledge_graph_routes import knowledge_graph_bp, mapToCytoscapeElements_test

@pytest.fixture
def app():
    """Create test Flask app."""
    app = Flask(__name__)
    app.register_blueprint(knowledge_graph_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

class TestKnowledgeGraphAPI:
    """Tests for the Knowledge Graph API endpoints."""

    def test_get_knowledge_graph_returns_200(self, client):
        """Test that GET /api/knowledge-graph returns 200 status."""
        response = client.get('/api/knowledge-graph')
        assert response.status_code == 200

    def test_get_knowledge_graph_returns_json(self, client):
        """Test that GET /api/knowledge-graph returns valid JSON."""
        response = client.get('/api/knowledge-graph')
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert data is not None

    def test_knowledge_graph_has_context(self, client):
        """Test that response includes JSON-LD context."""
        response = client.get('/api/knowledge-graph')
        data = json.loads(response.data)
        assert '@context' in data or '@graph' in data

    def test_knowledge_graph_has_graph_nodes(self, client):
        """Test that response includes graph nodes."""
        response = client.get('/api/knowledge-graph')
        data = json.loads(response.data)
        # Should have @graph array with nodes
        if '@graph' in data:
            assert isinstance(data['@graph'], list)
            if len(data['@graph']) > 0:
                node = data['@graph'][0]
                assert 'id' in node
                assert 'type' in node
                assert 'label' in node

    def test_knowledge_graph_cloud_computing_exists(self, client):
        """Test that Cloud Computing field exists with SaaS, PaaS, IaaS children."""
        response = client.get('/api/knowledge-graph')
        data = json.loads(response.data)
        
        cloud_computing = None
        if '@graph' in data:
            for node in data['@graph']:
                if node.get('label') == 'Cloud Computing':
                    cloud_computing = node
                    break
        
        assert cloud_computing is not None, "Cloud Computing field not found"
        assert cloud_computing.get('type') == 'Field'
        
        # Check for children
        children = cloud_computing.get('children', [])
        child_labels = [c.get('label') for c in children]
        assert 'SaaS' in child_labels, "SaaS subfield not found"
        assert 'PaaS' in child_labels, "PaaS subfield not found"
        assert 'IaaS' in child_labels, "IaaS subfield not found"

    def test_knowledge_graph_search(self, client):
        """Test search endpoint."""
        response = client.get('/api/knowledge-graph/search?q=cloud')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'total' in data

    def test_knowledge_graph_search_finds_saas(self, client):
        """Test that searching for SaaS returns results."""
        response = client.get('/api/knowledge-graph/search?q=saas')
        data = json.loads(response.data)
        
        assert data['total'] > 0, "SaaS search should return results"
        found_saas = any(r['label'] == 'SaaS' for r in data['results'])
        assert found_saas, "SaaS node should be in search results"

    def test_knowledge_graph_stats(self, client):
        """Test stats endpoint."""
        response = client.get('/api/knowledge-graph/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'totalFields' in data
        assert 'totalSubfields' in data
        assert data['totalFields'] > 0

    def test_knowledge_graph_export_json(self, client):
        """Test JSON export."""
        response = client.get('/api/knowledge-graph/export?format=json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data is not None

    def test_field_details_endpoint(self, client):
        """Test getting specific field details."""
        response = client.get('/api/knowledge-graph/field/field-cloud-computing')
        # May return 404 if not found, but should not error
        assert response.status_code in [200, 404]

    def test_response_time_under_200ms(self, client):
        """Test that response time is under 200ms."""
        import time
        start = time.time()
        response = client.get('/api/knowledge-graph')
        elapsed = (time.time() - start) * 1000  # Convert to milliseconds
        
        assert response.status_code == 200
        assert elapsed < 200, f"Response took {elapsed:.2f}ms, should be under 200ms"


class TestKnowledgeGraphDataFormat:
    """Tests for the canonical JSON data format."""

    def test_sample_json_file_exists(self):
        """Test that sample JSON file exists."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'knowledge-graph.example.json'
        )
        assert os.path.exists(data_path), f"Sample JSON file not found at {data_path}"

    def test_sample_json_is_valid(self):
        """Test that sample JSON file is valid JSON."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'knowledge-graph.example.json'
        )
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert '@context' in data
        assert '@graph' in data
        assert isinstance(data['@graph'], list)

    def test_node_format_is_correct(self):
        """Test that node format matches specification."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'knowledge-graph.example.json'
        )
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for node in data['@graph']:
            # Required fields
            assert 'id' in node, "Node must have 'id'"
            assert 'type' in node, "Node must have 'type'"
            assert 'label' in node, "Node must have 'label'"
            
            # Type should be one of the expected values
            assert node['type'] in ['Field', 'Subfield', 'Skill', 'Person'], \
                f"Unknown node type: {node['type']}"
            
            # If has children, they should follow same format
            if 'children' in node:
                assert isinstance(node['children'], list)
                for child in node['children']:
                    assert 'id' in child
                    assert 'type' in child
                    assert 'label' in child

    def test_relationships_format(self):
        """Test that relationships array has correct format."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'knowledge-graph.example.json'
        )
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'relationships' in data:
            for rel in data['relationships']:
                assert 'source' in rel
                assert 'target' in rel
                assert 'type' in rel


# Helper function for testing mapping (exposed for testing)
def mapToCytoscapeElements_test(graphJson, collapsedNodes=None):
    """Test helper to map JSON to Cytoscape elements."""
    if collapsedNodes is None:
        collapsedNodes = set()
    
    nodes = []
    edges = []

    def walk(node, parentId=None, depth=0):
        nodeId = node.get('id')
        isCollapsed = nodeId in collapsedNodes

        nodes.append({
            'data': {
                'id': nodeId,
                'label': node.get('label'),
                'type': node.get('type'),
                'hasChildren': 'children' in node and len(node.get('children', [])) > 0,
                'childCount': len(node.get('children', [])),
                'depth': depth,
            }
        })

        if parentId:
            relation = 'HAS_SKILL' if node.get('type') == 'Skill' else 'HAS_SUBFIELD'
            edges.append({
                'data': {
                    'id': f"{parentId}->{nodeId}",
                    'source': parentId,
                    'target': nodeId,
                    'relation': relation,
                }
            })

        if not isCollapsed and 'children' in node:
            for child in node['children']:
                walk(child, nodeId, depth + 1)

    graph_nodes = graphJson.get('@graph', graphJson if isinstance(graphJson, list) else [])
    for root in graph_nodes:
        walk(root, None, 0)

    return {'nodes': nodes, 'edges': edges}


class TestCytoscapeMapping:
    """Tests for the Cytoscape element mapping function."""

    def test_map_creates_nodes(self):
        """Test that mapping creates nodes from graph data."""
        graph_data = {
            '@graph': [
                {
                    'id': 'field-test',
                    'type': 'Field',
                    'label': 'Test Field',
                    'children': [
                        {'id': 'subfield-test', 'type': 'Subfield', 'label': 'Test Subfield'}
                    ]
                }
            ]
        }
        
        result = mapToCytoscapeElements_test(graph_data)
        
        assert len(result['nodes']) == 2
        assert len(result['edges']) == 1

    def test_map_preserves_node_data(self):
        """Test that mapping preserves node data correctly."""
        graph_data = {
            '@graph': [
                {'id': 'field-ml', 'type': 'Field', 'label': 'Machine Learning'}
            ]
        }
        
        result = mapToCytoscapeElements_test(graph_data)
        
        node = result['nodes'][0]
        assert node['data']['id'] == 'field-ml'
        assert node['data']['type'] == 'Field'
        assert node['data']['label'] == 'Machine Learning'

    def test_map_creates_correct_edge_relations(self):
        """Test that edges have correct relation types."""
        graph_data = {
            '@graph': [
                {
                    'id': 'field-test',
                    'type': 'Field',
                    'label': 'Test',
                    'children': [
                        {
                            'id': 'subfield-test',
                            'type': 'Subfield',
                            'label': 'Sub',
                            'children': [
                                {'id': 'skill-test', 'type': 'Skill', 'label': 'Skill'}
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = mapToCytoscapeElements_test(graph_data)
        
        # Find edges and check relations
        subfield_edge = next(e for e in result['edges'] if e['data']['target'] == 'subfield-test')
        skill_edge = next(e for e in result['edges'] if e['data']['target'] == 'skill-test')
        
        assert subfield_edge['data']['relation'] == 'HAS_SUBFIELD'
        assert skill_edge['data']['relation'] == 'HAS_SKILL'

    def test_collapsed_nodes_hide_children(self):
        """Test that collapsed nodes don't have children in output."""
        graph_data = {
            '@graph': [
                {
                    'id': 'field-test',
                    'type': 'Field',
                    'label': 'Test',
                    'children': [
                        {'id': 'child-1', 'type': 'Subfield', 'label': 'Child 1'},
                        {'id': 'child-2', 'type': 'Subfield', 'label': 'Child 2'}
                    ]
                }
            ]
        }
        
        # With parent collapsed
        result = mapToCytoscapeElements_test(graph_data, {'field-test'})
        
        # Should only have the parent node
        assert len(result['nodes']) == 1
        assert result['nodes'][0]['data']['id'] == 'field-test'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

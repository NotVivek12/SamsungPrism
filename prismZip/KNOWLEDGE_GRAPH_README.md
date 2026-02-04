# Hierarchical Knowledge Graph

A production-ready knowledge graph visualization for the Statistics page, showing structured relationships between research domains, subfields, skills, and professors.

## Overview

The Knowledge Graph provides an interactive, hierarchical visualization of academic research domains with proper parent-child relationships. It replaces the previous flat expertise visualization with a semantically correct structure.

### Features

- **Hierarchical Structure**: Fields → Subfields → Skills → People
- **Multiple Layout Options**: Hierarchical (dagre), Breadth-first, Force-directed
- **Interactive Search**: Real-time node search with highlighting
- **Expand/Collapse**: Double-click nodes to show/hide subtrees
- **Node Details Panel**: Click nodes to see metadata, descriptions, and links
- **Export**: PNG/SVG images and JSON-LD data export
- **Keyboard Accessible**: Full keyboard navigation support
- **Mobile Responsive**: Condensed controls for smaller screens

## Data Format

The knowledge graph uses JSON-LD format for semantic web compatibility.

### Canonical Node Format

```json
{
  "id": "field-cloud-computing",
  "type": "Field",
  "label": "Cloud Computing",
  "description": "Distributed computing paradigm",
  "color": "#A855F7",
  "children": [
    {
      "id": "subfield-saas",
      "type": "Subfield",
      "label": "SaaS",
      "children": [
        {
          "id": "skill-multitenant",
          "type": "Skill",
          "label": "Multi-tenant Architecture"
        }
      ]
    }
  ]
}
```

### Node Types

| Type | Description | Visual |
|------|-------------|--------|
| `Field` | Top-level research domain | Large purple rounded rectangle |
| `Subfield` | Sub-category of a field | Medium blue rounded rectangle |
| `Skill` | Specific technique or technology | Small green circle |
| `Person` | Professor or researcher | Small amber circle |

### Relationship Types

| Type | Description |
|------|-------------|
| `HAS_SUBFIELD` | Parent field contains child subfield |
| `HAS_SKILL` | Subfield includes a skill |
| `ASSOCIATED_WITH` | Person is associated with a field/skill |
| `RELATED_TO` | Cross-reference between fields (dashed line) |

## API Endpoints

### GET /api/knowledge-graph

Returns the full knowledge graph in JSON-LD format.

**Query Parameters:**
- `source`: `static` (default) or `dynamic` (build from professor data)
- `include_professors`: `true` or `false` (include professor nodes)
- `field`: Filter to specific field ID
- `expand`: `all`, `none`, or comma-separated field IDs

**Response:**
```json
{
  "@context": {...},
  "@graph": [...],
  "relationships": [...],
  "metadata": {...}
}
```

### GET /api/knowledge-graph/search

Search nodes by label or description.

**Query Parameters:**
- `q`: Search query (required)
- `type`: Filter by node type
- `limit`: Max results (default: 20)

### GET /api/knowledge-graph/field/{field_id}

Get details for a specific field (lazy loading).

### GET /api/knowledge-graph/export

Export graph data.

**Query Parameters:**
- `format`: `json` or `jsonld`

### GET /api/knowledge-graph/stats

Get graph statistics.

## Adding/Modifying Nodes

### Option 1: Edit Static JSON

1. Open `prismZip/data/knowledge-graph.example.json`
2. Add nodes following the canonical format
3. Restart the server

### Option 2: Dynamic Generation

The API can build a graph dynamically from professor data:

```
GET /api/knowledge-graph?source=dynamic
```

This creates Field nodes from professor `domain_expertise` fields and links professors to their expertise areas.

## Development

### Frontend

The main component is located at:
```
professors/src/components/StatisticsKnowledgeGraph.jsx
```

**Dependencies:**
- `cytoscape`: Graph visualization library
- `react-cytoscapejs`: React wrapper
- `cytoscape-dagre`: Hierarchical layout plugin

**Key Functions:**
- `mapToCytoscapeElements()`: Converts JSON-LD to Cytoscape format
- `handleNodeClick()`: Opens detail panel
- `handleNodeDoubleClick()`: Expand/collapse subtrees

### Backend

API routes are in:
```
prismZip/knowledge_graph_routes.py
```

Registered in `app.py` as `knowledge_graph_bp`.

### Running Tests

**Backend:**
```bash
cd prismZip
pytest tests/test_knowledge_graph.py -v
```

**Frontend:**
```bash
cd professors
npm test -- --testPathPattern=StatisticsKnowledgeGraph
```

## Performance Considerations

### For Large Graphs (>2000 nodes)

1. **Lazy Loading**: Use `expand=none` to load collapsed initially
2. **Server-side Aggregation**: Filter by field or type
3. **Client-side Clustering**: Group nodes by parent field

### Debouncing

Search and controls are debounced at 300ms to prevent excessive re-renders.

## Future Improvements

- [ ] Neo4j integration for persistent graph storage
- [ ] Admin UI for editing nodes
- [ ] RDF/Turtle export for semantic web
- [ ] Server-side clustering for very large graphs
- [ ] Collaborative editing with real-time sync
- [ ] Graph analytics (centrality, communities)

## Screenshots

### Hierarchical View
The default view shows Fields at the top level, with Subfields and Skills as children.

### Search & Highlight
Type in the search box to find and highlight matching nodes.

### Node Details
Click any node to open the side panel with metadata.

### Layout Options
Switch between hierarchical, breadth-first, and force-directed layouts.

## Troubleshooting

### Graph not loading
1. Check that the Flask server is running on port 5000
2. Verify CORS is enabled
3. Check browser console for errors

### Layout looks wrong
1. Try resetting the view (Reset button)
2. Switch layout types
3. Zoom out to see full graph

### Performance issues
1. Collapse unused subtrees
2. Use search to focus on specific areas
3. Consider filtering by field

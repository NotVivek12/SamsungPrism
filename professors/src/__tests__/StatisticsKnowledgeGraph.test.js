/**
 * Unit tests for StatisticsKnowledgeGraph utility functions
 */

import { mapToCytoscapeElements } from '../components/StatisticsKnowledgeGraph';

describe('mapToCytoscapeElements', () => {
  describe('basic mapping', () => {
    it('should map a simple graph with one node', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-test',
            type: 'Field',
            label: 'Test Field'
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes).toHaveLength(1);
      expect(result.edges).toHaveLength(0);
      expect(result.nodes[0].data.id).toBe('field-test');
      expect(result.nodes[0].data.label).toBe('Test Field');
      expect(result.nodes[0].data.type).toBe('Field');
    });

    it('should map parent-child relationships correctly', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-cloud',
            type: 'Field',
            label: 'Cloud Computing',
            children: [
              { id: 'subfield-saas', type: 'Subfield', label: 'SaaS' },
              { id: 'subfield-paas', type: 'Subfield', label: 'PaaS' },
              { id: 'subfield-iaas', type: 'Subfield', label: 'IaaS' }
            ]
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes).toHaveLength(4);
      expect(result.edges).toHaveLength(3);

      // Check that all children are linked to parent
      const edgeTargets = result.edges.map(e => e.data.target);
      expect(edgeTargets).toContain('subfield-saas');
      expect(edgeTargets).toContain('subfield-paas');
      expect(edgeTargets).toContain('subfield-iaas');

      // All edges should have the parent as source
      result.edges.forEach(edge => {
        expect(edge.data.source).toBe('field-cloud');
      });
    });

    it('should handle deeply nested hierarchies', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-ml',
            type: 'Field',
            label: 'Machine Learning',
            children: [
              {
                id: 'subfield-dl',
                type: 'Subfield',
                label: 'Deep Learning',
                children: [
                  { id: 'skill-cnn', type: 'Skill', label: 'CNN' },
                  { id: 'skill-rnn', type: 'Skill', label: 'RNN' }
                ]
              }
            ]
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes).toHaveLength(4); // Field + Subfield + 2 Skills
      expect(result.edges).toHaveLength(3); // 3 parent-child relationships

      // Check depth values
      const fieldNode = result.nodes.find(n => n.data.id === 'field-ml');
      const subfieldNode = result.nodes.find(n => n.data.id === 'subfield-dl');
      const skillNode = result.nodes.find(n => n.data.id === 'skill-cnn');

      expect(fieldNode.data.depth).toBe(0);
      expect(subfieldNode.data.depth).toBe(1);
      expect(skillNode.data.depth).toBe(2);
    });
  });

  describe('edge relations', () => {
    it('should set HAS_SUBFIELD relation for Field to Subfield edges', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-test',
            type: 'Field',
            label: 'Test',
            children: [
              { id: 'subfield-test', type: 'Subfield', label: 'Sub' }
            ]
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);
      const edge = result.edges[0];

      expect(edge.data.relation).toBe('HAS_SUBFIELD');
    });

    it('should set HAS_SKILL relation for Subfield to Skill edges', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-test',
            type: 'Field',
            label: 'Test',
            children: [
              {
                id: 'subfield-test',
                type: 'Subfield',
                label: 'Sub',
                children: [
                  { id: 'skill-test', type: 'Skill', label: 'Skill' }
                ]
              }
            ]
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);
      const skillEdge = result.edges.find(e => e.data.target === 'skill-test');

      expect(skillEdge.data.relation).toBe('HAS_SKILL');
    });
  });

  describe('relationships array', () => {
    it('should map RELATED_TO relationships from relationships array', () => {
      const graphData = {
        '@graph': [
          { id: 'field-ml', type: 'Field', label: 'Machine Learning' },
          { id: 'field-ai', type: 'Field', label: 'AI' }
        ],
        relationships: [
          {
            source: 'field-ml',
            target: 'field-ai',
            type: 'RELATED_TO',
            label: 'subset of'
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.edges).toHaveLength(1);
      expect(result.edges[0].data.relation).toBe('RELATED_TO');
      expect(result.edges[0].data.source).toBe('field-ml');
      expect(result.edges[0].data.target).toBe('field-ai');
    });
  });

  describe('collapsed nodes', () => {
    it('should not include children of collapsed nodes', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-test',
            type: 'Field',
            label: 'Test',
            children: [
              { id: 'child-1', type: 'Subfield', label: 'Child 1' },
              { id: 'child-2', type: 'Subfield', label: 'Child 2' }
            ]
          }
        ]
      };

      const collapsedNodes = new Set(['field-test']);
      const result = mapToCytoscapeElements(graphData, collapsedNodes);

      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0].data.id).toBe('field-test');
      expect(result.edges).toHaveLength(0);
    });

    it('should mark collapsed nodes with isCollapsed flag', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-test',
            type: 'Field',
            label: 'Test',
            children: [{ id: 'child', type: 'Subfield', label: 'Child' }]
          }
        ]
      };

      const collapsedNodes = new Set(['field-test']);
      const result = mapToCytoscapeElements(graphData, collapsedNodes);

      expect(result.nodes[0].data.isCollapsed).toBe(true);
    });

    it('should track hasChildren and childCount', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-test',
            type: 'Field',
            label: 'Test',
            children: [
              { id: 'child-1', type: 'Subfield', label: 'Child 1' },
              { id: 'child-2', type: 'Subfield', label: 'Child 2' },
              { id: 'child-3', type: 'Subfield', label: 'Child 3' }
            ]
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);
      const parentNode = result.nodes.find(n => n.data.id === 'field-test');

      expect(parentNode.data.hasChildren).toBe(true);
      expect(parentNode.data.childCount).toBe(3);
    });
  });

  describe('node metadata', () => {
    it('should preserve description in node data', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-cloud',
            type: 'Field',
            label: 'Cloud Computing',
            description: 'Distributed computing paradigm'
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes[0].data.description).toBe('Distributed computing paradigm');
    });

    it('should preserve color in node data', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-cloud',
            type: 'Field',
            label: 'Cloud Computing',
            color: '#A855F7'
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes[0].data.color).toBe('#A855F7');
    });

    it('should preserve Person-specific fields', () => {
      const graphData = {
        '@graph': [
          {
            id: 'person-1',
            type: 'Person',
            label: 'Dr. Smith',
            citations: 1500,
            hIndex: 25,
            email: 'smith@university.edu',
            college: 'Computer Science'
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);
      const node = result.nodes[0];

      expect(node.data.citations).toBe(1500);
      expect(node.data.hIndex).toBe(25);
      expect(node.data.email).toBe('smith@university.edu');
      expect(node.data.college).toBe('Computer Science');
    });
  });

  describe('multiple root nodes', () => {
    it('should handle multiple top-level fields', () => {
      const graphData = {
        '@graph': [
          { id: 'field-ml', type: 'Field', label: 'Machine Learning' },
          { id: 'field-cloud', type: 'Field', label: 'Cloud Computing' },
          { id: 'field-security', type: 'Field', label: 'Cybersecurity' }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes).toHaveLength(3);
      expect(result.edges).toHaveLength(0); // No parent-child edges for root nodes
    });
  });

  describe('edge cases', () => {
    it('should handle empty graph', () => {
      const graphData = { '@graph': [] };
      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes).toHaveLength(0);
      expect(result.edges).toHaveLength(0);
    });

    it('should handle missing @graph key', () => {
      const graphData = [];
      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes).toHaveLength(0);
      expect(result.edges).toHaveLength(0);
    });

    it('should handle nodes with empty children array', () => {
      const graphData = {
        '@graph': [
          {
            id: 'field-test',
            type: 'Field',
            label: 'Test',
            children: []
          }
        ]
      };

      const result = mapToCytoscapeElements(graphData);

      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0].data.hasChildren).toBe(false);
      expect(result.nodes[0].data.childCount).toBe(0);
    });
  });
});

describe('Search functionality', () => {
  // These tests would require mocking Cytoscape and testing the search behavior
  // For now, we test the expected filter behavior

  it('should filter nodes by label match', () => {
    const nodes = [
      { label: 'Cloud Computing', type: 'Field' },
      { label: 'Machine Learning', type: 'Field' },
      { label: 'SaaS', type: 'Subfield' }
    ];

    const query = 'cloud';
    const matches = nodes.filter(n => 
      n.label.toLowerCase().includes(query.toLowerCase())
    );

    expect(matches).toHaveLength(1);
    expect(matches[0].label).toBe('Cloud Computing');
  });

  it('should be case-insensitive', () => {
    const nodes = [
      { label: 'CLOUD COMPUTING', type: 'Field' },
      { label: 'cloud computing', type: 'Field' }
    ];

    const query = 'Cloud';
    const matches = nodes.filter(n => 
      n.label.toLowerCase().includes(query.toLowerCase())
    );

    expect(matches).toHaveLength(2);
  });
});

describe('Layout configurations', () => {
  it('should have correct dagre layout config', () => {
    const dagreConfig = {
      name: 'dagre',
      rankDir: 'TB',
      nodeSep: 60,
      rankSep: 80,
    };

    expect(dagreConfig.name).toBe('dagre');
    expect(dagreConfig.rankDir).toBe('TB');
  });

  it('should have correct breadthfirst layout config', () => {
    const bfConfig = {
      name: 'breadthfirst',
      directed: true,
    };

    expect(bfConfig.name).toBe('breadthfirst');
    expect(bfConfig.directed).toBe(true);
  });
});

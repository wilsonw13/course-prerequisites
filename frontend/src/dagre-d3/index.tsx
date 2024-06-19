import { useState, useEffect, useRef } from 'react'
import { RecursivePartial, NodeOptions, EdgeOptions, DagreReact } from 'dagre-reactjs'
import { UncontrolledReactSVGPanZoom } from 'react-svg-pan-zoom'
import AutoSizer from 'react-virtualized-auto-sizer'

type graphT = {
  nodes: Array<RecursivePartial<NodeOptions>>;
  edges: Array<RecursivePartial<EdgeOptions>>;
};

export default function DagreMain () {
//   const g = new graphlib.Graph() // Create a new directed graph
//   g.setGraph({}) // Set an object for the graph label
//   g.setDefaultEdgeLabel(function () { return {} }) // Default to assigning a new object as a label for each new edge.
//
//   // Add nodes to the graph. The first argument is the node id. The second is
//   // metadata about the node. In this case we're going to add labels to each of
//   // our nodes.
//   g.setNode('kspacey', { label: 'Kevin Spacey', width: 144, height: 100 })
//   g.setNode('swilliams', { label: 'Saul Williams', width: 160, height: 100 })
//   g.setNode('bpitt', { label: 'Brad Pitt', width: 108, height: 100 })
//   g.setNode('hford', { label: 'Harrison Ford', width: 168, height: 100 })
//   g.setNode('lwilson', { label: 'Luke Wilson', width: 144, height: 100 })
//   g.setNode('kbacon', { label: 'Kevin Bacon', width: 121, height: 100 })
//
//   g.nodes().forEach((v) => {
//     const node = g.node(v)
//     // Round the corners of the nodes
//     node.rx = node.ry = 5
//   })
//
//   // Add edges to the graph.
//   g.setEdge('kspacey', 'swilliams')
//   g.setEdge('swilliams', 'kbacon')
//   g.setEdge('bpitt', 'kbacon')
//   g.setEdge('hford', 'lwilson')
//   g.setEdge('lwilson', 'kbacon')
//
  //   // perform layout for all the nodes/edges of the graph
  //   layout(g)
  //
  //   g.nodes().forEach(function (v) {
  //     console.log('Node ' + v + ': ' + JSON.stringify(g.node(v)))
  //   })
  //   g.edges().forEach(function (e) {
  //     console.log('Edge ' + e.v + ' -> ' + e.w + ': ' + JSON.stringify(g.edge(e)))
  //   })

  const basic1_graph: graphT = {
    nodes: [
      {
        id: '0',
        label: 'Project Start'
      },
      {
        id: '1',
        label: 'Project End'
      }
    ],
    edges: [
      {
        from: '0',
        to: '1'
      }
    ]
  }

  const basic2_graph: graphT = {
    nodes: [
      {
        id: '0',
        label: 'TOP'
      },
      {
        id: '1',
        label: 'S'
      },
      {
        id: '2',
        label: 'NP'
      },
      {
        id: '3',
        label: 'DT'
      },
      {
        id: '4',
        label: 'This',
        styles: {
          shape: {
            className: 'basic2end'
          }
        }
      },
      {
        id: '5',
        label: 'VP'
      },
      {
        id: '6',
        label: 'VBZ'
      },
      {
        id: '7',
        label: 'is',
        styles: {
          shape: {
            className: 'basic2end'
          }
        }
      },
      {
        id: '8',
        label: 'NP'
      },
      {
        id: '9',
        label: 'DT'
      },
      {
        id: '10',
        label: 'an',
        styles: {
          shape: {
            className: 'basic2end'
          }
        }
      },
      {
        id: '11',
        label: 'NN'
      },
      {
        id: '12',
        label: 'example',
        styles: {
          shape: {
            className: 'basic2end'
          }
        }
      },
      {
        id: '13',
        label: '.'
      },
      {
        id: '14',
        label: 'sentence',
        styles: {
          shape: {
            className: 'basic2end'
          }
        }
      }
    ],
    edges: [
      {
        from: '3',
        to: '4'
      },
      {
        from: '2',
        to: '3'
      },
      {
        from: '1',
        to: '2'
      },
      {
        from: '6',
        to: '7'
      },
      {
        from: '5',
        to: '6'
      },
      {
        from: '9',
        to: '10'
      },
      {
        from: '8',
        to: '9'
      },
      {
        from: '11',
        to: '12'
      },
      {
        from: '8',
        to: '11'
      },
      {
        from: '5',
        to: '8'
      },
      {
        from: '1',
        to: '5'
      },
      {
        from: '13',
        to: '14'
      },
      {
        from: '1',
        to: '13'
      },
      {
        from: '0',
        to: '1'
      }
    ]
  }

  const myGraph: graphT = {
    nodes: [
      { id: 'ESE_380', label: 'ESE 380' },
      { id: 'OR_CSE_316_0', label: 'or', shape: 'circle' },
      { id: 'OR_CSE_316_1', label: 'or', shape: 'circle' },
      { id: 'OR_CSE_306_0', label: 'or', shape: 'circle' },
      { id: 'CSE_320', label: 'CSE 320' },
      { id: 'CSE_316', label: 'CSE 316' },
      { id: 'CSE_307', label: 'CSE 307' },
      { id: 'CSE_306', label: 'CSE 306' },
      { id: 'CSE_260', label: 'CSE 260' },
      { id: 'CSE_220', label: 'CSE 220' },
      { id: 'CSE_216', label: 'CSE 216' },
      { id: 'CSE_214', label: 'CSE 214' },
      { id: 'CSE_160', label: 'CSE 160' }
    ],
    edges: [
      { from: 'OR_CSE_316_0', to: 'CSE_316' },
      { from: 'OR_CSE_316_1', to: 'CSE_316' },
      { from: 'CSE_216', to: 'OR_CSE_316_0' },
      { from: 'CSE_307', to: 'OR_CSE_316_0' },
      { from: 'CSE_260', to: 'OR_CSE_316_1' },
      { from: 'CSE_214', to: 'OR_CSE_316_1' },
      { from: 'CSE_160', to: 'CSE_260' },
      { from: 'OR_CSE_306_0', to: 'CSE_306' },
      { from: 'CSE_320', to: 'OR_CSE_306_0' },
      { from: 'ESE_380', to: 'OR_CSE_306_0' },
      { from: 'CSE_220', to: 'CSE_320' },
      { from: 'CSE_214', to: 'CSE_220' }
    ]
  }

  const defaultNodeConfig = {
    styles: {
      node: {
        padding: {
          top: 10,
          bottom: 10,
          left: 10,
          right: 10
        }
      },
      shape: {
        styles: { stroke: '#000' },
        className: 'basic2'
      },
      label: {
        className: 'basic2label'
      }
    }
  }

  const [nodes, setNodes] = useState<Array<RecursivePartial<NodeOptions>>>(myGraph.nodes)
  const [edges, setEdges] = useState<Array<RecursivePartial<EdgeOptions>>>(myGraph.edges)
  const viewer = useRef<UncontrolledReactSVGPanZoom>(null)

  return (
    <div>
      <svg id="schedule" width={1150} height={1000}>
        <DagreReact
          nodes={nodes}
          edges={edges}
          defaultNodeConfig={defaultNodeConfig}
          graphOptions={{
            marginx: 15,
            marginy: 15,
            ranksep: 55,
            nodesep: 35
          }}
        />
      </svg>
    </div>
  )
}

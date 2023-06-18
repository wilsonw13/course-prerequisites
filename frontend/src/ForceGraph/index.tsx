import { useRef, useState, useEffect } from 'react'
import { ForceGraph3D } from 'react-force-graph'
import SpriteText from 'three-spritetext'
// import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js'
import { GraphData, Node } from '../interfaces/index.ts'

interface Props {
  graphData: GraphData | null,
}

interface Object3DNode extends Node, THREE.Object3D {
  color: string
}

export default function Graph ({ graphData }: Props) {
  const graphRef = useRef(undefined)

  // const [focusControls, setFocusControls] = useState<boolean>(true)

  // const enableControls = (enabled: boolean) => {
  //   const graphInstance = gr\aphRef?.current
  //   if (graphInstance) {
  //     const controls = graphInstance.controls()
  //     if (controls) {
  //       controls.enabled = enabled
  //     }
  //   }
  // }

  // useEffect(() => {
  //   enableControls(focusControls)
  // }, [focusControls])

  const ForceGraph = <ForceGraph3D
    ref={graphRef}

    graphData={graphData}
    nodeId={'course_number'}
    nodeLabel={'name'}
    nodeAutoColorBy={'group'}
    nodeThreeObject={(node: Object3DNode) => {
      const sprite = new SpriteText(node.course_number)
      sprite.material.depthWrite = false // make sprite background transparent
      sprite.color = node.color
      sprite.textHeight = 8
      return sprite
    }}
    nodeThreeObjectExtend={true}
    linkDirectionalArrowLength={3.5}
    linkDirectionalArrowRelPos={1}
    controlType={'fly'}
  />

  return (
    <>{ graphData ? ForceGraph : <div>Loading...</div>}</>
  )
}

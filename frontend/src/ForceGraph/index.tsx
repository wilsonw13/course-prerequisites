import { useRef, useState, useEffect, forwardRef } from 'react'
import ForceGraph3D from 'react-force-graph-3d'
import { GraphData } from '../interfaces'

interface Props {
  graphData: GraphData,
  // focusControls: boolean
}

export default function Graph ({ graphData/* , focusControls */ }: Props) {
  const graphRef = useRef(undefined)
  const [focusControls, setFocusControls] = useState<boolean>(true)

  const enableControls = (enabled: boolean) => {
    const graphInstance = graphRef?.current
    if (graphInstance) {
      const controls = graphInstance.controls()
      if (controls) {
        controls.enabled = enabled
      }
    }
  }

  useEffect(() => {
    enableControls(focusControls)
  }, [focusControls])

  return (
    <ForceGraph3D
      ref={graphRef}

      graphData={graphData}
      nodeLabel={'id'}
      nodeAutoColorBy={'group'}
      linkDirectionalArrowLength={3.5}
      linkDirectionalArrowRelPos={1}
      controlType={'fly'}
    />
  )
}

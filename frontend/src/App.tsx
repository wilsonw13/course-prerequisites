import { useEffect, useState } from 'react'
import ForceGraph3DPage from './3d-force-graph/index.tsx'
import SugiyamaLayoutView from './d3-dag/index.tsx'
import DagreMain from './dagre-d3/index.tsx'

export default function App () {
  const [page, setPage] = useState(1)

  return (
    <>
      {page ? <ForceGraph3DPage/> : <DagreMain/>}
    </>
  )
}

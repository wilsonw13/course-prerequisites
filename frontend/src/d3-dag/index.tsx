import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { graphStratify, sugiyama, decrossOpt } from 'd3-dag'

import PropTypes from 'prop-types'

const propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      parentIds: PropTypes.arrayOf(PropTypes.string)
    })
  ).isRequired
}

const SugiyamaLayoutView = ({ data }) => {
  const d3Chart = useRef()

  useEffect(() => {
    const dag = graphStratify()(data)

    const nodeRadius = 20
    const layout = sugiyama() // base layout
      .decross(decrossOpt()) // minimize number of crossings
      .nodeSize((node) => [(node ? 3.6 : 0.25) * nodeRadius, 3 * nodeRadius]) // set node size instead of constraining to fit
    const { width, height } = layout(dag)

    // --------------------------------
    // This code only handles rendering
    // --------------------------------
    const svgSelection = d3.select(d3Chart.current)
    svgSelection.attr('viewBox', [0, 0, width, height].join(' '))
    const defs = svgSelection.append('defs') // For gradients

    const steps = dag.size()
    const interp = d3.interpolateRainbow
    const colorMap = new Map()
    // for (const [i, node] of dag.idescendants().entries()) {
    // for (const [i, node] of dag.idescendants()) {
    for (const [i, node] of [...dag].entries()) {
      try {
        colorMap.set(node.data.id, interp(i / steps))
      } catch (e) {
        console.log('Error: ', i)
      }
    }

    // How to draw edges
    const line = d3
      .line()
      .curve(d3.curveCatmullRom)
      .x((d) => d.x)
      .y((d) => d.y)

    // Plot edges
    svgSelection
      .append('g')
      .selectAll('path')
      .data(dag.links())
      .enter()
      .append('path')
      .attr('d', ({ points }) => line(points))
      .attr('fill', 'none')
      .attr('stroke-width', 3)
      .attr('stroke', ({ source, target }) => {
        // encodeURIComponents for spaces, hope id doesn't have a `--` in it
        const gradId = encodeURIComponent(`${source.data.id}--${target.data.id}`)
        const grad = defs
          .append('linearGradient')
          .attr('id', gradId)
          .attr('gradientUnits', 'userSpaceOnUse')
          .attr('x1', source.x)
          .attr('x2', target.x)
          .attr('y1', source.y)
          .attr('y2', target.y)
        grad
          .append('stop')
          .attr('offset', '0%')
          .attr('stop-color', colorMap.get(source.data.id))
        grad
          .append('stop')
          .attr('offset', '100%')
          .attr('stop-color', colorMap.get(target.data.id))
        return `url(#${gradId})`
      })

    // Select nodes
    const nodes = svgSelection
      .append('g')
      .selectAll('g')
      .data(dag.descendants())
      .enter()
      .append('g')
      .attr('transform', ({ x, y }) => `translate(${x}, ${y})`)

    // Plot node circles
    nodes
      .append('circle')
      .attr('r', nodeRadius)
      .attr('fill', (n) => colorMap.get(n.data.id))

    // Add text to nodes
    nodes
      .append('text')
      .text((d) => d.data.id)
      .attr('font-weight', 'bold')
      .attr('font-family', 'sans-serif')
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('fill', 'white')
  })

  return (
    <div id='d3demo'>
      <svg ref={d3Chart}></svg>
    </div>
  )
}

SugiyamaLayoutView.propTypes = propTypes

export default SugiyamaLayoutView

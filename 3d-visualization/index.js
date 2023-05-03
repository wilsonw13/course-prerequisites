// async function fetchJSON(url) {
//     const response = await fetch(url);
//     return await response.json();
// }

// const nodes = {};

// await fetchJSON("../../log/CSE-data-short.json").then(data => {
//     console.log(data);
//     for(const c in data) {
//         nodes[`${data[c].department} ${data[c].number}`] = data[c].prerequisites;
//     }
//     console.log(nodes)
// });

import { CSS2DRenderer, CSS2DObject } from '//unpkg.com/three/examples/jsm/renderers/CSS2DRenderer.js';

// const Graph = ForceGraph3D()
//       (document.getElementById('graph'))
//         .jsonUrl('../../log/all-3d-visual.json')
//         .nodeAutoColorBy('group')
//         .nodeThreeObject(node => {
//           const sprite = new SpriteText(node.id);
//           sprite.material.depthWrite = false; // make sprite background transparent
//           sprite.color = node.color;
//           sprite.textHeight = 8;
//           return sprite;
//         })
//         .linkDirectionalArrowLength(3.5)
//         .linkDirectionalArrowRelPos(1);

//     // Spread nodes a little wider
//     Graph.d3Force('charge').strength(-120);

const Graph = ForceGraph3D({
    extraRenderers: [new CSS2DRenderer()]
})
      (document.getElementById('graph'))
        .jsonUrl('../datasets/CSE-3d-visual.json')
        // .jsonUrl('../../log/CSE-3d-visual.json')
        .nodeAutoColorBy('group')
        .nodeThreeObject(node => {
            const nodeEl = document.createElement('div');
            nodeEl.textContent = node.id;
            nodeEl.style.color = node.color;
            nodeEl.className = 'node-label';
            return new CSS2DObject(nodeEl);
        })
        .nodeThreeObjectExtend(true)
        .linkDirectionalArrowLength(3.5)
        .linkDirectionalArrowRelPos(1);

    // Spread nodes a little wider
    Graph.d3Force('charge').strength(-200);





    // count = 0
    // d.links.forEach(l => {
    //     if (!d.nodes.includes(l.source)) {
    //         count++;
    //         d.nodes.push(l.source);
    //     }
    // } )
    
    // console.log(d)
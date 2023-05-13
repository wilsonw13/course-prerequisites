import {
  CSS2DRenderer,
  CSS2DObject,
} from "//unpkg.com/three/examples/jsm/renderers/CSS2DRenderer.js";

/* const Graph = ForceGraph3D({ controlType: "fly" })(
  document.getElementById("graph")
)
  .jsonUrl("../../datasets/small-graph-data.json")
  .nodeAutoColorBy("group")
  .nodeThreeObject((node) => {
    const sprite = new SpriteText(node.id);
    sprite.material.depthWrite = false; // make sprite background transparent
    sprite.color = node.color;
    sprite.textHeight = 8;
    return sprite;
  })
  .linkDirectionalArrowLength(3.5)
  .linkDirectionalArrowRelPos(1);

// Spread nodes a little wider
Graph.d3Force("charge").strength(-120); */

const Graph = ForceGraph3D({
  controlType: "fly",
  extraRenderers: [new CSS2DRenderer()],
})(document.getElementById("graph"))
  .jsonUrl("../../datasets/queried-graph-data.json")
  .nodeLabel("name")
  .nodeAutoColorBy("group")
  .nodeThreeObject((node) => {
    // const nodeEl = document.createElement('div');
    // nodeEl.textContent = node.id;
    // nodeEl.style.color = node.color;
    // nodeEl.className = 'node-label';
    // return new CSS2DObject(nodeEl); // HTML node (sphere w/ text)

    const sprite = new SpriteText(node.id);
    sprite.material.depthWrite = false; // make sprite background transparent
    sprite.color = node.color;
    sprite.textHeight = 8;
    return sprite; // text only
  })
  .nodeThreeObjectExtend(true)
  .linkDirectionalArrowLength(3.5)
  .linkDirectionalArrowRelPos(1)
  .onNodeClick(moveCameraToNode);

function moveCameraToNode(node) {
  console.log(node);

  // Aim at node from outside it
  const distance = 300;
  const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

  const newPos =
    node.x || node.y || node.z
      ? { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }
      : { x: 0, y: 0, z: distance }; // special case if node is in (0,0,0)

  Graph.cameraPosition(
    newPos, // new position
    node, // lookAt ({ x, y, z })
    1000 // ms transition duration
  );
}

Graph.d3Force("charge").strength(-200); // Spread nodes a little wider
Graph.controls().rotateSpeed = 4; // increase rotation speed
Graph.controls().panSpeed = 0.05;
// Graph.controls().zoomSpeed = 2.4;

// GUI
const settings = {
  course: "",
};

const gui = new dat.GUI();

const courseController = gui.add(settings, "course");

courseController.onFinishChange(onCourseInputChange);

function onCourseInputChange() {
  const { nodes, links } = Graph.graphData();

  const selectedNode = nodes.find(
    (node) =>
      node.id.replace(" ", "") ===
      settings.course.replace(" ", "").toUpperCase()
  );

  if (selectedNode) moveCameraToNode(selectedNode);

  console.log(Graph.controls());
}

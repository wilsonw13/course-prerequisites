fetch("../../datasets/full-graph-data.json")
  .then((res) => res.json())
  .then((data) => {
    const Graph = ForceGraph()(document.getElementById("graph"))
      .graphData(data)
      .nodeId("id")
      .nodeAutoColorBy("group")
      .nodeLabel("name")
      .nodeCanvasObject((node, ctx, globalScale) => {
        const label = node.id;
        const fontSize = 12 / globalScale;
        ctx.font = `${fontSize}px Sans-Serif`;
        const textWidth = ctx.measureText(label).width;
        const bckgDimensions = [textWidth, fontSize].map(
          (n) => n + fontSize * 0.2
        ); // some padding

        ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
        ctx.fillRect(
          node.x - bckgDimensions[0] / 2,
          node.y - bckgDimensions[1] / 2,
          ...bckgDimensions
        );

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = node.color;
        ctx.fillText(label, node.x, node.y);

        node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
      })
      .nodePointerAreaPaint((node, color, ctx) => {
        ctx.fillStyle = color;
        const bckgDimensions = node.__bckgDimensions;
        bckgDimensions &&
          ctx.fillRect(
            node.x - bckgDimensions[0] / 2,
            node.y - bckgDimensions[1] / 2,
            ...bckgDimensions
          );
      })
      .linkDirectionalArrowLength(3.5)
      .linkDirectionalArrowRelPos(1)
      .onNodeClick(focusOnNode);

    function focusOnNode(node) {
      Graph.centerAt(node.x, node.y, 1000);
      Graph.zoom(4, 2000);
    }

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

      if (selectedNode) focusOnNode(selectedNode);
    }
  });

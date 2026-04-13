import { useEffect, useRef, useState } from "react";
import cytoscape, { type Core } from "cytoscape";
// @ts-ignore
import cola from "cytoscape-cola";

cytoscape.use(cola);

const NODE_STYLES: Record<string, { shape: string; color: string }> = {
  Patient: { shape: "ellipse", color: "#3b82f6" },
  Symptom: { shape: "round-rectangle", color: "#60a5fa" },
  Disease: { shape: "hexagon", color: "#ef4444" },
  Drug: { shape: "round-rectangle", color: "#22c55e" },
  Specialist: { shape: "diamond", color: "#a855f7" },
  Treatment: { shape: "rectangle", color: "#f97316" },
  RiskFactor: { shape: "triangle", color: "#eab308" },
  LabTest: { shape: "ellipse", color: "#06b6d4" },
  Protocol: { shape: "rectangle", color: "#6b7280" },
  FollowUp: { shape: "round-rectangle", color: "#ec4899" },
};

interface GraphNode {
  id: string;
  label: string;
  type: string;
  score?: number;
  hop?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  label?: string;
  weight?: number;
  severity?: string;
}

interface AnimationHop {
  hop: number;
  nodes: string[];
  edges: string[];
}

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  animationSequence?: AnimationHop[];
  layout?: "concentric" | "cola" | "breadthfirst" | "circle";
  onNodeClick?: (nodeId: string, nodeData: any) => void;
}

export default function GraphView({
  nodes,
  edges,
  animationSequence,
  layout = "cola",
  onNodeClick,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [currentHop, setCurrentHop] = useState(-1);
  const [, setAnimating] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const isDark = document.documentElement.classList.contains('dark');

    const elements: any[] = [];

    nodes.forEach((n) => {
      const style = NODE_STYLES[n.type] || NODE_STYLES.Patient;
      elements.push({
        data: {
          id: n.id,
          label: n.label,
          type: n.type,
          score: n.score,
          hop: n.hop,
          nodeColor: style.color,
          nodeShape: style.shape,
        },
      });
    });

    edges.forEach((e, i) => {
      const edgeId = `e${i}-${e.source}-${e.target}`;
      elements.push({
        data: {
          id: edgeId,
          source: e.source,
          target: e.target,
          label: e.label || "",
          weight: e.weight || 1,
          severity: e.severity,
        },
      });
    });

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": "data(nodeColor)",
            shape: "data(nodeShape)" as any,
            width: 50,
            height: 50,
            "font-size": "10px",
            "text-wrap": "wrap",
            "text-max-width": "80px",
            "text-valign": "bottom",
            "text-margin-y": 8,
            color: isDark ? "#cbd5e1" : "#1e293b",
            "border-width": 2,
            "border-color": "data(nodeColor)",
            "border-opacity": 0.5,
            "background-opacity": 0.85,
            "transition-property":
              "background-opacity, width, height, border-width",
            "transition-duration": 400,
          },
        },
        {
          selector: "node[?score]",
          style: {
            width: "mapData(score, 0, 1, 40, 80)",
            height: "mapData(score, 0, 1, 40, 80)",
          },
        },
        {
          selector: "edge",
          style: {
            width: "mapData(weight, 0, 1, 1, 5)",
            "line-color": isDark ? "#475569" : "#cbd5e1",
            "target-arrow-color": isDark ? "#475569" : "#cbd5e1",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "line-opacity": 0.6,
            label: "data(label)",
            "font-size": "8px",
            color: isDark ? "#94a3b8" : "#64748b",
            "text-rotation": "autorotate",
            "transition-property": "line-color, line-opacity, width",
            "transition-duration": 400,
          },
        },
        {
          selector: 'edge[severity = "severe"]',
          style: {
            "line-color": "#ef4444",
            "target-arrow-color": "#ef4444",
            "line-style": "dashed",
            width: 4,
          },
        },
        {
          selector: 'edge[severity = "moderate"]',
          style: {
            "line-color": "#eab308",
            "target-arrow-color": "#eab308",
            width: 3,
          },
        },
        {
          selector: 'edge[severity = "mild"]',
          style: {
            "line-color": "#22c55e",
            "target-arrow-color": "#22c55e",
            width: 2,
          },
        },
        {
          selector: ".highlighted",
          style: {
            "border-width": 4,
            "background-opacity": 1,
            "border-opacity": 1,
          },
        },
        {
          selector: "edge.highlighted",
          style: {
            "line-opacity": 1,
            width: 4,
            "line-color": "#818cf8",
            "target-arrow-color": "#818cf8",
          },
        },
        {
          selector: ".dimmed",
          style: {
            "background-opacity": 0.2,
            "border-opacity": 0.2,
          },
        },
        {
          selector: "edge.dimmed",
          style: {
            "line-opacity": 0.15,
          },
        },
        {
          selector: ".hidden-node",
          style: {
            "background-opacity": 0,
            "border-opacity": 0,
            width: 0,
            height: 0,
            "font-size": "0px",
          },
        },
        {
          selector: "edge.hidden-edge",
          style: {
            "line-opacity": 0,
            width: 0,
            "font-size": "0px",
          },
        },
      ],
      layout: getLayout(layout),
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.3,
    });

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      onNodeClick?.(node.id(), node.data());
    });

    cyRef.current = cy;

    if (animationSequence && animationSequence.length > 0) {
      runAnimation(cy, animationSequence);
    }

    return () => {
      cy.destroy();
    };
  }, [nodes, edges, animationSequence, layout]);

  function getLayout(type: string) {
    switch (type) {
      case "concentric":
        return {
          name: "concentric",
          concentric: (node: any) => {
            const hop = node.data("hop") ?? 0;
            return 10 - hop;
          },
          levelWidth: () => 1,
          minNodeSpacing: 50,
          animate: true,
          animationDuration: 500,
        };
      case "breadthfirst":
        return {
          name: "breadthfirst",
          directed: true,
          spacingFactor: 1.5,
          animate: true,
          animationDuration: 500,
        };
      case "circle":
        return {
          name: "circle",
          animate: true,
          animationDuration: 500,
        };
      case "cola":
      default:
        return {
          name: "cola",
          animate: true,
          maxSimulationTime: 2000,
          nodeSpacing: 30,
          edgeLength: 120,
        };
    }
  }

  async function runAnimation(cy: Core, sequence: AnimationHop[]) {
    setAnimating(true);

    cy.elements().addClass("hidden-node");
    cy.edges().addClass("hidden-edge");

    for (const hop of sequence) {
      setCurrentHop(hop.hop);

      for (const nodeId of hop.nodes) {
        const node = cy.getElementById(nodeId);
        if (node.length) {
          node.removeClass("hidden-node");
          node.addClass("highlighted");
          node.animate(
            {
              style: { width: 70, height: 70 },
            },
            {
              duration: 300,
              complete: () => {
                node.animate(
                  { style: { width: 50, height: 50 } },
                  { duration: 200 }
                );
              },
            }
          );
        }
      }

      for (const edgeId of hop.edges) {
        const edge = cy.getElementById(edgeId);
        if (edge.length) {
          edge.removeClass("hidden-edge");
          edge.addClass("highlighted");
        }
      }

      await new Promise((r) => setTimeout(r, 600));
    }

    setAnimating(false);
    setCurrentHop(sequence.length);
  }

  function replayAnimation() {
    if (cyRef.current && animationSequence) {
      runAnimation(cyRef.current, animationSequence);
    }
  }

  return (
    <div className="relative h-full w-full">
      <div ref={containerRef} className="h-full w-full bg-slate-100 dark:bg-slate-950/50 rounded-2xl border border-slate-200 dark:border-white/10" />

      {/* Hop progress indicator */}
      {animationSequence && animationSequence.length > 0 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-white/90 dark:bg-slate-900/90 backdrop-blur px-4 py-2 rounded-full border border-slate-200 dark:border-white/10 shadow-sm dark:shadow-none">
          {animationSequence.map((hop) => (
            <div key={hop.hop} className="flex items-center gap-2">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  currentHop >= hop.hop
                    ? "bg-indigo-500 text-white scale-110"
                    : "bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400"
                }`}
              >
                {hop.hop}
              </div>
              {hop.hop < animationSequence.length && (
                <div
                  className={`w-6 h-0.5 ${
                    currentHop > hop.hop ? "bg-indigo-500" : "bg-slate-200 dark:bg-slate-700"
                  }`}
                />
              )}
            </div>
          ))}
          <button
            onClick={replayAnimation}
            className="ml-3 text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-bold"
          >
            Replay
          </button>
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-3 right-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur p-3 rounded-xl border border-slate-200 dark:border-white/10 text-xs space-y-1 shadow-sm dark:shadow-none">
        {Object.entries(NODE_STYLES)
          .filter(([type]) => nodes.some((n) => n.type === type))
          .map(([type, style]) => (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: style.color }}
              />
              <span className="text-slate-600 dark:text-slate-400">{type}</span>
            </div>
          ))}
      </div>
    </div>
  );
}

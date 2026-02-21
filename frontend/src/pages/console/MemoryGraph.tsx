import { useState, useCallback, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Filter,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Download,
  RefreshCw
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface Node {
  id: string;
  label: string;
  type: "error" | "fix" | "policy" | "experiment";
  x: number;
  y: number;
  connections: string[];
  severity?: "high" | "medium" | "low";
  domain?: string;
}

const nodes: Node[] = [
  { id: "1", label: "API Timeout", type: "error", x: 150, y: 100, connections: ["5", "6"], severity: "high", domain: "api" },
  { id: "2", label: "Memory Leak", type: "error", x: 400, y: 80, connections: ["7", "8"], severity: "medium", domain: "code" },
  { id: "3", label: "Auth Failure", type: "error", x: 650, y: 120, connections: ["9"], severity: "high", domain: "user-flow" },
  { id: "4", label: "Rate Limit", type: "error", x: 300, y: 250, connections: ["5", "10"], severity: "low", domain: "api" },
  { id: "5", label: "Retry Logic", type: "fix", x: 200, y: 180, connections: ["11"], domain: "api" },
  { id: "6", label: "Connection Pool", type: "fix", x: 100, y: 280, connections: ["11"], domain: "code" },
  { id: "7", label: "GC Tuning", type: "fix", x: 450, y: 160, connections: ["12"], domain: "code" },
  { id: "8", label: "Object Pooling", type: "fix", x: 500, y: 250, connections: ["12"], domain: "code" },
  { id: "9", label: "Token Refresh", type: "fix", x: 700, y: 200, connections: ["13"], domain: "user-flow" },
  { id: "10", label: "Backoff Strategy", type: "policy", x: 350, y: 350, connections: [], domain: "api" },
  { id: "11", label: "Resilience Policy", type: "policy", x: 150, y: 380, connections: [], domain: "api" },
  { id: "12", label: "Memory Policy", type: "policy", x: 480, y: 350, connections: [], domain: "code" },
  { id: "13", label: "Auth Policy", type: "policy", x: 720, y: 300, connections: [], domain: "user-flow" },
  { id: "14", label: "RL Experiment 1", type: "experiment", x: 250, y: 450, connections: ["10", "11"], domain: "api" },
  { id: "15", label: "RL Experiment 2", type: "experiment", x: 550, y: 450, connections: ["12"], domain: "code" },
];

const NodeComponent = ({ 
  node, 
  isSelected, 
  onClick 
}: { 
  node: Node; 
  isSelected: boolean; 
  onClick: () => void;
}) => {
  const getNodeStyle = (type: Node["type"]) => {
    switch (type) {
      case "error": return "bg-red-500/20 border-red-500/50 text-red-400";
      case "fix": return "bg-green-500/20 border-green-500/50 text-green-400";
      case "policy": return "bg-blue-500/20 border-blue-500/50 text-blue-400";
      case "experiment": return "bg-primary/20 border-primary/50 text-primary";
    }
  };

  const getNodeSize = (type: Node["type"]) => {
    switch (type) {
      case "error": return "h-16 w-16";
      case "fix": return "h-14 w-14";
      case "policy": return "h-12 w-12";
      case "experiment": return "h-14 w-14";
    }
  };

  return (
    <motion.div
      className={cn(
        "absolute rounded-full border-2 flex items-center justify-center cursor-pointer transition-all duration-200",
        getNodeStyle(node.type),
        getNodeSize(node.type),
        isSelected && "ring-2 ring-primary ring-offset-2 ring-offset-background scale-110"
      )}
      style={{ left: node.x, top: node.y, transform: "translate(-50%, -50%)" }}
      onClick={onClick}
      whileHover={{ scale: 1.1 }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <span className="text-[10px] font-medium text-center leading-tight px-1">
        {node.label.split(" ").slice(0, 2).join(" ")}
      </span>
    </motion.div>
  );
};

export const MemoryGraph = () => {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [zoom, setZoom] = useState(1);
  const [timeFilter, setTimeFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [domainFilter, setDomainFilter] = useState("all");
  const svgRef = useRef<SVGSVGElement>(null);

  const filteredNodes = nodes.filter((node) => {
    if (severityFilter !== "all" && node.severity && node.severity !== severityFilter) return false;
    if (domainFilter !== "all" && node.domain !== domainFilter) return false;
    return true;
  });

  const filteredNodeIds = new Set(filteredNodes.map(n => n.id));

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Memory Graph</h1>
          <p className="text-muted-foreground">Visualize relationships between errors, fixes, and policies</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="flex gap-6 h-[calc(100%-4rem)]">
        {/* Graph Canvas */}
        <Card className="flex-1 bg-card border-border relative overflow-hidden">
          {/* Toolbar */}
          <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
            <div className="flex items-center gap-1 bg-background/80 backdrop-blur-sm rounded-lg p-1 border border-border">
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8"
                onClick={() => setZoom(Math.min(zoom + 0.2, 2))}
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
              <span className="text-xs px-2 min-w-[3rem] text-center">{Math.round(zoom * 100)}%</span>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8"
                onClick={() => setZoom(Math.max(zoom - 0.2, 0.5))}
              >
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Legend */}
          <div className="absolute bottom-4 left-4 z-10 bg-background/80 backdrop-blur-sm rounded-lg p-3 border border-border">
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-red-500/50" />
                <span>Errors</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-green-500/50" />
                <span>Fixes</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-blue-500/50" />
                <span>Policies</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-primary/50" />
                <span>Experiments</span>
              </div>
            </div>
          </div>

          {/* Graph */}
          <CardContent className="p-0 h-full">
            <div 
              className="w-full h-full relative"
              style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }}
            >
              {/* Connection Lines */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {filteredNodes.map((node) =>
                  node.connections
                    .filter(connId => filteredNodeIds.has(connId))
                    .map((connId) => {
                      const targetNode = nodes.find((n) => n.id === connId);
                      if (!targetNode) return null;
                      return (
                        <line
                          key={`${node.id}-${connId}`}
                          x1={node.x}
                          y1={node.y}
                          x2={targetNode.x}
                          y2={targetNode.y}
                          stroke="hsl(0, 0%, 30%)"
                          strokeWidth="1"
                          strokeDasharray="4"
                        />
                      );
                    })
                )}
              </svg>

              {/* Nodes */}
              {filteredNodes.map((node) => (
                <NodeComponent
                  key={node.id}
                  node={node}
                  isSelected={selectedNode?.id === node.id}
                  onClick={() => setSelectedNode(node)}
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Sidebar */}
        <div className="w-[300px] space-y-4 flex-shrink-0">
          {/* Filters */}
          <Card className="bg-card border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Filters
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-xs text-muted-foreground mb-1.5 block">Time Range</label>
                <Select value={timeFilter} onValueChange={setTimeFilter}>
                  <SelectTrigger className="bg-background">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    <SelectItem value="all">All Time</SelectItem>
                    <SelectItem value="24h">Last 24 Hours</SelectItem>
                    <SelectItem value="7d">Last 7 Days</SelectItem>
                    <SelectItem value="30d">Last 30 Days</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1.5 block">Severity</label>
                <Select value={severityFilter} onValueChange={setSeverityFilter}>
                  <SelectTrigger className="bg-background">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    <SelectItem value="all">All Severities</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1.5 block">Domain</label>
                <Select value={domainFilter} onValueChange={setDomainFilter}>
                  <SelectTrigger className="bg-background">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    <SelectItem value="all">All Domains</SelectItem>
                    <SelectItem value="code">Code</SelectItem>
                    <SelectItem value="api">API</SelectItem>
                    <SelectItem value="user-flow">User Flow</SelectItem>
                    <SelectItem value="math">Math</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Node Details */}
          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card className="bg-card border-border">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Node Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-xs text-muted-foreground">Label</p>
                    <p className="font-medium">{selectedNode.label}</p>
                  </div>
                  <div className="flex gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground">Type</p>
                      <Badge variant="outline" className="capitalize mt-1">
                        {selectedNode.type}
                      </Badge>
                    </div>
                    {selectedNode.severity && (
                      <div>
                        <p className="text-xs text-muted-foreground">Severity</p>
                        <Badge 
                          variant="outline" 
                          className={cn(
                            "capitalize mt-1",
                            selectedNode.severity === "high" && "text-red-400 border-red-400/30",
                            selectedNode.severity === "medium" && "text-amber-400 border-amber-400/30",
                            selectedNode.severity === "low" && "text-green-400 border-green-400/30"
                          )}
                        >
                          {selectedNode.severity}
                        </Badge>
                      </div>
                    )}
                  </div>
                  {selectedNode.domain && (
                    <div>
                      <p className="text-xs text-muted-foreground">Domain</p>
                      <p className="text-sm capitalize">{selectedNode.domain}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-xs text-muted-foreground">Connections</p>
                    <p className="text-sm">{selectedNode.connections.length} linked nodes</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Stats */}
          <Card className="bg-card border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Graph Stats</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-3">
              <div className="p-2 rounded-lg bg-muted/30 text-center">
                <p className="text-lg font-bold">{filteredNodes.length}</p>
                <p className="text-xs text-muted-foreground">Nodes</p>
              </div>
              <div className="p-2 rounded-lg bg-muted/30 text-center">
                <p className="text-lg font-bold">
                  {filteredNodes.reduce((acc, n) => acc + n.connections.filter(c => filteredNodeIds.has(c)).length, 0)}
                </p>
                <p className="text-xs text-muted-foreground">Edges</p>
              </div>
              <div className="p-2 rounded-lg bg-muted/30 text-center">
                <p className="text-lg font-bold">{filteredNodes.filter(n => n.type === "error").length}</p>
                <p className="text-xs text-muted-foreground">Errors</p>
              </div>
              <div className="p-2 rounded-lg bg-muted/30 text-center">
                <p className="text-lg font-bold">{filteredNodes.filter(n => n.type === "fix").length}</p>
                <p className="text-xs text-muted-foreground">Fixes</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MemoryGraph;

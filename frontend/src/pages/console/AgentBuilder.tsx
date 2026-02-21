import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Bot, 
  Plus, 
  Trash2, 
  Settings, 
  Play,
  Save,
  ArrowRight,
  Brain,
  Shield,
  Zap,
  Eye,
  GitBranch,
  Code2,
  Database,
  AlertTriangle,
  CheckCircle2,
  GripVertical
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface WorkflowNode {
  id: string;
  type: "monitor" | "critic" | "executor" | "planner" | "custom";
  name: string;
  config: Record<string, any>;
}

const nodeTypes = [
  { type: "monitor", name: "Monitor", icon: Eye, color: "bg-green-500/10 text-green-500 border-green-500/20", desc: "Detect errors and anomalies" },
  { type: "critic", name: "Critic", icon: Brain, color: "bg-purple-500/10 text-purple-500 border-purple-500/20", desc: "Analyze and evaluate solutions" },
  { type: "executor", name: "Executor", icon: Zap, color: "bg-primary/10 text-primary border-primary/20", desc: "Execute corrections and fixes" },
  { type: "planner", name: "Planner", icon: GitBranch, color: "bg-blue-500/10 text-blue-500 border-blue-500/20", desc: "Plan multi-step strategies" },
  { type: "custom", name: "Custom", icon: Code2, color: "bg-amber-500/10 text-amber-500 border-amber-500/20", desc: "Custom logic and tools" },
];

export const AgentBuilder = () => {
  const [agentName, setAgentName] = useState("New Agent");
  const [workflow, setWorkflow] = useState<WorkflowNode[]>([
    { id: "1", type: "monitor", name: "Monitor-01", config: {} },
    { id: "2", type: "critic", name: "Critic-01", config: {} },
    { id: "3", type: "executor", name: "Executor-01", config: {} },
  ]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selfHealing, setSelfHealing] = useState(true);
  const [strategy, setStrategy] = useState("hybrid");

  const addNode = (type: WorkflowNode["type"]) => {
    const newNode: WorkflowNode = {
      id: Date.now().toString(),
      type,
      name: `${type.charAt(0).toUpperCase() + type.slice(1)}-${workflow.filter(n => n.type === type).length + 1}`,
      config: {}
    };
    setWorkflow([...workflow, newNode]);
    toast.success(`Added ${newNode.name} to workflow`);
  };

  const removeNode = (id: string) => {
    setWorkflow(workflow.filter(n => n.id !== id));
    if (selectedNode === id) setSelectedNode(null);
    toast.success("Node removed from workflow");
  };

  const moveNode = (index: number, direction: "up" | "down") => {
    const newWorkflow = [...workflow];
    const newIndex = direction === "up" ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= workflow.length) return;
    [newWorkflow[index], newWorkflow[newIndex]] = [newWorkflow[newIndex], newWorkflow[index]];
    setWorkflow(newWorkflow);
  };

  const handleDeploy = () => {
    toast.success("Agent deployed successfully!", {
      description: `${agentName} is now running with ${workflow.length} nodes`
    });
  };

  const handleSave = () => {
    toast.success("Agent configuration saved");
  };

  const getNodeStyle = (type: WorkflowNode["type"]) => {
    return nodeTypes.find(n => n.type === type) || nodeTypes[0];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agent Builder</h1>
          <p className="text-muted-foreground">Create and configure custom agent workflows</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Draft
          </Button>
          <Button className="btn-primary" onClick={handleDeploy}>
            <Play className="h-4 w-4 mr-2" />
            Deploy Agent
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Node Palette */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Add Nodes
              </CardTitle>
              <CardDescription>Drag or click to add to workflow</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {nodeTypes.map((node) => (
                <button
                  key={node.type}
                  onClick={() => addNode(node.type as WorkflowNode["type"])}
                  className="w-full flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary/50 hover:bg-muted/30 transition-all group"
                >
                  <div className={cn("h-10 w-10 rounded-lg flex items-center justify-center", node.color)}>
                    <node.icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="font-medium group-hover:text-primary transition-colors">{node.name}</p>
                    <p className="text-xs text-muted-foreground">{node.desc}</p>
                  </div>
                  <Plus className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </button>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Workflow Canvas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5" />
                Workflow
              </CardTitle>
              <CardDescription>Define agent processing pipeline</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {workflow.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Bot className="h-12 w-12 mx-auto mb-4 opacity-30" />
                  <p>No nodes in workflow</p>
                  <p className="text-sm">Add nodes from the palette</p>
                </div>
              ) : (
                workflow.map((node, index) => {
                  const style = getNodeStyle(node.type);
                  const Icon = style.icon;
                  return (
                    <div key={node.id}>
                      <motion.div
                        layout
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={cn(
                          "flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer",
                          selectedNode === node.id 
                            ? "border-primary bg-primary/5" 
                            : "border-border hover:border-primary/50"
                        )}
                        onClick={() => setSelectedNode(node.id)}
                      >
                        <GripVertical className="h-4 w-4 text-muted-foreground cursor-grab" />
                        <div className={cn("h-8 w-8 rounded-lg flex items-center justify-center", style.color)}>
                          <Icon className="h-4 w-4" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">{node.name}</p>
                          <p className="text-xs text-muted-foreground capitalize">{node.type}</p>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={(e) => { e.stopPropagation(); moveNode(index, "up"); }}
                            disabled={index === 0}
                          >
                            <span className="text-xs">↑</span>
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={(e) => { e.stopPropagation(); moveNode(index, "down"); }}
                            disabled={index === workflow.length - 1}
                          >
                            <span className="text-xs">↓</span>
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 text-red-500 hover:text-red-400"
                            onClick={(e) => { e.stopPropagation(); removeNode(node.id); }}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </motion.div>
                      {index < workflow.length - 1 && (
                        <div className="flex justify-center py-1">
                          <ArrowRight className="h-4 w-4 text-muted-foreground rotate-90" />
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Configuration Panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Agent Name</Label>
                <Input 
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  className="bg-background"
                />
              </div>

              <div className="space-y-2">
                <Label>Correction Strategy</Label>
                <Select value={strategy} onValueChange={setStrategy}>
                  <SelectTrigger className="bg-background">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    <SelectItem value="rule-based">Rule-Based</SelectItem>
                    <SelectItem value="ml">ML-Driven</SelectItem>
                    <SelectItem value="hybrid">Hybrid (Recommended)</SelectItem>
                    <SelectItem value="tot">Tree of Thoughts</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator />

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Self-Healing</p>
                    <p className="text-xs text-muted-foreground">Auto-correct detected errors</p>
                  </div>
                  <Switch checked={selfHealing} onCheckedChange={setSelfHealing} />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Memory Persistence</p>
                    <p className="text-xs text-muted-foreground">Save corrections to memory</p>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Dry Run Mode</p>
                    <p className="text-xs text-muted-foreground">Simulate without applying</p>
                  </div>
                  <Switch />
                </div>
              </div>

              <Separator />

              {/* Validation */}
              <div className="space-y-2">
                <p className="font-medium text-sm">Validation</p>
                <div className="space-y-2">
                  {workflow.length > 0 ? (
                    <>
                      <div className="flex items-center gap-2 text-sm text-green-500">
                        <CheckCircle2 className="h-4 w-4" />
                        {workflow.length} nodes configured
                      </div>
                      <div className="flex items-center gap-2 text-sm text-green-500">
                        <CheckCircle2 className="h-4 w-4" />
                        Agent name set
                      </div>
                      <div className="flex items-center gap-2 text-sm text-green-500">
                        <CheckCircle2 className="h-4 w-4" />
                        Ready to deploy
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center gap-2 text-sm text-amber-500">
                      <AlertTriangle className="h-4 w-4" />
                      Add at least one node
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default AgentBuilder;

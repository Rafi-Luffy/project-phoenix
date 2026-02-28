import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bot, 
  X, 
  Activity,
  Clock,
  CheckCircle2,
  AlertTriangle,
  MoreVertical,
  Play,
  Pause,
  RefreshCw,
  ChevronRight,
  Brain,
  GitBranch,
  Plus,
  Trash2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface Agent {
  id: string;
  name: string;
  role: "Planner" | "Critic" | "Executor" | "Monitor";
  status: "active" | "idle" | "error";
  lastError: string;
  lastCorrection: string;
  version: string;
  uptime: string;
  corrections: number;
}

const STORAGE_KEY = 'phoenix_agents';

export const Agents = () => {
  const [agents, setAgents] = useState<Agent[]>(() => {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]'); }
    catch { return []; }
  });
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState<Agent['role']>('Monitor');

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(agents));
  }, [agents]);

  const addAgent = () => {
    if (!newName.trim()) return;
    const agent: Agent = {
      id: crypto.randomUUID(),
      name: newName.trim(),
      role: newRole,
      status: 'idle',
      lastError: '—',
      lastCorrection: '—',
      version: 'v1.0.0',
      uptime: '0m',
      corrections: 0,
    };
    setAgents(prev => [...prev, agent]);
    setNewName('');
    setNewRole('Monitor');
    setDialogOpen(false);
  };

  const deleteAgent = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setAgents(prev => prev.filter(a => a.id !== id));
    setSelectedAgent(prev => prev?.id === id ? null : prev);
  };

  const getRoleColor = (role: Agent["role"]) => {
    switch (role) {
      case "Planner": return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "Critic": return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      case "Executor": return "bg-primary/10 text-primary border-primary/20";
      case "Monitor": return "bg-green-500/10 text-green-400 border-green-500/20";
    }
  };

  const getStatusIcon = (status: Agent["status"]) => {
    switch (status) {
      case "active": return <span className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />;
      case "idle": return <span className="h-2 w-2 bg-amber-500 rounded-full" />;
      case "error": return <AlertTriangle className="h-3 w-3 text-red-500" />;
    }
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)]">
      {/* Main Content */}
      <div className="flex-1 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Agents</h1>
            <p className="text-muted-foreground">Manage and monitor your runtime agents</p>
          </div>
          <Button variant="hero" size="sm" onClick={() => setDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Agent
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: "Total Agents", value: agents.length.toString(), icon: Bot },
            { label: "Active", value: agents.filter(a => a.status === "active").length.toString(), icon: Activity },
            { label: "Corrections Today", value: "0", icon: CheckCircle2 },
            { label: "Avg Response", value: "—", icon: Clock },
          ].map((stat, i) => (
            <Card key={i} className="bg-card border-border">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <stat.icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Agents Table */}
        <Card className="bg-card border-border">
          <CardContent className="p-0">
            {agents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <Bot className="h-12 w-12 text-muted-foreground/20 mb-4" />
                <p className="text-lg font-medium mb-1">No agents deployed yet</p>
                <p className="text-sm text-muted-foreground mb-6">
                  Deploy your first agent to start monitoring and self-healing automatically.
                </p>
                <Button variant="hero" size="sm" onClick={() => setDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add First Agent
                </Button>
              </div>
            ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent border-border">
                  <TableHead className="text-muted-foreground">Agent</TableHead>
                  <TableHead className="text-muted-foreground">Role</TableHead>
                  <TableHead className="text-muted-foreground">Status</TableHead>
                  <TableHead className="text-muted-foreground">Last Error</TableHead>
                  <TableHead className="text-muted-foreground">Last Correction</TableHead>
                  <TableHead className="text-muted-foreground">Version</TableHead>
                  <TableHead className="text-muted-foreground text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {agents.map((agent) => (
                  <TableRow 
                    key={agent.id}
                    className={cn(
                      "cursor-pointer border-border transition-colors",
                      selectedAgent?.id === agent.id ? "bg-primary/5" : "hover:bg-muted/50"
                    )}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Bot className="h-4 w-4 text-muted-foreground" />
                        {agent.name}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={getRoleColor(agent.role)}>
                        {agent.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(agent.status)}
                        <span className="capitalize text-sm">{agent.status}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">{agent.lastError}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">{agent.lastCorrection}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">{agent.version}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-card border-border">
                          <DropdownMenuItem>
                            <Play className="h-4 w-4 mr-2" /> Start
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Pause className="h-4 w-4 mr-2" /> Pause
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <RefreshCw className="h-4 w-4 mr-2" /> Restart
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={(e) => deleteAgent(agent.id, e)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" /> Remove
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Side Panel */}
      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="w-[400px] flex-shrink-0"
          >
            <Card className="bg-card border-border h-full">
              <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-border">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{selectedAgent.name}</CardTitle>
                    <Badge variant="outline" className={cn("mt-1", getRoleColor(selectedAgent.role))}>
                      {selectedAgent.role}
                    </Badge>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => setSelectedAgent(null)}
                  className="h-8 w-8"
                >
                  <X className="h-4 w-4" />
                </Button>
              </CardHeader>

              <ScrollArea className="h-[calc(100%-5rem)]">
                <CardContent className="p-4 space-y-6">
                  {/* Agent Stats */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-muted/50">
                      <p className="text-xs text-muted-foreground">Uptime</p>
                      <p className="font-semibold">{selectedAgent.uptime}</p>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50">
                      <p className="text-xs text-muted-foreground">Corrections</p>
                      <p className="font-semibold">{selectedAgent.corrections}</p>
                    </div>
                  </div>

                  {/* Memory Summary */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Brain className="h-4 w-4 text-primary" />
                      <h3 className="font-semibold">Memory Summary</h3>
                    </div>
                    <div className="flex flex-col items-center justify-center py-6 text-muted-foreground text-xs border border-dashed border-border rounded-lg">
                      <Brain className="h-5 w-5 mb-1 opacity-20" />
                      No memory data yet for this agent
                    </div>
                  </div>

                  {/* Recent Trace */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <GitBranch className="h-4 w-4 text-primary" />
                      <h3 className="font-semibold">Recent ToT Trace</h3>
                    </div>
                    <div className="flex flex-col items-center justify-center py-6 text-muted-foreground text-xs border border-dashed border-border rounded-lg">
                      <GitBranch className="h-5 w-5 mb-1 opacity-20" />
                      No trace data yet for this agent
                    </div>
                  </div>
                </CardContent>
              </ScrollArea>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Add Agent Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-card border-border sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              Add Agent
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <div className="space-y-1.5">
              <Label htmlFor="agent-name">Agent Name</Label>
              <Input
                id="agent-name"
                placeholder="e.g. Planner-Alpha"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addAgent()}
                className="bg-background border-border"
              />
            </div>
            <div className="space-y-1.5">
              <Label>Role</Label>
              <Select value={newRole} onValueChange={(v) => setNewRole(v as Agent['role'])}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="Planner">Planner</SelectItem>
                  <SelectItem value="Critic">Critic</SelectItem>
                  <SelectItem value="Executor">Executor</SelectItem>
                  <SelectItem value="Monitor">Monitor</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2 pt-2">
              <Button className="flex-1" variant="hero" onClick={addAgent} disabled={!newName.trim()}>
                <Plus className="h-4 w-4 mr-2" /> Add Agent
              </Button>
              <Button variant="outline" className="border-border" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Agents;

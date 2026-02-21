import { useState } from "react";
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
  GitBranch
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

const agents: Agent[] = [
  { id: "1", name: "Monitor-01", role: "Monitor", status: "active", lastError: "API timeout", lastCorrection: "2m ago", version: "v2.4.1", uptime: "14d 3h", corrections: 234 },
  { id: "2", name: "Monitor-02", role: "Monitor", status: "active", lastError: "Memory leak", lastCorrection: "12m ago", version: "v2.4.1", uptime: "14d 3h", corrections: 189 },
  { id: "3", name: "Critic-01", role: "Critic", status: "idle", lastError: "-", lastCorrection: "1h ago", version: "v2.3.8", uptime: "7d 12h", corrections: 156 },
  { id: "4", name: "Critic-02", role: "Critic", status: "active", lastError: "Rate limit", lastCorrection: "8m ago", version: "v2.4.0", uptime: "3d 5h", corrections: 98 },
  { id: "5", name: "Executor-01", role: "Executor", status: "active", lastError: "Loop detected", lastCorrection: "25m ago", version: "v2.4.1", uptime: "14d 3h", corrections: 312 },
  { id: "6", name: "Executor-02", role: "Executor", status: "error", lastError: "Config mismatch", lastCorrection: "45m ago", version: "v2.4.0", uptime: "1d 8h", corrections: 45 },
  { id: "7", name: "Executor-03", role: "Executor", status: "active", lastError: "Null pointer", lastCorrection: "5m ago", version: "v2.4.1", uptime: "10d 2h", corrections: 278 },
  { id: "8", name: "Planner-01", role: "Planner", status: "active", lastError: "-", lastCorrection: "15m ago", version: "v2.4.1", uptime: "14d 3h", corrections: 445 },
  { id: "9", name: "Planner-02", role: "Planner", status: "idle", lastError: "-", lastCorrection: "2h ago", version: "v2.3.9", uptime: "5d 18h", corrections: 203 },
];

const traceSteps = [
  { step: "Detection", time: "0ms", status: "complete", details: "Anomaly detected in response latency" },
  { step: "Analysis", time: "120ms", status: "complete", details: "Root cause: Database connection pool exhausted" },
  { step: "Planning", time: "340ms", status: "complete", details: "Strategy: Increase pool size, add connection timeout" },
  { step: "Execution", time: "890ms", status: "complete", details: "Applied configuration changes to db-config.yaml" },
  { step: "Validation", time: "1.2s", status: "complete", details: "Response latency normalized, no regression detected" },
];

const memorySummary = [
  { concept: "API Timeouts", count: 45, severity: "high" },
  { concept: "Memory Leaks", count: 23, severity: "medium" },
  { concept: "Rate Limiting", count: 67, severity: "low" },
  { concept: "Auth Failures", count: 12, severity: "high" },
  { concept: "Data Validation", count: 89, severity: "low" },
];

export const Agents = () => {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

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
          <Button variant="hero" size="sm">
            <Bot className="h-4 w-4 mr-2" />
            Deploy New Agent
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: "Total Agents", value: "9", icon: Bot },
            { label: "Active", value: "6", icon: Activity },
            { label: "Corrections Today", value: "147", icon: CheckCircle2 },
            { label: "Avg Response", value: "1.2s", icon: Clock },
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
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
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
                    <div className="space-y-2">
                      {memorySummary.map((item) => (
                        <div key={item.concept} className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                          <span className="text-sm">{item.concept}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">{item.count}</span>
                            <Badge 
                              variant="outline" 
                              className={cn(
                                "text-xs",
                                item.severity === "high" && "text-red-400 border-red-400/30",
                                item.severity === "medium" && "text-amber-400 border-amber-400/30",
                                item.severity === "low" && "text-green-400 border-green-400/30"
                              )}
                            >
                              {item.severity}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recent Trace */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <GitBranch className="h-4 w-4 text-primary" />
                      <h3 className="font-semibold">Recent ToT Trace</h3>
                    </div>
                    <div className="space-y-2">
                      {traceSteps.map((step, i) => (
                        <div key={step.step} className="relative">
                          {i < traceSteps.length - 1 && (
                            <div className="absolute left-[11px] top-6 h-full w-0.5 bg-border" />
                          )}
                          <div className="flex gap-3">
                            <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 z-10">
                              <CheckCircle2 className="h-3 w-3 text-primary" />
                            </div>
                            <div className="flex-1 pb-4">
                              <div className="flex items-center justify-between">
                                <span className="font-medium text-sm">{step.step}</span>
                                <span className="text-xs text-muted-foreground">{step.time}</span>
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">{step.details}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </ScrollArea>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Agents;

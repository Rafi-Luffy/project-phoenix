import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { 
  Bot, 
  Shield, 
  Clock, 
  Cpu,
  HardDrive,
  TrendingUp,
  Activity,
  GitBranch,
  PlusCircle,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Play,
  ExternalLink,
  Radio,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area
} from "recharts";
import { LiveActivityFeed } from "@/components/console/LiveActivityFeed";
import { LiveIncidentStream } from "@/components/console/LiveIncidentStream";
import { useLiveMetrics, useRealtimeChartData } from "@/hooks/useRealtimeData";
import { useUser } from "@clerk/clerk-react";

const WS_BACKEND = "ws://localhost:8000/ws";

// Connects to backend WebSocket — streams live fault/heal events from any connected agent
type GameLogEntry = {
  id: number;
  time: string;
  type: "anomaly" | "correction" | "move" | "start" | "stop" | "info";
  summary: string;
  code?: string;
};

const useAgentEventLog = () => {
  const [entries, setEntries] = useState<GameLogEntry[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const idRef = useRef(0);

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(WS_BACKEND);
        wsRef.current = ws;

        ws.onopen = () => setConnected(true);
        ws.onclose = () => {
          setConnected(false);
          setTimeout(connect, 5000);
        };
        ws.onerror = () => { ws.close(); };

        ws.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            const type_raw: string = data.type ?? data.event ?? "";
            let type: GameLogEntry["type"] = "info";
            let summary = "";
            let code: string | undefined;

            if (type_raw === "anomaly_detected" || type_raw === "injection_confirmed") {
              type = "anomaly";
              const label = data.injection_type ?? data.anomaly_type ?? "UNKNOWN_FAULT";
              code = `ERR::0x${Math.floor(Math.random() * 0xFFFFFFFF).toString(16).toUpperCase().padStart(8, "0")}`;
              summary = `Fault detected — ${String(label).replaceAll("_", " ")} [${code}]`;
            } else if (type_raw === "correction") {
              type = "correction";
              summary = `Correction applied — ${String(data.explanation ?? "anomaly resolved")}`;
            } else if (type_raw === "healed") {
              type = "correction";
              const ms = data.recovery_time_ms ? ` in ${data.recovery_time_ms}ms` : "";
              summary = `Self-healed${ms} — system restored`;
            } else if (type_raw === "incident") {
              type = "info";
              summary = String(data.message ?? "Healing step");
            } else if (type_raw === "game_started") {
              type = "start"; summary = "Agent session started";
            } else if (type_raw === "game_over" || type_raw === "reset") {
              type = "stop"; summary = "Agent session ended";
            } else {
              return; // skip moves / thinking / metrics — too noisy
            }

            const now = new Date();
            const time = `${now.getHours().toString().padStart(2,"0")}:${now.getMinutes().toString().padStart(2,"0")}:${now.getSeconds().toString().padStart(2,"0")}`;
            setEntries(prev => [{ id: ++idRef.current, time, type, summary, code }, ...prev].slice(0, 60));
          } catch { /* ignore malformed */ }
        };
      } catch { /* ignore if ws unavailable */ }
    };

    connect();
    return () => { wsRef.current?.close(); };
  }, []);

  return { entries, connected };
};

const iconForType = (type: GameLogEntry["type"]) => {
  switch (type) {
    case "anomaly": return <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0" />;
    case "correction": return <CheckCircle2 className="h-3.5 w-3.5 text-green-400 shrink-0" />;
    case "start": return <Play className="h-3.5 w-3.5 text-primary shrink-0" />;
    case "stop": return <Shield className="h-3.5 w-3.5 text-rose-400 shrink-0" />;
    case "move": return <Zap className="h-3.5 w-3.5 text-blue-400 shrink-0" />;
    default: return <Activity className="h-3.5 w-3.5 text-muted-foreground shrink-0" />;
  }
};

const AgentEventLog = ({ entries, connected }: { entries: GameLogEntry[]; connected: boolean }) => {
  return (
    <Card className="bg-card border-border h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Agent Event Log
          </CardTitle>
          <p className="text-xs text-muted-foreground mt-0.5">
            Live fault detections &amp; self-healing events from connected agents
          </p>
        </div>
        <Badge variant="outline" className="text-xs shrink-0">
          <span className={`h-1.5 w-1.5 rounded-full mr-1.5 ${connected ? "bg-green-500 animate-pulse" : "bg-muted-foreground"}`} />
          {connected ? "Connected" : "Offline"}
        </Badge>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        {entries.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-muted-foreground text-sm gap-2 px-4 text-center">
            <Shield className="h-8 w-8 opacity-20" />
            <p>No events yet. Add your agents, start a session, and inject faults — self-healing events will stream here in real time.</p>
          </div>
        ) : (
          <div className="overflow-y-auto max-h-80 divide-y divide-border">
            {entries.map(entry => (
              <div key={entry.id} className="flex items-start gap-2.5 px-4 py-2.5 hover:bg-muted/20 transition-colors">
                <div className="mt-0.5">{iconForType(entry.type)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-foreground leading-snug">{entry.summary}</p>
                  {entry.code && (
                    <code className="text-[10px] text-amber-400/70 font-mono">{entry.code}</code>
                  )}
                </div>
                <span className="text-[10px] text-muted-foreground font-mono shrink-0">{entry.time}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};



// Minimal KPI card
const KPICard = ({ 
  title, 
  value, 
  icon: Icon, 
  delay,
  isEmpty = false
}: { 
  title: string; 
  value: string | number; 
  icon: React.ElementType;
  delay: number;
  isEmpty?: boolean;
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
  >
    <Card className="bg-card border-border hover:border-primary/30 transition-colors">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{title}</p>
            <motion.p 
              key={String(value)}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-3xl font-bold ${isEmpty ? "text-muted-foreground/40" : ""}`}
            >
              {isEmpty ? "—" : value}
            </motion.p>
            {isEmpty && <p className="text-xs text-muted-foreground/60">Connect agents to see data</p>}
          </div>
          <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);


export const Dashboard = () => {
  const metrics = useLiveMetrics();
  const { chartData } = useRealtimeChartData();
  const { user, isLoaded } = useUser();
  const { entries: logEntries, connected: backendConnected } = useAgentEventLog();

  const isConnectedUser = isLoaded && !!user;
  const displayName = user?.firstName || user?.emailAddresses?.[0]?.emailAddress || "User";

  // Show as "live" when backend is connected and streaming events from chess testbed
  const hasAgents = metrics.activeAgents > 0 || (backendConnected && logEntries.length > 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            {isConnectedUser ? `Welcome back, ${displayName}` : "Dashboard"}
          </h1>
          <p className="text-muted-foreground">
            {hasAgents
              ? "Live agent monitoring \u2022 Phoenix AI active"
              : "Connect your first agent to start monitoring"}
          </p>
        </div>
        <Badge variant="outline" className="text-xs">
          <span className={`h-1.5 w-1.5 rounded-full mr-1.5 ${hasAgents ? "bg-green-500 animate-pulse" : "bg-muted-foreground"}`} />
          {hasAgents ? "Live" : "Idle"}
        </Badge>
      </div>

      {/* Empty state banner — shows connection steps */}
      {!hasAgents && isConnectedUser && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-5 rounded-xl border border-dashed border-primary/30 bg-primary/5"
        >
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center mt-0.5 shrink-0">
                <Bot className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">No agents connected yet</p>
                <p className="text-sm text-muted-foreground mb-3">
                  Follow these steps to see live fault detection &amp; self-healing events on this dashboard:
                </p>
                <div className="flex flex-col gap-1.5 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="h-5 w-5 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center font-bold shrink-0">1</span>
                    <span className="text-muted-foreground">Go to <a href="/console/agents" className="text-primary hover:underline">Agents</a> and add an agent (name it anything — Planner, Monitor, etc.)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="h-5 w-5 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center font-bold shrink-0">2</span>
                    <span className="text-muted-foreground">Start the backend: <code className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">python src/backend/chess_app.py</code></span>
                    {backendConnected && <span className="text-green-400 text-xs font-medium">✓ Connected</span>}
                    {!backendConnected && <span className="text-muted-foreground/60 text-xs">(offline)</span>}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="h-5 w-5 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center font-bold shrink-0">3</span>
                    <span className="text-muted-foreground">Open the Chess Testbed → inject faults → events stream here automatically</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              <a href="/console/agents">
                <button className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition-colors">
                  <PlusCircle className="h-4 w-4" />
                  Add Agent
                </button>
              </a>
              <a href="http://localhost:8081" target="_blank" rel="noreferrer">
                <button className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  backendConnected
                    ? "bg-green-500/10 text-green-400 hover:bg-green-500/20 border border-green-500/20"
                    : "bg-muted/50 text-muted-foreground cursor-not-allowed"
                }`}>
                  <ExternalLink className="h-4 w-4" />
                  Launch Chess Testbed
                </button>
              </a>
            </div>
          </div>
        </motion.div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Active Agents"    value={metrics.activeAgents}   icon={Bot}      delay={0}    isEmpty={!hasAgents} />
        <KPICard title="Self-Healed (24h)" value={metrics.incidentsToday} icon={Shield}   delay={0.1}  isEmpty={!hasAgents} />
        <KPICard title="Success Rate"     value={metrics.successRate > 0 ? `${metrics.successRate.toFixed(1)}%` : "0%"} icon={TrendingUp} delay={0.2} isEmpty={!hasAgents} />
        <KPICard title="Avg Response"     value={metrics.avgResponseTime > 0 ? `${metrics.avgResponseTime.toFixed(1)}s` : "0s"} icon={Clock} delay={0.3} isEmpty={!hasAgents} />
      </div>

      {/* System Health */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
      >
        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            {hasAgents ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
                  <div className="h-10 w-10 rounded-lg bg-green-500 flex items-center justify-center">
                    <Cpu className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">CPU Usage</span>
                      <span className="text-sm font-bold">{metrics.cpuUsage.toFixed(0)}%</span>
                    </div>
                    <Progress value={metrics.cpuUsage} className="h-1.5" />
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
                  <div className="h-10 w-10 rounded-lg bg-green-500 flex items-center justify-center">
                    <HardDrive className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">Memory Usage</span>
                      <span className="text-sm font-bold">{metrics.memoryUsage.toFixed(0)}%</span>
                    </div>
                    <Progress value={metrics.memoryUsage} className="h-1.5" />
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-muted-foreground text-sm">
                <Activity className="h-8 w-8 mb-2 opacity-20" />
                <p>No agent health data available yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Area Chart - Live Incidents */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="lg:col-span-2"
        >
          <Card className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg">Incidents vs Time</CardTitle>
              <Badge variant="outline" className="text-xs">
                <span className={`h-1.5 w-1.5 rounded-full mr-1.5 ${hasAgents ? "bg-green-500 animate-pulse" : "bg-muted-foreground"}`} />
                {hasAgents ? "Real-time" : "Awaiting agents"}
              </Badge>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="incidentGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(25, 95%, 53%)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(25, 95%, 53%)" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="resolvedGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(142, 76%, 45%)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(142, 76%, 45%)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 20%)" />
                    <XAxis dataKey="time" stroke="hsl(30, 10%, 60%)" fontSize={12} />
                    <YAxis stroke="hsl(30, 10%, 60%)" fontSize={12} />
                    <Tooltip contentStyle={{ backgroundColor: "hsl(0, 0%, 10%)", border: "1px solid hsl(0, 0%, 20%)", borderRadius: "8px" }} />
                    <Legend />
                    <Area type="monotone" dataKey="incidents" stroke="hsl(25, 95%, 53%)" strokeWidth={2} fill="url(#incidentGradient)" name="Incidents" />
                    <Area type="monotone" dataKey="resolved" stroke="hsl(142, 76%, 45%)" strokeWidth={2} fill="url(#resolvedGradient)" name="Resolved" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions / Empty State */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { label: "Build Agent", desc: "Create and configure a custom agent", href: "/console/builder", icon: Bot },
                { label: "View Agents", desc: "Manage your deployed agents", href: "/console/agents", icon: Activity },
                { label: "Pipelines", desc: "Configure agent pipelines", href: "/console/pipelines", icon: GitBranch },
                { label: "Chess Testbed", desc: "Open the live fault-injection testbed", href: "http://localhost:8081", icon: Radio, external: true },
              ].map((a) => (
                <a key={a.label} href={a.href} target={'external' in a && a.external ? '_blank' : undefined} rel={'external' in a && a.external ? 'noreferrer' : undefined} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 border border-border hover:border-primary/30 transition-colors group">
                  <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
                    <a.icon className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{a.label}</p>
                    <p className="text-xs text-muted-foreground">{a.desc}</p>
                  </div>
                </a>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live Activity Feed */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg">Live Activity</CardTitle>
              <Badge variant="outline" className="text-xs">
                <span className={`h-1.5 w-1.5 rounded-full mr-1.5 ${hasAgents ? "bg-green-500 animate-pulse" : "bg-muted-foreground"}`} />
                {hasAgents ? "Streaming" : "Idle"}
              </Badge>
            </CardHeader>
            <CardContent className="p-0">
              <LiveActivityFeed maxItems={6} />
            </CardContent>
          </Card>
        </motion.div>

        {/* Live Incident Stream */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg">Incident Stream</CardTitle>
              <Badge variant="outline" className="text-xs">
                <span className={`h-1.5 w-1.5 rounded-full mr-1.5 ${hasAgents ? "bg-amber-500 animate-pulse" : "bg-muted-foreground"}`} />
                {hasAgents ? "Monitoring" : "Idle"}
              </Badge>
            </CardHeader>
            <CardContent>
              <LiveIncidentStream />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Agent Event Log — live fault/heal stream from backend */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        <AgentEventLog entries={logEntries} connected={backendConnected} />
      </motion.div>
    </div>
  );
};

export default Dashboard;

import { motion } from "framer-motion";
import { 
  Bot, 
  Shield, 
  Clock, 
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Cpu,
  HardDrive,
  TrendingUp,
  Activity,
  Cloud,
  CheckCircle2,
  Server,
  GitBranch,
  Database,
  Network
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
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
import { useEffect, useState } from "react";

// Get user auth data
const getUserData = () => {
  try {
    const auth = localStorage.getItem("phoenix_auth");
    if (auth) {
      return JSON.parse(auth);
    }
  } catch {
    return null;
  }
  return null;
};

// KPI Card Component with live data
const KPICard = ({ 
  title, 
  value, 
  change, 
  trend, 
  icon: Icon, 
  delay,
  isLive = false
}: { 
  title: string; 
  value: string | number; 
  change: string; 
  trend: "up" | "down"; 
  icon: React.ElementType;
  delay: number;
  isLive?: boolean;
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
            <div className="flex items-center gap-2">
              <p className="text-sm text-muted-foreground">{title}</p>
              {isLive && (
                <span className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
              )}
            </div>
            <motion.p 
              key={value}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl font-bold"
            >
              {value}
            </motion.p>
            <div className="flex items-center gap-1">
              {trend === "up" ? (
                <ArrowUpRight className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowDownRight className="h-4 w-4 text-red-500" />
              )}
              <span className={trend === "up" ? "text-green-500 text-sm" : "text-red-500 text-sm"}>
                {change}
              </span>
              <span className="text-muted-foreground text-sm">vs last 24h</span>
            </div>
          </div>
          <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

// System Health Card
const SystemHealthCard = ({ 
  title, 
  value, 
  icon: Icon,
  color 
}: { 
  title: string; 
  value: number; 
  icon: React.ElementType;
  color: string;
}) => (
  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
    <div className={`h-10 w-10 rounded-lg ${color} flex items-center justify-center`}>
      <Icon className="h-5 w-5 text-white" />
    </div>
    <div className="flex-1">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium">{title}</span>
        <span className="text-sm font-bold">{value.toFixed(0)}%</span>
      </div>
      <Progress value={value} className="h-1.5" />
    </div>
  </div>
);

// Connected System Card
const ConnectedSystemCard = ({ 
  name, 
  status, 
  icon: Icon,
  delay 
}: { 
  name: string; 
  status: "connected" | "syncing" | "warning";
  icon: React.ElementType;
  delay: number;
}) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3, delay }}
    className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 border border-border hover:border-primary/30 transition-colors"
  >
    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
      <Icon className="h-5 w-5 text-primary" />
    </div>
    <div className="flex-1">
      <span className="text-sm font-medium">{name}</span>
      <div className="flex items-center gap-1 mt-0.5">
        <span className={`h-1.5 w-1.5 rounded-full ${
          status === "connected" ? "bg-green-500" : 
          status === "syncing" ? "bg-amber-500 animate-pulse" : 
          "bg-red-500"
        }`} />
        <span className="text-xs text-muted-foreground capitalize">{status}</span>
      </div>
    </div>
    <CheckCircle2 className={`h-4 w-4 ${
      status === "connected" ? "text-green-500" : "text-muted-foreground"
    }`} />
  </motion.div>
);

const strategyData = [
  { strategy: "Rule-Based", success: 92, failed: 8 },
  { strategy: "ML-Driven", success: 87, failed: 13 },
  { strategy: "Hybrid", success: 96, failed: 4 },
  { strategy: "ToT", success: 94, failed: 6 },
];

const errorCategories = [
  { name: "API Errors", value: 35, color: "hsl(25, 95%, 53%)" },
  { name: "Code Logic", value: 28, color: "hsl(35, 100%, 50%)" },
  { name: "Data Issues", value: 20, color: "hsl(43, 96%, 56%)" },
  { name: "User Flow", value: 12, color: "hsl(15, 90%, 55%)" },
  { name: "Other", value: 5, color: "hsl(0, 0%, 40%)" },
];

const connectedSystems = [
  { name: "AWS Lambda", status: "connected" as const, icon: Cloud },
  { name: "Azure Functions", status: "connected" as const, icon: Server },
  { name: "Kubernetes", status: "syncing" as const, icon: Network },
  { name: "Docker Swarm", status: "connected" as const, icon: Database },
  { name: "GitHub Actions", status: "connected" as const, icon: GitBranch },
  { name: "Slack Alerts", status: "connected" as const, icon: Zap },
];

export const Dashboard = () => {
  const metrics = useLiveMetrics();
  const chartData = useRealtimeChartData();
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    setUserData(getUserData());
  }, []);

  const isConnectedUser = userData?.isConnected || userData?.userType === "connected";
  const connectedStats = userData?.stats || {
    activeAgents: 12,
    incidentsResolved: 1247,
    activePipelines: 8,
    memoryNodes: 2534,
    uptime: 99.98
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            {isConnectedUser ? `Welcome back, ${userData?.displayName || "Team"}` : "Dashboard"}
          </h1>
          <p className="text-muted-foreground">
            {isConnectedUser ? "All systems operational • 6 integrations connected" : "Real-time monitoring and analytics"}
          </p>
        </div>
        <Badge variant="outline" className="text-xs">
          <span className="h-1.5 w-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse" />
          Live Updates
        </Badge>
      </div>

      {/* Connected Systems Banner (for connected user) */}
      {isConnectedUser && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-xl bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10 border border-primary/30"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <CheckCircle2 className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">Production Environment Connected</p>
                <p className="text-sm text-muted-foreground">
                  {connectedStats.uptime}% uptime • {connectedStats.incidentsResolved.toLocaleString()} incidents auto-resolved
                </p>
              </div>
            </div>
            <Badge className="bg-green-500/20 text-green-500 border-green-500/30">
              All Systems Go
            </Badge>
          </div>
        </motion.div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Active Agents"
          value={isConnectedUser ? connectedStats.activeAgents : metrics.activeAgents}
          change={isConnectedUser ? "+2" : "+3"}
          trend="up"
          icon={Bot}
          delay={0}
          isLive
        />
        <KPICard
          title="Self-Healed (24h)"
          value={isConnectedUser ? 156 : metrics.incidentsToday}
          change={isConnectedUser ? "+34%" : "+23%"}
          trend="up"
          icon={Shield}
          delay={0.1}
          isLive
        />
        <KPICard
          title="Success Rate"
          value={isConnectedUser ? "99.4%" : `${metrics.successRate.toFixed(1)}%`}
          change={isConnectedUser ? "+0.8%" : "+2.3%"}
          trend="up"
          icon={TrendingUp}
          delay={0.2}
          isLive
        />
        <KPICard
          title="Avg Response Time"
          value={isConnectedUser ? "0.8s" : `${metrics.avgResponseTime.toFixed(1)}s`}
          change="-15%"
          trend="down"
          icon={Clock}
          delay={0.3}
          isLive
        />
      </div>

      {/* Connected Systems Grid (for connected user) */}
      {isConnectedUser && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.35 }}
        >
          <Card className="bg-card border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <Network className="h-5 w-5 text-primary" />
                Connected Integrations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {connectedSystems.map((system, index) => (
                  <ConnectedSystemCard
                    key={system.name}
                    name={system.name}
                    status={system.status}
                    icon={system.icon}
                    delay={0.4 + index * 0.05}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SystemHealthCard 
                title="CPU Usage" 
                value={isConnectedUser ? 42 : metrics.cpuUsage} 
                icon={Cpu}
                color={isConnectedUser ? "bg-green-500" : (metrics.cpuUsage > 80 ? "bg-red-500" : metrics.cpuUsage > 60 ? "bg-amber-500" : "bg-green-500")}
              />
              <SystemHealthCard 
                title="Memory Usage" 
                value={isConnectedUser ? 58 : metrics.memoryUsage} 
                icon={HardDrive}
                color={isConnectedUser ? "bg-green-500" : (metrics.memoryUsage > 80 ? "bg-red-500" : metrics.memoryUsage > 60 ? "bg-amber-500" : "bg-green-500")}
              />
            </div>
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
                <span className="h-1.5 w-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse" />
                Real-time
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
                    <XAxis 
                      dataKey="time" 
                      stroke="hsl(30, 10%, 60%)"
                      fontSize={12}
                    />
                    <YAxis 
                      stroke="hsl(30, 10%, 60%)"
                      fontSize={12}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "hsl(0, 0%, 10%)", 
                        border: "1px solid hsl(0, 0%, 20%)",
                        borderRadius: "8px"
                      }}
                    />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="incidents" 
                      stroke="hsl(25, 95%, 53%)" 
                      strokeWidth={2}
                      fill="url(#incidentGradient)"
                      name="Incidents"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="resolved" 
                      stroke="hsl(142, 76%, 45%)" 
                      strokeWidth={2}
                      fill="url(#resolvedGradient)"
                      name="Resolved"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Pie Chart - Error Categories */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader>
              <CardTitle className="text-lg">Error Categories</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[260px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={errorCategories}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {errorCategories.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "hsl(0, 0%, 10%)", 
                        border: "1px solid hsl(0, 0%, 20%)",
                        borderRadius: "8px"
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {errorCategories.slice(0, 4).map((cat) => (
                  <div key={cat.name} className="flex items-center gap-2 text-xs">
                    <div 
                      className="h-2 w-2 rounded-full" 
                      style={{ backgroundColor: cat.color }}
                    />
                    <span className="text-muted-foreground">{cat.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bar Chart - Strategy Success Rates */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader>
              <CardTitle className="text-lg">Strategy Success Rates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[260px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={strategyData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 20%)" />
                    <XAxis 
                      type="number" 
                      domain={[0, 100]}
                      stroke="hsl(30, 10%, 60%)"
                      fontSize={12}
                    />
                    <YAxis 
                      type="category" 
                      dataKey="strategy" 
                      stroke="hsl(30, 10%, 60%)"
                      fontSize={12}
                      width={80}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "hsl(0, 0%, 10%)", 
                        border: "1px solid hsl(0, 0%, 20%)",
                        borderRadius: "8px"
                      }}
                    />
                    <Bar 
                      dataKey="success" 
                      fill="hsl(25, 95%, 53%)" 
                      radius={[0, 4, 4, 0]}
                      name="Success %"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Live Activity Feed */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg">Live Activity</CardTitle>
              <Badge variant="outline" className="text-xs">
                <span className="h-1.5 w-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse" />
                Streaming
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
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <Card className="bg-card border-border h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg">Incident Stream</CardTitle>
              <Badge variant="outline" className="text-xs">
                <span className="h-1.5 w-1.5 bg-amber-500 rounded-full mr-1.5 animate-pulse" />
                Monitoring
              </Badge>
            </CardHeader>
            <CardContent>
              <LiveIncidentStream />
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;

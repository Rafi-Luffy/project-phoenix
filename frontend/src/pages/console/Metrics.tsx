import { motion } from "framer-motion";
import { 
  Activity, 
  TrendingUp,
  TrendingDown,
  Clock,
  Zap,
  Server,
  Cpu,
  MemoryStick,
  HardDrive
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const latencyData = [
  { time: "00:00", p50: 45, p95: 120, p99: 250 },
  { time: "04:00", p50: 42, p95: 115, p99: 230 },
  { time: "08:00", p50: 55, p95: 145, p99: 280 },
  { time: "12:00", p50: 68, p95: 180, p99: 350 },
  { time: "16:00", p50: 52, p95: 140, p99: 270 },
  { time: "20:00", p50: 48, p95: 125, p99: 240 },
  { time: "Now", p50: 46, p95: 118, p99: 235 },
];

const throughputData = [
  { time: "00:00", requests: 1200, tokens: 45000 },
  { time: "04:00", requests: 800, tokens: 32000 },
  { time: "08:00", requests: 2500, tokens: 98000 },
  { time: "12:00", requests: 4200, tokens: 165000 },
  { time: "16:00", requests: 3800, tokens: 148000 },
  { time: "20:00", requests: 2100, tokens: 82000 },
  { time: "Now", requests: 1800, tokens: 71000 },
];

const systemMetrics = [
  { name: "CPU Usage", value: 42, max: 100, unit: "%", icon: Cpu, trend: "up", change: "+5%" },
  { name: "Memory", value: 6.8, max: 16, unit: "GB", icon: MemoryStick, trend: "stable", change: "0%" },
  { name: "Storage", value: 124, max: 500, unit: "GB", icon: HardDrive, trend: "up", change: "+2%" },
  { name: "Network", value: 245, max: 1000, unit: "Mbps", icon: Activity, trend: "down", change: "-12%" },
];

const agentMetrics = [
  { agent: "Planner-01", latency: "45ms", throughput: "1.2k/hr", errors: 0, corrections: 12 },
  { agent: "Executor-01", latency: "120ms", throughput: "890/hr", errors: 2, corrections: 45 },
  { agent: "Executor-02", latency: "115ms", throughput: "920/hr", errors: 1, corrections: 38 },
  { agent: "Critic-01", latency: "85ms", throughput: "1.5k/hr", errors: 0, corrections: 8 },
  { agent: "Monitor-01", latency: "25ms", throughput: "3.2k/hr", errors: 0, corrections: 3 },
];

export default function Metrics() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">Metrics</h1>
        <p className="text-muted-foreground">System performance and agent analytics</p>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {systemMetrics.map((metric, i) => (
          <motion.div
            key={metric.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                      <metric.icon className="h-4 w-4 text-primary" />
                    </div>
                    <span className="text-sm font-medium">{metric.name}</span>
                  </div>
                  <div className={`flex items-center gap-1 text-xs ${
                    metric.trend === 'up' ? 'text-amber-500' : 
                    metric.trend === 'down' ? 'text-green-500' : 
                    'text-muted-foreground'
                  }`}>
                    {metric.trend === 'up' ? <TrendingUp className="h-3 w-3" /> : 
                     metric.trend === 'down' ? <TrendingDown className="h-3 w-3" /> : null}
                    {metric.change}
                  </div>
                </div>
                <div className="flex items-end gap-1 mb-2">
                  <span className="text-2xl font-bold">{metric.value}</span>
                  <span className="text-muted-foreground text-sm mb-0.5">/ {metric.max} {metric.unit}</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-500"
                    style={{ width: `${(metric.value / metric.max) * 100}%` }}
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Latency Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="h-5 w-5 text-primary" />
                Response Latency
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={latencyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 20%)" />
                    <XAxis dataKey="time" stroke="hsl(30, 10%, 60%)" fontSize={12} />
                    <YAxis stroke="hsl(30, 10%, 60%)" fontSize={12} unit="ms" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "hsl(0, 0%, 10%)", 
                        border: "1px solid hsl(0, 0%, 20%)",
                        borderRadius: "8px"
                      }}
                    />
                    <Line type="monotone" dataKey="p50" stroke="hsl(142, 76%, 45%)" strokeWidth={2} name="P50" />
                    <Line type="monotone" dataKey="p95" stroke="hsl(35, 100%, 50%)" strokeWidth={2} name="P95" />
                    <Line type="monotone" dataKey="p99" stroke="hsl(0, 84%, 60%)" strokeWidth={2} name="P99" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-green-500" />
                  <span className="text-sm text-muted-foreground">P50</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-amber-500" />
                  <span className="text-sm text-muted-foreground">P95</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <span className="text-sm text-muted-foreground">P99</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Throughput Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                Throughput
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={throughputData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 20%)" />
                    <XAxis dataKey="time" stroke="hsl(30, 10%, 60%)" fontSize={12} />
                    <YAxis stroke="hsl(30, 10%, 60%)" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "hsl(0, 0%, 10%)", 
                        border: "1px solid hsl(0, 0%, 20%)",
                        borderRadius: "8px"
                      }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="requests" 
                      stroke="hsl(25, 95%, 53%)" 
                      fill="hsl(25, 95%, 53% / 0.2)"
                      strokeWidth={2}
                      name="Requests/hr"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Agent Metrics Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Server className="h-5 w-5 text-primary" />
              Agent Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Agent</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Avg Latency</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Throughput</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Errors</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Corrections</th>
                  </tr>
                </thead>
                <tbody>
                  {agentMetrics.map((metric) => (
                    <tr key={metric.agent} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                      <td className="py-3 px-4 font-medium">{metric.agent}</td>
                      <td className="py-3 px-4 text-green-500">{metric.latency}</td>
                      <td className="py-3 px-4">{metric.throughput}</td>
                      <td className="py-3 px-4">
                        <span className={metric.errors > 0 ? "text-red-500" : "text-green-500"}>
                          {metric.errors}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-primary">{metric.corrections}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

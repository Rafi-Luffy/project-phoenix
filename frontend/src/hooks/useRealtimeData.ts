import { useState, useEffect, useCallback } from "react";

// Types for real-time data
export interface AgentActivity {
  id: string;
  agentName: string;
  action: "detected" | "analyzed" | "patched" | "validated";
  title: string;
  timestamp: Date;
  severity: "low" | "medium" | "high" | "critical";
}

export interface IncidentStream {
  id: string;
  type: string;
  message: string;
  timestamp: Date;
  status: "open" | "investigating" | "resolved";
}

export interface LiveMetrics {
  activeAgents: number;
  incidentsToday: number;
  successRate: number;
  avgResponseTime: number;
  memoryUsage: number;
  cpuUsage: number;
}

// Simulated real-time data generator
const generateAgentActivity = (): AgentActivity => {
  const agents = ["Monitor-01", "Monitor-02", "Executor-01", "Executor-02", "Critic-01", "Critic-02"];
  const actions: AgentActivity["action"][] = ["detected", "analyzed", "patched", "validated"];
  const titles = [
    "API timeout in payment-service",
    "Null pointer exception in user-auth",
    "Rate limit exceeded in external-api",
    "Memory leak in cache-service",
    "Database connection pool exhausted",
    "Infinite loop in recommendation-engine",
    "SSL certificate expiring soon",
    "High latency in search-service",
    "Disk space warning on node-3",
    "Failed health check on worker-5",
  ];
  const severities: AgentActivity["severity"][] = ["low", "medium", "high", "critical"];

  return {
    id: `activity-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    agentName: agents[Math.floor(Math.random() * agents.length)],
    action: actions[Math.floor(Math.random() * actions.length)],
    title: titles[Math.floor(Math.random() * titles.length)],
    timestamp: new Date(),
    severity: severities[Math.floor(Math.random() * severities.length)],
  };
};

const generateIncident = (): IncidentStream => {
  const types = ["Error", "Warning", "Critical", "Info"];
  const messages = [
    "Service degradation detected",
    "Unusual traffic pattern identified",
    "Auto-scaling triggered",
    "Failover initiated",
    "Cache invalidated",
    "Configuration drift detected",
  ];
  const statuses: IncidentStream["status"][] = ["open", "investigating", "resolved"];

  return {
    id: `incident-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    type: types[Math.floor(Math.random() * types.length)],
    message: messages[Math.floor(Math.random() * messages.length)],
    timestamp: new Date(),
    status: statuses[Math.floor(Math.random() * statuses.length)],
  };
};

// Hook for simulated real-time agent activity
export const useRealtimeAgentActivity = (maxItems: number = 10) => {
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Simulate connection
    const connectTimeout = setTimeout(() => setIsConnected(true), 500);

    // Generate initial activities
    const initialActivities = Array.from({ length: 5 }, generateAgentActivity);
    setActivities(initialActivities);

    // Simulate real-time updates
    const interval = setInterval(() => {
      if (Math.random() > 0.3) { // 70% chance of new activity
        setActivities((prev) => {
          const newActivity = generateAgentActivity();
          const updated = [newActivity, ...prev];
          return updated.slice(0, maxItems);
        });
      }
    }, 3000); // New activity every 3 seconds

    return () => {
      clearTimeout(connectTimeout);
      clearInterval(interval);
    };
  }, [maxItems]);

  return { activities, isConnected };
};

// Hook for simulated real-time incident stream
export const useRealtimeIncidents = (maxItems: number = 5) => {
  const [incidents, setIncidents] = useState<IncidentStream[]>([]);

  useEffect(() => {
    // Generate initial incidents
    const initialIncidents = Array.from({ length: 3 }, generateIncident);
    setIncidents(initialIncidents);

    // Simulate real-time updates
    const interval = setInterval(() => {
      if (Math.random() > 0.5) { // 50% chance of new incident
        setIncidents((prev) => {
          const newIncident = generateIncident();
          const updated = [newIncident, ...prev];
          return updated.slice(0, maxItems);
        });
      }
    }, 5000); // New incident every 5 seconds

    return () => clearInterval(interval);
  }, [maxItems]);

  const resolveIncident = useCallback((id: string) => {
    setIncidents((prev) =>
      prev.map((incident) =>
        incident.id === id ? { ...incident, status: "resolved" as const } : incident
      )
    );
  }, []);

  return { incidents, resolveIncident };
};

// Hook for simulated live metrics
export const useLiveMetrics = () => {
  const [metrics, setMetrics] = useState<LiveMetrics>({
    activeAgents: 24,
    incidentsToday: 147,
    successRate: 98.5,
    avgResponseTime: 1.2,
    memoryUsage: 67,
    cpuUsage: 45,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        activeAgents: prev.activeAgents + (Math.random() > 0.8 ? (Math.random() > 0.5 ? 1 : -1) : 0),
        incidentsToday: prev.incidentsToday + (Math.random() > 0.5 ? 1 : 0),
        successRate: Math.min(100, Math.max(95, prev.successRate + (Math.random() - 0.5) * 0.5)),
        avgResponseTime: Math.max(0.5, prev.avgResponseTime + (Math.random() - 0.5) * 0.2),
        memoryUsage: Math.min(95, Math.max(30, prev.memoryUsage + (Math.random() - 0.5) * 5)),
        cpuUsage: Math.min(90, Math.max(20, prev.cpuUsage + (Math.random() - 0.5) * 8)),
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return metrics;
};

// Hook for chart data that updates in real-time
export const useRealtimeChartData = () => {
  const [chartData, setChartData] = useState([
    { time: "00:00", incidents: 3, resolved: 3 },
    { time: "04:00", incidents: 5, resolved: 5 },
    { time: "08:00", incidents: 12, resolved: 11 },
    { time: "12:00", incidents: 8, resolved: 8 },
    { time: "16:00", incidents: 15, resolved: 14 },
    { time: "20:00", incidents: 7, resolved: 7 },
    { time: "Now", incidents: 4, resolved: 3 },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setChartData((prev) => {
        const updated = [...prev];
        const lastItem = { ...updated[updated.length - 1] };
        
        // Randomly update the "Now" data point
        lastItem.incidents = Math.max(1, lastItem.incidents + Math.floor((Math.random() - 0.4) * 3));
        lastItem.resolved = Math.min(lastItem.incidents, lastItem.resolved + (Math.random() > 0.3 ? 1 : 0));
        
        updated[updated.length - 1] = lastItem;
        return updated;
      });
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return chartData;
};

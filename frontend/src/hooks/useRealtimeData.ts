import { useState, useCallback } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────
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

// ─── Hooks ────────────────────────────────────────────────────────────────────

/**
 * Real-time agent activity feed.
 * Starts empty — data is populated when agents are connected and emit events.
 */
export const useRealtimeAgentActivity = (maxItems: number = 10) => {
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [isConnected] = useState(false);

  const addActivity = useCallback((activity: AgentActivity) => {
    setActivities((prev) => [activity, ...prev].slice(0, maxItems));
  }, [maxItems]);

  return { activities, isConnected, addActivity };
};

/**
 * Real-time incident stream.
 * Starts empty — incidents appear only when real agents report them.
 */
export const useRealtimeIncidents = (maxItems: number = 5) => {
  const [incidents, setIncidents] = useState<IncidentStream[]>([]);

  const resolveIncident = useCallback((id: string) => {
    setIncidents((prev) =>
      prev.map((inc) =>
        inc.id === id ? { ...inc, status: "resolved" as const } : inc
      )
    );
  }, []);

  const addIncident = useCallback((incident: IncidentStream) => {
    setIncidents((prev) => [incident, ...prev].slice(0, maxItems));
  }, [maxItems]);

  return { incidents, resolveIncident, addIncident };
};

/**
 * Live system metrics.
 * All start at 0 for new users — real values come from connected agents.
 */
export const useLiveMetrics = () => {
  const [metrics, setMetrics] = useState<LiveMetrics>({
    activeAgents: 0,
    incidentsToday: 0,
    successRate: 0,
    avgResponseTime: 0,
    memoryUsage: 0,
    cpuUsage: 0,
  });

  const updateMetrics = useCallback((patch: Partial<LiveMetrics>) => {
    setMetrics((prev) => ({ ...prev, ...patch }));
  }, []);

  return { ...metrics, updateMetrics };
};

/**
 * Real-time chart data for incidents vs time.
 * Starts with empty timeline — fills as real events arrive.
 */
export const useRealtimeChartData = () => {
  const now = new Date();
  const hours = Array.from({ length: 7 }, (_, i) => {
    const h = new Date(now.getTime() - (6 - i) * 4 * 3600 * 1000);
    return `${h.getHours().toString().padStart(2, "0")}:00`;
  });

  const [chartData, setChartData] = useState(
    hours.map((h, i) => ({ time: i === 6 ? "Now" : h, incidents: 0, resolved: 0 }))
  );

  const recordIncident = useCallback((resolved: boolean) => {
    setChartData((prev) => {
      const updated = [...prev];
      const last = { ...updated[updated.length - 1] };
      last.incidents += 1;
      if (resolved) last.resolved += 1;
      updated[updated.length - 1] = last;
      return updated;
    });
  }, []);

  return { chartData, recordIncident };
};

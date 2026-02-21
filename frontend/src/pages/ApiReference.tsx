import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, Code2, Copy, Check, Search,
  ChevronRight, Zap, Database, Shield, Cpu,
  Activity, MessageSquare, Brain, Heart
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const endpoints = [
  {
    category: "Agents",
    icon: Cpu,
    items: [
      { method: "POST", path: "/agents", description: "Create a new agent" },
      { method: "GET", path: "/agents", description: "List all agents" },
      { method: "GET", path: "/agents/:id", description: "Get agent by ID" },
      { method: "PATCH", path: "/agents/:id", description: "Update agent" },
      { method: "DELETE", path: "/agents/:id", description: "Delete agent" },
      { method: "POST", path: "/agents/:id/start", description: "Start agent" },
      { method: "POST", path: "/agents/:id/stop", description: "Stop agent" },
    ],
  },
  {
    category: "Memory",
    icon: Database,
    items: [
      { method: "GET", path: "/memory/:agentId", description: "Get agent memory" },
      { method: "POST", path: "/memory/:agentId", description: "Store memory" },
      { method: "DELETE", path: "/memory/:agentId", description: "Clear memory" },
      { method: "GET", path: "/memory/:agentId/search", description: "Search memory" },
    ],
  },
  {
    category: "Corrections",
    icon: Zap,
    items: [
      { method: "GET", path: "/corrections", description: "List corrections" },
      { method: "GET", path: "/corrections/:id", description: "Get correction details" },
      { method: "POST", path: "/corrections/:id/replay", description: "Replay correction" },
    ],
  },
  {
    category: "Auth",
    icon: Shield,
    items: [
      { method: "POST", path: "/auth/token", description: "Generate API token" },
      { method: "POST", path: "/auth/refresh", description: "Refresh token" },
      { method: "DELETE", path: "/auth/revoke", description: "Revoke token" },
    ],
  },
  {
    category: "Monitoring & Status",
    icon: Activity,
    items: [
      { method: "GET", path: "/status", description: "Get system status" },
      { method: "GET", path: "/health", description: "Health check" },
      { method: "GET", path: "/llm/health", description: "LLM service health" },
    ],
  },
  {
    category: "Metrics & Observability",
    icon: Heart,
    items: [
      { method: "GET", path: "/metrics", description: "Get system metrics" },
      { method: "GET", path: "/alerts", description: "Get active alerts" },
      { method: "GET", path: "/logs", description: "Get system logs" },
      { method: "GET", path: "/events", description: "Get system events" },
    ],
  },
  {
    category: "Messaging",
    icon: MessageSquare,
    items: [
      { method: "POST", path: "/messages", description: "Send message" },
      { method: "GET", path: "/messages/:id", description: "Get message by ID" },
    ],
  },
  {
    category: "LLM Integration",
    icon: Brain,
    items: [
      { method: "POST", path: "/llm/analyze_error", description: "Analyze error with LLM" },
      { method: "POST", path: "/llm/explain_correction", description: "Explain correction" },
      { method: "POST", path: "/llm/detect_patterns", description: "Detect patterns" },
      { method: "POST", path: "/llm/optimize", description: "Optimize with LLM" },
    ],
  },
  {
    category: "Agent Tasks",
    icon: Cpu,
    items: [
      { method: "POST", path: "/agents/:id/tasks", description: "Create agent task" },
    ],
  },
];

const methodColors: Record<string, string> = {
  GET: "text-emerald-400 bg-emerald-400/10",
  POST: "text-blue-400 bg-blue-400/10",
  PATCH: "text-amber-400 bg-amber-400/10",
  DELETE: "text-red-400 bg-red-400/10",
};

export default function ApiReference() {
  const [copiedPath, setCopiedPath] = useState<string | null>(null);

  const copyPath = (path: string) => {
    navigator.clipboard.writeText(path);
    setCopiedPath(path);
    setTimeout(() => setCopiedPath(null), 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Link
              to="/docs"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Docs
            </Link>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                <Code2 className="w-6 h-6 text-primary" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Reference</span>
                <h1 className="text-3xl md:text-4xl font-bold text-foreground">API Reference</h1>
              </div>
            </div>

            <p className="text-lg text-muted-foreground mb-8">
              Complete reference for the Phoenix REST API. All endpoints require authentication.
            </p>

            {/* Search */}
            <div className="relative max-w-md">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search endpoints..."
                className="h-12 pl-11 bg-muted/30 border-border focus:border-primary rounded-xl"
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Base URL */}
      <section className="pb-8 px-4">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-4 rounded-xl bg-muted/20 border border-border"
          >
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Base URL</span>
                <p className="font-mono text-foreground">https://api.phoenixruntime.dev/v1</p>
              </div>
              <button
                onClick={() => copyPath("https://api.phoenixruntime.dev/v1")}
                className="p-2 rounded-lg hover:bg-muted/50 transition-colors"
              >
                {copiedPath === "https://api.phoenixruntime.dev/v1" ? (
                  <Check className="w-4 h-4 text-primary" />
                ) : (
                  <Copy className="w-4 h-4 text-muted-foreground" />
                )}
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Endpoints */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-5xl">
          <div className="space-y-8">
            {endpoints.map((section, i) => (
              <motion.div
                key={section.category}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <section.icon className="w-5 h-5 text-primary" />
                  </div>
                  <h2 className="text-xl font-bold text-foreground">{section.category}</h2>
                </div>

                <div className="rounded-xl border border-border overflow-hidden">
                  {section.items.map((endpoint, j) => (
                    <div
                      key={j}
                      className={`flex items-center gap-4 p-4 hover:bg-muted/20 transition-colors cursor-pointer group ${
                        j !== section.items.length - 1 ? "border-b border-border" : ""
                      }`}
                    >
                      <span className={`px-2 py-1 rounded text-xs font-mono font-medium ${methodColors[endpoint.method]}`}>
                        {endpoint.method}
                      </span>
                      <code className="flex-1 font-mono text-sm text-foreground">{endpoint.path}</code>
                      <span className="text-sm text-muted-foreground hidden sm:block">{endpoint.description}</span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

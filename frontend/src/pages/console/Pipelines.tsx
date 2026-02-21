import { motion } from "framer-motion";
import { 
  GitBranch, 
  Play, 
  Pause,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowRight,
  MoreVertical,
  Plus
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const pipelines = [
  {
    id: "1",
    name: "Customer Support Pipeline",
    description: "Handle customer inquiries with escalation logic",
    status: "running",
    agents: ["Classifier", "Responder", "Escalator"],
    lastRun: "2 minutes ago",
    successRate: 98.5,
    avgDuration: "1.2s",
  },
  {
    id: "2",
    name: "Data Analysis Pipeline",
    description: "Process and analyze incoming data streams",
    status: "running",
    agents: ["Ingester", "Analyzer", "Reporter"],
    lastRun: "5 minutes ago",
    successRate: 99.1,
    avgDuration: "3.4s",
  },
  {
    id: "3",
    name: "Content Moderation",
    description: "Moderate user-generated content automatically",
    status: "paused",
    agents: ["Scanner", "Classifier", "Moderator"],
    lastRun: "1 hour ago",
    successRate: 97.8,
    avgDuration: "0.8s",
  },
  {
    id: "4",
    name: "Research Assistant",
    description: "Gather and synthesize research from multiple sources",
    status: "running",
    agents: ["Searcher", "Synthesizer", "Critic"],
    lastRun: "10 minutes ago",
    successRate: 95.2,
    avgDuration: "8.5s",
  },
  {
    id: "5",
    name: "Code Review Pipeline",
    description: "Automated code review and suggestions",
    status: "idle",
    agents: ["Parser", "Reviewer", "Suggester"],
    lastRun: "2 hours ago",
    successRate: 94.7,
    avgDuration: "2.1s",
  },
];

const statusConfig = {
  running: { color: "bg-green-500", label: "Running", icon: Play },
  paused: { color: "bg-yellow-500", label: "Paused", icon: Pause },
  idle: { color: "bg-muted-foreground", label: "Idle", icon: Clock },
  error: { color: "bg-red-500", label: "Error", icon: AlertCircle },
};

export default function Pipelines() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Pipelines</h1>
          <p className="text-muted-foreground">Orchestrate multi-agent workflows</p>
        </div>
        <Button className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          New Pipeline
        </Button>
      </div>

      {/* Pipeline Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Total Pipelines", value: "5", icon: GitBranch },
          { label: "Running", value: "3", icon: Play },
          { label: "Success Rate", value: "97.1%", icon: CheckCircle2 },
          { label: "Avg Duration", value: "3.2s", icon: Clock },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="bg-card border-border">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <stat.icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Pipelines List */}
      <div className="space-y-4">
        {pipelines.map((pipeline, i) => {
          const status = statusConfig[pipeline.status as keyof typeof statusConfig];
          const StatusIcon = status.icon;
          
          return (
            <motion.div
              key={pipeline.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="bg-card border-border hover:border-primary/30 transition-colors cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold">{pipeline.name}</h3>
                        <Badge 
                          variant="outline" 
                          className={`${pipeline.status === 'running' ? 'border-green-500/50 text-green-500' : 
                            pipeline.status === 'paused' ? 'border-yellow-500/50 text-yellow-500' : 
                            'border-muted-foreground/50 text-muted-foreground'}`}
                        >
                          <span className={`h-1.5 w-1.5 rounded-full ${status.color} mr-1.5 ${pipeline.status === 'running' ? 'animate-pulse' : ''}`} />
                          {status.label}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-4">{pipeline.description}</p>
                      
                      {/* Agent Flow */}
                      <div className="flex items-center gap-2 mb-4">
                        {pipeline.agents.map((agent, idx) => (
                          <div key={agent} className="flex items-center gap-2">
                            <span className="px-3 py-1 rounded-lg bg-muted text-sm font-medium">
                              {agent}
                            </span>
                            {idx < pipeline.agents.length - 1 && (
                              <ArrowRight className="h-4 w-4 text-muted-foreground" />
                            )}
                          </div>
                        ))}
                      </div>

                      {/* Stats */}
                      <div className="flex items-center gap-6 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          Last run: {pipeline.lastRun}
                        </span>
                        <span className="flex items-center gap-1">
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                          {pipeline.successRate}% success
                        </span>
                        <span>Avg: {pipeline.avgDuration}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {pipeline.status === 'running' ? (
                        <Button variant="outline" size="sm">
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm">
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

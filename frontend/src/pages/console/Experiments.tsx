import { useState } from "react";
import { motion } from "framer-motion";
import { 
  FlaskConical, 
  Play, 
  Pause, 
  RotateCcw,
  TrendingUp,
  Target,
  Clock,
  Layers,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Loader2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";

interface Experiment {
  id: string;
  name: string;
  status: "running" | "completed" | "failed" | "paused";
  progress: number;
  currentReward: number;
  bestReward: number;
  iterations: number;
  maxIterations: number;
  hyperparameters: {
    learningRate: number;
    batchSize: number;
    gamma: number;
    epsilon: number;
  };
  startTime: string;
  duration: string;
  policy: string;
}

const experiments: Experiment[] = [
  {
    id: "1",
    name: "API Resilience Optimization",
    status: "running",
    progress: 67,
    currentReward: 0.847,
    bestReward: 0.892,
    iterations: 6700,
    maxIterations: 10000,
    hyperparameters: { learningRate: 0.001, batchSize: 64, gamma: 0.99, epsilon: 0.1 },
    startTime: "2h 34m ago",
    duration: "2h 34m",
    policy: "PPO"
  },
  {
    id: "2",
    name: "Memory Management Policy",
    status: "completed",
    progress: 100,
    currentReward: 0.923,
    bestReward: 0.923,
    iterations: 10000,
    maxIterations: 10000,
    hyperparameters: { learningRate: 0.0005, batchSize: 128, gamma: 0.95, epsilon: 0.05 },
    startTime: "1d ago",
    duration: "4h 12m",
    policy: "A2C"
  },
  {
    id: "3",
    name: "Error Detection Tuning",
    status: "paused",
    progress: 34,
    currentReward: 0.654,
    bestReward: 0.712,
    iterations: 3400,
    maxIterations: 10000,
    hyperparameters: { learningRate: 0.002, batchSize: 32, gamma: 0.99, epsilon: 0.2 },
    startTime: "3h ago",
    duration: "1h 45m",
    policy: "DQN"
  },
  {
    id: "4",
    name: "Auth Flow Recovery",
    status: "failed",
    progress: 45,
    currentReward: 0.234,
    bestReward: 0.567,
    iterations: 4500,
    maxIterations: 10000,
    hyperparameters: { learningRate: 0.01, batchSize: 64, gamma: 0.9, epsilon: 0.15 },
    startTime: "5h ago",
    duration: "2h 10m",
    policy: "SAC"
  },
];

const rewardCurves: Record<string, { iteration: number; reward: number }[]> = {
  "1": [
    { iteration: 0, reward: 0.1 },
    { iteration: 1000, reward: 0.35 },
    { iteration: 2000, reward: 0.52 },
    { iteration: 3000, reward: 0.68 },
    { iteration: 4000, reward: 0.75 },
    { iteration: 5000, reward: 0.82 },
    { iteration: 6000, reward: 0.85 },
    { iteration: 6700, reward: 0.847 },
  ],
  "2": [
    { iteration: 0, reward: 0.12 },
    { iteration: 2000, reward: 0.45 },
    { iteration: 4000, reward: 0.67 },
    { iteration: 6000, reward: 0.82 },
    { iteration: 8000, reward: 0.89 },
    { iteration: 10000, reward: 0.923 },
  ],
  "3": [
    { iteration: 0, reward: 0.08 },
    { iteration: 1000, reward: 0.32 },
    { iteration: 2000, reward: 0.51 },
    { iteration: 3000, reward: 0.64 },
    { iteration: 3400, reward: 0.654 },
  ],
  "4": [
    { iteration: 0, reward: 0.15 },
    { iteration: 1000, reward: 0.42 },
    { iteration: 2000, reward: 0.56 },
    { iteration: 3000, reward: 0.48 },
    { iteration: 4000, reward: 0.32 },
    { iteration: 4500, reward: 0.234 },
  ],
};

export const Experiments = () => {
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment>(experiments[0]);

  const getStatusConfig = (status: Experiment["status"]) => {
    switch (status) {
      case "running": return { icon: Loader2, color: "text-blue-400", bg: "bg-blue-500/10", label: "Running", animate: true };
      case "completed": return { icon: CheckCircle2, color: "text-green-400", bg: "bg-green-500/10", label: "Completed", animate: false };
      case "paused": return { icon: Pause, color: "text-amber-400", bg: "bg-amber-500/10", label: "Paused", animate: false };
      case "failed": return { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10", label: "Failed", animate: false };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Experiments</h1>
          <p className="text-muted-foreground">RL training runs and policy optimization</p>
        </div>
        <Button variant="hero" size="sm">
          <FlaskConical className="h-4 w-4 mr-2" />
          New Experiment
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Experiment List */}
        <div className="space-y-3">
          {experiments.map((exp) => {
            const statusConfig = getStatusConfig(exp.status);
            const StatusIcon = statusConfig.icon;
            
            return (
              <motion.div
                key={exp.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <Card 
                  className={cn(
                    "bg-card border-border cursor-pointer transition-all hover:border-primary/30",
                    selectedExperiment.id === exp.id && "border-primary/50 bg-primary/5"
                  )}
                  onClick={() => setSelectedExperiment(exp)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className={cn("h-8 w-8 rounded-lg flex items-center justify-center", statusConfig.bg)}>
                          <StatusIcon className={cn("h-4 w-4", statusConfig.color, statusConfig.animate && "animate-spin")} />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{exp.name}</p>
                          <p className="text-xs text-muted-foreground">{exp.policy} Policy</p>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Progress</span>
                        <span>{exp.progress}%</span>
                      </div>
                      <Progress value={exp.progress} className="h-1.5" />
                    </div>

                    <div className="flex items-center justify-between mt-3 text-xs">
                      <span className="text-muted-foreground">Best Reward</span>
                      <span className="font-mono text-primary">{exp.bestReward.toFixed(3)}</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Experiment Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Reward Curve */}
          <Card className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg">{selectedExperiment.name}</CardTitle>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="icon" className="h-8 w-8">
                  <RotateCcw className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" className="h-8 w-8">
                  {selectedExperiment.status === "running" ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={rewardCurves[selectedExperiment.id]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 20%)" />
                    <XAxis 
                      dataKey="iteration" 
                      stroke="hsl(30, 10%, 60%)"
                      fontSize={12}
                      tickFormatter={(v) => `${v / 1000}k`}
                    />
                    <YAxis 
                      stroke="hsl(30, 10%, 60%)"
                      fontSize={12}
                      domain={[0, 1]}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "hsl(0, 0%, 10%)", 
                        border: "1px solid hsl(0, 0%, 20%)",
                        borderRadius: "8px"
                      }}
                      formatter={(value: number) => [value.toFixed(3), "Reward"]}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="reward" 
                      stroke="hsl(25, 95%, 53%)" 
                      strokeWidth={2}
                      dot={{ fill: "hsl(25, 95%, 53%)", strokeWidth: 0, r: 3 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Metrics & Hyperparameters */}
          <div className="grid grid-cols-2 gap-6">
            {/* Current Metrics */}
            <Card className="bg-card border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Current Metrics</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    <span className="text-xs text-muted-foreground">Current Reward</span>
                  </div>
                  <p className="text-xl font-bold font-mono">{selectedExperiment.currentReward.toFixed(3)}</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2 mb-1">
                    <Target className="h-4 w-4 text-green-400" />
                    <span className="text-xs text-muted-foreground">Best Reward</span>
                  </div>
                  <p className="text-xl font-bold font-mono">{selectedExperiment.bestReward.toFixed(3)}</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2 mb-1">
                    <Layers className="h-4 w-4 text-blue-400" />
                    <span className="text-xs text-muted-foreground">Iterations</span>
                  </div>
                  <p className="text-xl font-bold font-mono">
                    {(selectedExperiment.iterations / 1000).toFixed(1)}k
                    <span className="text-sm text-muted-foreground">/{selectedExperiment.maxIterations / 1000}k</span>
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="h-4 w-4 text-amber-400" />
                    <span className="text-xs text-muted-foreground">Duration</span>
                  </div>
                  <p className="text-xl font-bold">{selectedExperiment.duration}</p>
                </div>
              </CardContent>
            </Card>

            {/* Hyperparameters */}
            <Card className="bg-card border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Hyperparameters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-sm text-muted-foreground">Learning Rate</span>
                  <span className="font-mono text-sm">{selectedExperiment.hyperparameters.learningRate}</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-sm text-muted-foreground">Batch Size</span>
                  <span className="font-mono text-sm">{selectedExperiment.hyperparameters.batchSize}</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-sm text-muted-foreground">Gamma</span>
                  <span className="font-mono text-sm">{selectedExperiment.hyperparameters.gamma}</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-sm text-muted-foreground">Epsilon</span>
                  <span className="font-mono text-sm">{selectedExperiment.hyperparameters.epsilon}</span>
                </div>
                <Badge variant="outline" className="mt-2">
                  {selectedExperiment.policy} Algorithm
                </Badge>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Experiments;

import { motion, AnimatePresence } from "framer-motion";
import { 
  Search, 
  Activity, 
  RefreshCw, 
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Info
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useRealtimeAgentActivity, AgentActivity } from "@/hooks/useRealtimeData";
import { formatDistanceToNow } from "date-fns";

const statusConfig = {
  detected: { icon: Search, color: "text-amber-500", bg: "bg-amber-500/10" },
  analyzed: { icon: Activity, color: "text-blue-500", bg: "bg-blue-500/10" },
  patched: { icon: RefreshCw, color: "text-primary", bg: "bg-primary/10" },
  validated: { icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10" },
};

const severityConfig = {
  low: { icon: Info, color: "text-muted-foreground", label: "Low" },
  medium: { icon: AlertCircle, color: "text-amber-500", label: "Medium" },
  high: { icon: AlertTriangle, color: "text-orange-500", label: "High" },
  critical: { icon: AlertCircle, color: "text-red-500", label: "Critical" },
};

interface ActivityItemProps {
  activity: AgentActivity;
  index: number;
}

const ActivityItem = ({ activity, index }: ActivityItemProps) => {
  const config = statusConfig[activity.action];
  const Icon = config.icon;
  const severity = severityConfig[activity.severity];

  return (
    <motion.div
      initial={{ opacity: 0, x: -20, height: 0 }}
      animate={{ opacity: 1, x: 0, height: "auto" }}
      exit={{ opacity: 0, x: 20, height: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors border-b border-border/50 last:border-0"
    >
      <div className={`h-8 w-8 rounded-full ${config.bg} flex items-center justify-center flex-shrink-0`}>
        <Icon className={`h-4 w-4 ${config.color}`} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium truncate">{activity.title}</p>
          {activity.severity === "critical" || activity.severity === "high" ? (
            <Badge 
              variant="outline" 
              className={`text-xs ${severity.color} border-current`}
            >
              {severity.label}
            </Badge>
          ) : null}
        </div>
        <p className="text-xs text-muted-foreground">
          {activity.agentName} • {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
        </p>
      </div>
      <Badge variant="outline" className="capitalize text-xs flex-shrink-0">
        {activity.action}
      </Badge>
    </motion.div>
  );
};

interface LiveActivityFeedProps {
  maxItems?: number;
}

export const LiveActivityFeed = ({ maxItems = 8 }: LiveActivityFeedProps) => {
  const { activities, isConnected } = useRealtimeAgentActivity(maxItems);

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2 px-3 pb-2">
        <div className={`h-2 w-2 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-muted"}`} />
        <span className="text-xs text-muted-foreground">
          {isConnected ? "Live" : "Connecting..."}
        </span>
      </div>
      <div className="max-h-[400px] overflow-y-auto">
        <AnimatePresence mode="popLayout">
          {activities.map((activity, index) => (
            <ActivityItem 
              key={activity.id} 
              activity={activity} 
              index={index}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

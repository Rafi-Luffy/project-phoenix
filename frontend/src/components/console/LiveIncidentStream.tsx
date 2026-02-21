import { motion, AnimatePresence } from "framer-motion";
import { 
  AlertCircle,
  AlertTriangle,
  Info,
  CheckCircle2,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useRealtimeIncidents, IncidentStream } from "@/hooks/useRealtimeData";
import { formatDistanceToNow } from "date-fns";
import { toast } from "sonner";

const typeConfig: Record<string, { icon: React.ElementType; color: string; bg: string }> = {
  Critical: { icon: AlertCircle, color: "text-red-500", bg: "bg-red-500/10" },
  Error: { icon: AlertTriangle, color: "text-orange-500", bg: "bg-orange-500/10" },
  Warning: { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10" },
  Info: { icon: Info, color: "text-blue-500", bg: "bg-blue-500/10" },
};

const statusBadge: Record<string, { color: string; label: string }> = {
  open: { color: "bg-red-500/20 text-red-500 border-red-500/30", label: "Open" },
  investigating: { color: "bg-amber-500/20 text-amber-500 border-amber-500/30", label: "Investigating" },
  resolved: { color: "bg-green-500/20 text-green-500 border-green-500/30", label: "Resolved" },
};

interface IncidentItemProps {
  incident: IncidentStream;
  onResolve: (id: string) => void;
}

const IncidentItem = ({ incident, onResolve }: IncidentItemProps) => {
  const config = typeConfig[incident.type] || typeConfig.Info;
  const Icon = config.icon;
  const status = statusBadge[incident.status];

  const handleResolve = () => {
    onResolve(incident.id);
    toast.success("Incident marked as resolved");
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={`p-4 rounded-lg border transition-all ${
        incident.status === "resolved" 
          ? "bg-muted/30 border-border/50 opacity-60" 
          : "bg-card border-border"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`h-10 w-10 rounded-lg ${config.bg} flex items-center justify-center flex-shrink-0`}>
          {incident.status === "resolved" ? (
            <CheckCircle2 className="h-5 w-5 text-green-500" />
          ) : (
            <Icon className={`h-5 w-5 ${config.color}`} />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="font-medium text-sm">{incident.type}</span>
            <Badge variant="outline" className={`text-xs ${status.color}`}>
              {status.label}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">{incident.message}</p>
          <p className="text-xs text-muted-foreground mt-1">
            {formatDistanceToNow(incident.timestamp, { addSuffix: true })}
          </p>
        </div>
        {incident.status !== "resolved" && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 flex-shrink-0"
            onClick={handleResolve}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </motion.div>
  );
};

export const LiveIncidentStream = () => {
  const { incidents, resolveIncident } = useRealtimeIncidents();

  return (
    <div className="space-y-3">
      <AnimatePresence mode="popLayout">
        {incidents.map((incident) => (
          <IncidentItem 
            key={incident.id} 
            incident={incident} 
            onResolve={resolveIncident}
          />
        ))}
      </AnimatePresence>
      {incidents.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <CheckCircle2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No active incidents</p>
        </div>
      )}
    </div>
  );
};

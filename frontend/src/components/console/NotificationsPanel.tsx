import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bell, 
  X, 
  CheckCircle2, 
  AlertTriangle, 
  Info, 
  Zap,
  Activity,
  Clock
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface Notification {
  id: string;
  type: "success" | "warning" | "error" | "info";
  title: string;
  message: string;
  time: string;
  read: boolean;
  agent?: string;
}

const initialNotifications: Notification[] = [
  {
    id: "1",
    type: "success",
    title: "Self-Healing Complete",
    message: "API timeout in payment-service was automatically fixed",
    time: "2 min ago",
    read: false,
    agent: "Executor-01"
  },
  {
    id: "2",
    type: "warning",
    title: "High Memory Usage",
    message: "Agent Monitor-02 memory usage exceeded 80%",
    time: "5 min ago",
    read: false,
    agent: "Monitor-02"
  },
  {
    id: "3",
    type: "info",
    title: "New Agent Deployed",
    message: "Critic-03 has been deployed to production",
    time: "15 min ago",
    read: false
  },
  {
    id: "4",
    type: "success",
    title: "Correction Validated",
    message: "Database connection pool fix passed all tests",
    time: "22 min ago",
    read: true,
    agent: "Executor-03"
  },
  {
    id: "5",
    type: "error",
    title: "Agent Error",
    message: "Executor-02 encountered a configuration mismatch",
    time: "45 min ago",
    read: true,
    agent: "Executor-02"
  },
  {
    id: "6",
    type: "info",
    title: "Daily Report Ready",
    message: "Your daily performance report is now available",
    time: "1 hour ago",
    read: true
  }
];

export const NotificationsPanel = () => {
  const [notifications, setNotifications] = useState<Notification[]>(initialNotifications);
  const [isOpen, setIsOpen] = useState(false);

  const unreadCount = notifications.filter(n => !n.read).length;

  // Simulate real-time notifications
  useEffect(() => {
    const interval = setInterval(() => {
      const newNotification: Notification = {
        id: Date.now().toString(),
        type: Math.random() > 0.5 ? "success" : "info",
        title: Math.random() > 0.5 ? "Self-Healing Complete" : "Agent Status Update",
        message: Math.random() > 0.5 
          ? "Memory leak in cache-service was automatically patched"
          : "All agents operating within normal parameters",
        time: "Just now",
        read: false,
        agent: `Agent-${Math.floor(Math.random() * 10)}`
      };
      
      setNotifications(prev => [newNotification, ...prev.slice(0, 19)]);
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => 
      n.id === id ? { ...n, read: true } : n
    ));
  };

  const clearNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const getIcon = (type: Notification["type"]) => {
    switch (type) {
      case "success":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-amber-500" />;
      case "error":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case "info":
        return <Info className="h-4 w-4 text-blue-500" />;
    }
  };

  const getBgColor = (type: Notification["type"]) => {
    switch (type) {
      case "success":
        return "bg-green-500/10";
      case "warning":
        return "bg-amber-500/10";
      case "error":
        return "bg-red-500/10";
      case "info":
        return "bg-blue-500/10";
    }
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative h-9 w-9">
          <Bell className="h-5 w-5" />
          <AnimatePresence>
            {unreadCount > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0 }}
                className="absolute -top-0.5 -right-0.5 h-4 w-4 bg-primary rounded-full flex items-center justify-center text-[10px] font-bold text-primary-foreground"
              >
                {unreadCount > 9 ? "9+" : unreadCount}
              </motion.span>
            )}
          </AnimatePresence>
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        align="end" 
        className="w-[380px] p-0 bg-card border-border"
        sideOffset={8}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold">Notifications</h3>
            {unreadCount > 0 && (
              <Badge variant="secondary" className="bg-primary/10 text-primary">
                {unreadCount} new
              </Badge>
            )}
          </div>
          {unreadCount > 0 && (
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-xs text-muted-foreground hover:text-foreground"
              onClick={markAllRead}
            >
              Mark all read
            </Button>
          )}
        </div>

        {/* Notifications List */}
        <ScrollArea className="h-[400px]">
          <div className="p-2 space-y-1">
            <AnimatePresence initial={false}>
              {notifications.map((notification) => (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  layout
                  className={cn(
                    "p-3 rounded-lg cursor-pointer transition-colors group",
                    notification.read 
                      ? "hover:bg-muted/50" 
                      : "bg-muted/30 hover:bg-muted/50"
                  )}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex gap-3">
                    <div className={cn(
                      "h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0",
                      getBgColor(notification.type)
                    )}>
                      {getIcon(notification.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <p className={cn(
                            "text-sm font-medium truncate",
                            !notification.read && "text-foreground"
                          )}>
                            {notification.title}
                          </p>
                          {!notification.read && (
                            <span className="h-1.5 w-1.5 bg-primary rounded-full flex-shrink-0" />
                          )}
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            clearNotification(notification.id);
                          }}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-muted rounded"
                        >
                          <X className="h-3 w-3 text-muted-foreground" />
                        </button>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                        {notification.message}
                      </p>
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {notification.time}
                        </span>
                        {notification.agent && (
                          <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                            <Activity className="h-3 w-3" />
                            {notification.agent}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </ScrollArea>

        {/* Footer */}
        <div className="p-3 border-t border-border">
          <Button variant="ghost" className="w-full text-sm text-muted-foreground hover:text-foreground">
            View all notifications
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
};

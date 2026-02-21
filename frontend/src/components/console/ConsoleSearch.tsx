import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Search, 
  Bot, 
  GitBranch, 
  AlertTriangle, 
  Settings, 
  FileText,
  BarChart3,
  Network,
  FlaskConical,
  ArrowRight,
  Clock
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";

interface SearchResult {
  id: string;
  type: "agent" | "pipeline" | "incident" | "setting" | "page";
  title: string;
  description: string;
  href: string;
  icon: React.ElementType;
  iconColor: string;
}

const allResults: SearchResult[] = [
  // Agents
  { id: "a1", type: "agent", title: "Monitor-01", description: "Active • 234 corrections", href: "/console/agents", icon: Bot, iconColor: "text-green-500" },
  { id: "a2", type: "agent", title: "Monitor-02", description: "Active • 189 corrections", href: "/console/agents", icon: Bot, iconColor: "text-green-500" },
  { id: "a3", type: "agent", title: "Executor-01", description: "Active • 312 corrections", href: "/console/agents", icon: Bot, iconColor: "text-primary" },
  { id: "a4", type: "agent", title: "Executor-02", description: "Error • Config mismatch", href: "/console/agents", icon: Bot, iconColor: "text-red-500" },
  { id: "a5", type: "agent", title: "Critic-01", description: "Idle • 156 corrections", href: "/console/agents", icon: Bot, iconColor: "text-amber-500" },
  { id: "a6", type: "agent", title: "Planner-01", description: "Active • 445 corrections", href: "/console/agents", icon: Bot, iconColor: "text-blue-500" },
  // Pipelines
  { id: "p1", type: "pipeline", title: "API Error Handler", description: "Running • 98.5% success", href: "/console/pipelines", icon: GitBranch, iconColor: "text-primary" },
  { id: "p2", type: "pipeline", title: "Memory Leak Detector", description: "Running • 96.2% success", href: "/console/pipelines", icon: GitBranch, iconColor: "text-primary" },
  { id: "p3", type: "pipeline", title: "Rate Limit Manager", description: "Paused", href: "/console/pipelines", icon: GitBranch, iconColor: "text-amber-500" },
  // Incidents
  { id: "i1", type: "incident", title: "API timeout in payment-service", description: "Resolved • 2m ago", href: "/console", icon: AlertTriangle, iconColor: "text-green-500" },
  { id: "i2", type: "incident", title: "Memory leak in cache-service", description: "Detected • 12m ago", href: "/console", icon: AlertTriangle, iconColor: "text-amber-500" },
  { id: "i3", type: "incident", title: "Rate limit exceeded", description: "Analyzing • 8m ago", href: "/console", icon: AlertTriangle, iconColor: "text-blue-500" },
  // Pages
  { id: "pg1", type: "page", title: "Dashboard", description: "View KPIs and metrics", href: "/console", icon: BarChart3, iconColor: "text-muted-foreground" },
  { id: "pg2", type: "page", title: "Agents", description: "Manage runtime agents", href: "/console/agents", icon: Bot, iconColor: "text-muted-foreground" },
  { id: "pg3", type: "page", title: "Pipelines", description: "View and manage pipelines", href: "/console/pipelines", icon: GitBranch, iconColor: "text-muted-foreground" },
  { id: "pg4", type: "page", title: "Memory Graph", description: "Explore agent memory", href: "/console/memory", icon: Network, iconColor: "text-muted-foreground" },
  { id: "pg5", type: "page", title: "Experiments", description: "A/B tests and experiments", href: "/console/experiments", icon: FlaskConical, iconColor: "text-muted-foreground" },
  { id: "pg6", type: "page", title: "Metrics", description: "Performance analytics", href: "/console/metrics", icon: BarChart3, iconColor: "text-muted-foreground" },
  { id: "pg7", type: "page", title: "Settings", description: "Account and preferences", href: "/console/settings", icon: Settings, iconColor: "text-muted-foreground" },
  { id: "pg8", type: "page", title: "Profile", description: "Your profile settings", href: "/console/profile", icon: Settings, iconColor: "text-muted-foreground" },
  // Settings
  { id: "s1", type: "setting", title: "API Keys", description: "Manage API access tokens", href: "/console/settings", icon: Settings, iconColor: "text-muted-foreground" },
  { id: "s2", type: "setting", title: "Notifications", description: "Email and push preferences", href: "/console/settings", icon: Settings, iconColor: "text-muted-foreground" },
  { id: "s3", type: "setting", title: "Webhooks", description: "Configure webhook endpoints", href: "/console/settings", icon: Settings, iconColor: "text-muted-foreground" },
];

const recentSearches = ["Monitor-01", "API timeout", "payment-service"];

export const ConsoleSearch = () => {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (query.trim()) {
      const filtered = allResults.filter(
        item =>
          item.title.toLowerCase().includes(query.toLowerCase()) ||
          item.description.toLowerCase().includes(query.toLowerCase())
      );
      setResults(filtered.slice(0, 8));
      setSelectedIndex(0);
    } else {
      setResults([]);
    }
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === "Enter" && results[selectedIndex]) {
      navigate(results[selectedIndex].href);
      setQuery("");
      setIsFocused(false);
      inputRef.current?.blur();
    } else if (e.key === "Escape") {
      setIsFocused(false);
      inputRef.current?.blur();
    }
  };

  const handleResultClick = (result: SearchResult) => {
    navigate(result.href);
    setQuery("");
    setIsFocused(false);
  };

  const showDropdown = isFocused && (query.trim() || recentSearches.length > 0);

  return (
    <div className="relative w-80">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        ref={inputRef}
        placeholder="Search agents, incidents..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setTimeout(() => setIsFocused(false), 200)}
        onKeyDown={handleKeyDown}
        className="pl-10 bg-background border-border focus:border-primary"
      />
      <kbd className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
        <span className="text-xs">⌘</span>K
      </kbd>

      <AnimatePresence>
        {showDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-xl shadow-lg overflow-hidden z-50"
          >
            {results.length > 0 ? (
              <div className="py-2">
                <div className="px-3 py-1.5 text-xs text-muted-foreground font-medium">
                  Results
                </div>
                {results.map((result, index) => (
                  <button
                    key={result.id}
                    onClick={() => handleResultClick(result)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 transition-colors text-left",
                      index === selectedIndex ? "bg-muted" : "hover:bg-muted/50"
                    )}
                  >
                    <div className={cn(
                      "h-8 w-8 rounded-lg bg-muted flex items-center justify-center",
                      index === selectedIndex && "bg-primary/10"
                    )}>
                      <result.icon className={cn("h-4 w-4", result.iconColor)} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{result.title}</p>
                      <p className="text-xs text-muted-foreground truncate">{result.description}</p>
                    </div>
                    {index === selectedIndex && (
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    )}
                  </button>
                ))}
              </div>
            ) : query.trim() ? (
              <div className="py-8 text-center text-muted-foreground">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No results found for "{query}"</p>
              </div>
            ) : (
              <div className="py-2">
                <div className="px-3 py-1.5 text-xs text-muted-foreground font-medium flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Recent searches
                </div>
                {recentSearches.map((search) => (
                  <button
                    key={search}
                    onClick={() => setQuery(search)}
                    className="w-full flex items-center gap-3 px-3 py-2 hover:bg-muted/50 transition-colors text-left"
                  >
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">{search}</span>
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import {
  LayoutDashboard,
  Bot,
  Network,
  FlaskConical,
  Settings,
  GitBranch,
  BarChart3,
  User,
  Hammer,
  LogOut,
  Search,
  Plus,
  Play,
  Pause,
  RefreshCw,
  FileText,
  HelpCircle,
  Keyboard,
  Moon,
  Sun,
} from "lucide-react";
import { toast } from "sonner";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CommandPalette = ({ open, onOpenChange }: CommandPaletteProps) => {
  const navigate = useNavigate();
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const root = document.documentElement;
    setTheme(root.classList.contains("light") ? "light" : "dark");
  }, [open]);

  const runCommand = useCallback((command: () => void) => {
    onOpenChange(false);
    command();
  }, [onOpenChange]);

  const handleLogout = () => {
    localStorage.removeItem("phoenix_auth");
    toast.success("Logged out successfully");
    navigate("/");
  };

  const toggleTheme = () => {
    const root = document.documentElement;
    if (root.classList.contains("light")) {
      root.classList.remove("light");
      setTheme("dark");
      toast.success("Switched to dark mode");
    } else {
      root.classList.add("light");
      setTheme("light");
      toast.success("Switched to light mode");
    }
  };

  const navigationItems = [
    { label: "Dashboard", icon: LayoutDashboard, href: "/console", shortcut: "⌘1" },
    { label: "Agents", icon: Bot, href: "/console/agents", shortcut: "⌘2" },
    { label: "Agent Builder", icon: Hammer, href: "/console/builder", shortcut: "⌘3" },
    { label: "Pipelines", icon: GitBranch, href: "/console/pipelines", shortcut: "⌘4" },
    { label: "Memory Graph", icon: Network, href: "/console/memory", shortcut: "⌘5" },
    { label: "Experiments", icon: FlaskConical, href: "/console/experiments", shortcut: "⌘6" },
    { label: "Metrics", icon: BarChart3, href: "/console/metrics", shortcut: "⌘7" },
    { label: "Settings", icon: Settings, href: "/console/settings", shortcut: "⌘," },
    { label: "Profile", icon: User, href: "/console/profile" },
  ];

  const actionItems = [
    { 
      label: "Create New Agent", 
      icon: Plus, 
      action: () => {
        navigate("/console/builder");
        toast.success("Opening Agent Builder...");
      },
      shortcut: "⌘N"
    },
    { 
      label: "Start All Agents", 
      icon: Play, 
      action: () => toast.success("Starting all agents..."),
    },
    { 
      label: "Pause All Agents", 
      icon: Pause, 
      action: () => toast.success("Pausing all agents..."),
    },
    { 
      label: "Refresh Dashboard", 
      icon: RefreshCw, 
      action: () => {
        window.location.reload();
      },
      shortcut: "⌘R"
    },
    { 
      label: "Toggle Theme", 
      icon: theme === "dark" ? Sun : Moon, 
      action: toggleTheme,
      shortcut: "⌘T"
    },
  ];

  const helpItems = [
    { 
      label: "Documentation", 
      icon: FileText, 
      action: () => window.open("/docs", "_blank"),
      shortcut: "⌘D"
    },
    { 
      label: "Keyboard Shortcuts", 
      icon: Keyboard, 
      action: () => toast.info("Cmd+K: Command Palette\nCmd+1-7: Navigate\nCmd+N: New Agent\nCmd+,: Settings"),
    },
    { 
      label: "Contact Support", 
      icon: HelpCircle, 
      action: () => window.open("/docs/support", "_blank"),
    },
  ];

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        
        <CommandGroup heading="Navigation">
          {navigationItems.map((item) => (
            <CommandItem
              key={item.href}
              onSelect={() => runCommand(() => navigate(item.href))}
              className="cursor-pointer"
            >
              <item.icon className="mr-2 h-4 w-4" />
              <span>{item.label}</span>
              {item.shortcut && <CommandShortcut>{item.shortcut}</CommandShortcut>}
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Actions">
          {actionItems.map((item) => (
            <CommandItem
              key={item.label}
              onSelect={() => runCommand(item.action)}
              className="cursor-pointer"
            >
              <item.icon className="mr-2 h-4 w-4" />
              <span>{item.label}</span>
              {item.shortcut && <CommandShortcut>{item.shortcut}</CommandShortcut>}
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Help">
          {helpItems.map((item) => (
            <CommandItem
              key={item.label}
              onSelect={() => runCommand(item.action)}
              className="cursor-pointer"
            >
              <item.icon className="mr-2 h-4 w-4" />
              <span>{item.label}</span>
              {item.shortcut && <CommandShortcut>{item.shortcut}</CommandShortcut>}
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Account">
          <CommandItem
            onSelect={() => runCommand(handleLogout)}
            className="cursor-pointer text-red-500"
          >
            <LogOut className="mr-2 h-4 w-4" />
            <span>Log out</span>
            <CommandShortcut>⌘Q</CommandShortcut>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
};

// Hook for keyboard shortcuts
export const useKeyboardShortcuts = (onOpenCommandPalette: () => void) => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Command/Ctrl + K for command palette
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        onOpenCommandPalette();
      }

      // Navigation shortcuts with Command/Ctrl + number
      if (e.metaKey || e.ctrlKey) {
        switch (e.key) {
          case "1":
            e.preventDefault();
            navigate("/console");
            break;
          case "2":
            e.preventDefault();
            navigate("/console/agents");
            break;
          case "3":
            e.preventDefault();
            navigate("/console/builder");
            break;
          case "4":
            e.preventDefault();
            navigate("/console/pipelines");
            break;
          case "5":
            e.preventDefault();
            navigate("/console/memory");
            break;
          case "6":
            e.preventDefault();
            navigate("/console/experiments");
            break;
          case "7":
            e.preventDefault();
            navigate("/console/metrics");
            break;
          case ",":
            e.preventDefault();
            navigate("/console/settings");
            break;
          case "n":
            e.preventDefault();
            navigate("/console/builder");
            toast.success("Opening Agent Builder...");
            break;
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [navigate, onOpenCommandPalette]);
};

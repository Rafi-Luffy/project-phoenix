import { useState, useEffect } from "react";
import { Link, useLocation, Outlet, useNavigate } from "react-router-dom";
import { useUser, useClerk, UserButton } from "@clerk/clerk-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, 
  Bot, 
  Network, 
  FlaskConical, 
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  GitBranch,
  BarChart3,
  Hammer,
  Command,
} from "lucide-react";
import { PhoenixLogo } from "@/components/landing/PhoenixLogo";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./ThemeToggle";
import { NotificationsPanel } from "./NotificationsPanel";
import { ConsoleSearch } from "./ConsoleSearch";
import { CommandPalette, useKeyboardShortcuts } from "./CommandPalette";
import { OnboardingWizard } from "./OnboardingWizard";

const navItems = [
  { label: "Dashboard",     href: "/console",             icon: LayoutDashboard },
  { label: "Agents",        href: "/console/agents",       icon: Bot },
  { label: "Agent Builder", href: "/console/builder",      icon: Hammer },
  { label: "Pipelines",     href: "/console/pipelines",    icon: GitBranch },
  { label: "Memory Graph",  href: "/console/memory",       icon: Network },
  { label: "Experiments",   href: "/console/experiments",  icon: FlaskConical },
  { label: "Metrics",       href: "/console/metrics",      icon: BarChart3 },
  { label: "Settings",      href: "/console/settings",     icon: Settings },
];

export const ConsoleLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [environment, setEnvironment] = useState<"dev" | "prod">("dev");
  const [commandOpen, setCommandOpen] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useUser();
  const { signOut } = useClerk();

  // Initialize keyboard shortcuts
  useKeyboardShortcuts(() => setCommandOpen(true));

  // Show onboarding for first-time users
  useEffect(() => {
    const onboardingComplete = localStorage.getItem("phoenix_onboarding_complete");
    if (!onboardingComplete) {
      const timer = setTimeout(() => setShowOnboarding(true), 500);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleLogout = () => {
    signOut(() => navigate("/"));
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Command Palette */}
      <CommandPalette open={commandOpen} onOpenChange={setCommandOpen} />

      {/* Onboarding Wizard */}
      <OnboardingWizard 
        open={showOnboarding} 
        onClose={() => setShowOnboarding(false)} 
      />

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 72 : 260 }}
        className="fixed left-0 top-0 h-screen border-r border-border bg-card z-50 flex flex-col"
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          <Link to="/console" className="flex items-center gap-2">
            <PhoenixLogo size="sm" />
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  className="font-bold text-lg overflow-hidden whitespace-nowrap"
                >
                  Phoenix
                </motion.span>
              )}
            </AnimatePresence>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="h-8 w-8"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {/* Environment Selector */}
        {!collapsed && (
          <div className="px-4 py-3 border-b border-border">
            <div className="flex gap-1 p-1 bg-muted rounded-lg">
              <button
                onClick={() => setEnvironment("dev")}
                className={cn(
                  "flex-1 py-1.5 px-3 rounded-md text-xs font-medium transition-colors",
                  environment === "dev" 
                    ? "bg-amber-500/20 text-amber-500" 
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                Development
              </button>
              <button
                onClick={() => setEnvironment("prod")}
                className={cn(
                  "flex-1 py-1.5 px-3 rounded-md text-xs font-medium transition-colors",
                  environment === "prod" 
                    ? "bg-green-500/20 text-green-500" 
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                Production
              </button>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 overflow-y-auto">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.href || 
                (item.href !== "/console" && location.pathname.startsWith(item.href));
              
              return (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
                      isActive 
                        ? "bg-primary/10 text-primary border border-primary/20" 
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    )}
                  >
                    <item.icon className={cn("h-5 w-5 flex-shrink-0", isActive && "text-primary")} />
                    <AnimatePresence>
                      {!collapsed && (
                        <motion.span
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: "auto" }}
                          exit={{ opacity: 0, width: 0 }}
                          className="font-medium overflow-hidden whitespace-nowrap"
                        >
                          {item.label}
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Bottom */}
        <div className="p-4 border-t border-border">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors w-full"
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  className="font-medium overflow-hidden whitespace-nowrap"
                >
                  Logout
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <div className={cn("flex-1 transition-all duration-300", collapsed ? "ml-[72px]" : "ml-[260px]")}>
        {/* Top Bar */}
        <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <ConsoleSearch />
            {/* Command Palette Hint */}
            <button
              onClick={() => setCommandOpen(true)}
              className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/50 hover:bg-muted transition-colors text-sm text-muted-foreground"
            >
              <Command className="h-3 w-3" />
              <span>K</span>
            </button>
          </div>
          <div className="flex items-center gap-3">
            {/* Environment Badge */}
            <div className={cn(
              "px-3 py-1 rounded-full text-xs font-medium",
              environment === "dev" 
                ? "bg-amber-500/20 text-amber-500" 
                : "bg-green-500/20 text-green-500"
            )}>
              {environment === "dev" ? "Dev" : "Prod"}
            </div>

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Notifications */}
            <NotificationsPanel />

            {/* Clerk UserButton — manages profile, sign out automatically */}
            <UserButton
              afterSignOutUrl="/"
              appearance={{
                elements: {
                  avatarBox: "h-8 w-8",
                },
              }}
            />
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

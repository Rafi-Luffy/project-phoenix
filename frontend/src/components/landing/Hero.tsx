import { motion } from "framer-motion";
import { ArrowRight, Sparkles, GitBranch, Network, Activity, Command } from "lucide-react";
import { Button } from "@/components/ui/button";
import { NetworkGraph } from "./NetworkGraph";
import { FloatingOrbs } from "./FloatingOrbs";

const featurePills = [
  { icon: Sparkles, label: "Self-Refine Loops" },
  { icon: GitBranch, label: "Tree-of-Thoughts" },
  { icon: Network, label: "Multi-Agent" },
  { icon: Activity, label: "Production-Grade" },
];

export function Hero() {
  return (
    <section className="relative min-h-screen pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden flex items-center">
      {/* Background */}
      <div className="absolute inset-0 -z-10 bg-background">
        <FloatingOrbs />
      </div>

      <div className="container mx-auto px-4 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="space-y-8"
          >
            {/* Eyebrow badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-primary/10 text-primary border border-primary/20 backdrop-blur-sm">
                <motion.span 
                  className="w-2 h-2 rounded-full bg-primary"
                  animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                Open beta · Autonomous self-healing agents
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold leading-[1.1] tracking-tight"
            >
              <span className="text-foreground">The most </span>
              <span className="relative inline-block">
                <span className="gradient-text">intelligent</span>
                <motion.span
                  className="absolute -inset-1 bg-primary/20 blur-2xl rounded-full -z-10"
                  animate={{ opacity: [0.5, 0.8, 0.5] }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
              </span>
              <br />
              <span className="text-foreground">runtime for AI agents.</span>
            </motion.h1>

            {/* Subheading */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="text-lg lg:text-xl text-muted-foreground max-w-xl leading-relaxed"
            >
              Phoenix autonomously detects, repairs, and learns from failures using 
              meta-learning and multi-agent orchestration with zero human intervention.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="flex flex-col sm:flex-row gap-4"
            >
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button className="btn-primary text-base px-8 py-4 h-auto group">
                  <span>Start Building</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button variant="outline" className="btn-ghost text-base px-8 py-4 h-auto group">
                  <span>Book Onboarding</span>
                  <span className="flex items-center gap-0.5 px-2 py-1 rounded bg-muted text-xs font-mono text-muted-foreground group-hover:text-primary transition-colors">
                    <Command className="w-3 h-3" />K
                  </span>
                </Button>
              </motion.div>
            </motion.div>

            {/* Feature pills */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.6 }}
              className="flex flex-wrap gap-2 pt-4"
            >
              {featurePills.map((pill, index) => (
                <motion.span
                  key={pill.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.9 + index * 0.1, duration: 0.4 }}
                  whileHover={{ scale: 1.05, y: -2 }}
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium bg-muted/50 text-muted-foreground border border-border/50 cursor-default hover:border-primary/30 hover:text-foreground transition-all duration-200"
                >
                  <pill.icon className="w-3.5 h-3.5" />
                  {pill.label}
                </motion.span>
              ))}
            </motion.div>
          </motion.div>

          {/* Right visual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, x: 50 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
            className="relative"
          >
            <NetworkGraph />
          </motion.div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent pointer-events-none" />
    </section>
  );
}

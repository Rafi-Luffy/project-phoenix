import { motion } from "framer-motion";
import { Check, AlertTriangle, RefreshCw, Database, Zap, Terminal } from "lucide-react";

const features = [
  "Self-Refine feedback loops for autonomous error correction",
  "Tree-of-Thoughts planning for complex multi-step reasoning",
  "Reinforcement learning adapts policies from experience",
  "Meta-learning enables rapid generalization",
  "Multi-agent coordination for distributed workloads",
];

const logSteps = [
  { time: "12:45:03", type: "error", message: "API timeout detected in /process endpoint" },
  { time: "12:45:04", type: "reflect", message: "Critic analyzing: retry strategy ineffective" },
  { time: "12:45:05", type: "correct", message: "Applying adaptive backoff policy v2.3" },
  { time: "12:45:06", type: "store", message: "Experience stored → memory.long_term.api_errors" },
  { time: "12:45:07", type: "success", message: "Endpoint recovered, 0ms additional downtime" },
];

const getStepStyle = (type: string) => {
  switch (type) {
    case "error":
      return { icon: AlertTriangle, color: "text-red-400", bg: "bg-red-500/20", border: "border-red-500/30" };
    case "reflect":
      return { icon: RefreshCw, color: "text-accent", bg: "bg-accent/20", border: "border-accent/30" };
    case "correct":
      return { icon: Zap, color: "text-primary", bg: "bg-primary/20", border: "border-primary/30" };
    case "store":
      return { icon: Database, color: "text-amber-400", bg: "bg-amber-500/20", border: "border-amber-500/30" };
    case "success":
      return { icon: Check, color: "text-emerald-400", bg: "bg-emerald-500/20", border: "border-emerald-500/30" };
    default:
      return { icon: Check, color: "text-muted-foreground", bg: "bg-muted", border: "border-border" };
  }
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

export function WhySection() {
  return (
    <section className="py-24 lg:py-36 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/30 to-background" />
      
      <div className="container mx-auto px-4 lg:px-8 relative">
        {/* Headline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7 }}
          className="text-center mb-20"
        >
          <motion.span 
            className="inline-block pill-accent mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            Why Phoenix?
          </motion.span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-extrabold mb-6 tracking-tight">
            Stop <span className="gradient-text">Babysitting</span> Your Agents
          </h2>
          <p className="text-lg lg:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Phoenix implements Self-Refine, Tree of Thoughts, and reinforcement learning 
            to autonomously detect, critique, and fix its own mistakes at runtime.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-start">
          {/* Left: Feature list */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            className="space-y-4"
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature}
                variants={itemVariants}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ x: 8, transition: { duration: 0.2 } }}
                className="group"
              >
                <div className="flex items-start gap-4 p-5 rounded-2xl bg-card/50 border border-border/50 hover:border-primary/40 hover:bg-card transition-all duration-300">
                  <motion.div 
                    className="flex-shrink-0 w-8 h-8 rounded-xl bg-primary/20 flex items-center justify-center mt-0.5"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                  >
                    <Check className="w-4 h-4 text-primary" />
                  </motion.div>
                  <span className="text-foreground font-medium leading-relaxed group-hover:text-primary transition-colors">
                    {feature}
                  </span>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Right: Terminal mockup */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            <div className="rounded-2xl bg-black/80 border border-border/50 overflow-hidden shadow-2xl shadow-black/40">
              {/* Terminal header */}
              <div className="flex items-center gap-3 px-5 py-4 border-b border-border/30 bg-black/50">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <Terminal className="w-4 h-4 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground font-mono">
                    phoenix-runtime.log
                  </span>
                </div>
              </div>

              {/* Log entries */}
              <div className="p-5 space-y-3 font-mono text-sm">
                {logSteps.map((step, index) => {
                  const { icon: Icon, color, bg, border } = getStepStyle(step.type);
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.5 + index * 0.15, duration: 0.4 }}
                      className={`flex items-start gap-3 p-3 rounded-lg ${bg} border ${border}`}
                    >
                      <span className="text-muted-foreground text-xs flex-shrink-0 mt-0.5 font-mono">
                        {step.time}
                      </span>
                      <div className="flex-shrink-0">
                        <Icon className={`w-4 h-4 ${color}`} />
                      </div>
                      <span className="text-muted-foreground text-xs leading-relaxed flex-1">
                        {step.message}
                      </span>
                    </motion.div>
                  );
                })}
                
                {/* Blinking cursor */}
                <motion.div
                  className="flex items-center gap-2 pl-3"
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  <span className="text-primary text-xs">▌</span>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

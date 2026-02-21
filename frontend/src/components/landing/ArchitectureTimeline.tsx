import { motion } from "framer-motion";
// Phoenix Runtime - Architecture Timeline
import { 
  Blocks, 
  Bot, 
  Brain, 
  RefreshCw, 
  GraduationCap, 
  Network, 
  LineChart 
} from "lucide-react";

const modules = [
  {
    number: 1,
    title: "Core Architecture",
    icon: Blocks,
    summary: "Foundation layer with robust infrastructure",
    points: [
      "Project structure & DB schema",
      "API gateway & routing",
      "Authentication & authorization",
      "Centralized logging",
      "Configuration management",
    ],
  },
  {
    number: 2,
    title: "Agent Framework",
    icon: Bot,
    summary: "Flexible agent abstractions for any task",
    points: [
      "Abstract agent base class",
      "Message passing protocols",
      "State management",
      "Event bus architecture",
      "Lifecycle hooks",
    ],
  },
  {
    number: 3,
    title: "Memory System",
    icon: Brain,
    summary: "Unified memory for context and learning",
    points: [
      "Short-term working memory",
      "Long-term experience storage",
      "Vector store abstraction",
      "Context window optimization",
      "Semantic retrieval",
    ],
  },
  {
    number: 4,
    title: "Self-Correction Engine",
    icon: RefreshCw,
    summary: "Autonomous error detection and repair",
    points: [
      "Error & anomaly detection",
      "Confidence scoring",
      "Feedback loop orchestration",
      "Rule-based corrections",
      "ML-based & hybrid strategies",
    ],
  },
  {
    number: 5,
    title: "Learning & Adaptation",
    icon: GraduationCap,
    summary: "Continuous improvement through experience",
    points: [
      "Meta-learning algorithms",
      "Few-shot & transfer learning",
      "RL policy optimization",
      "Reward shaping & bandits",
      "Optional human feedback hooks",
    ],
  },
  {
    number: 6,
    title: "Multi-Agent Coordination",
    icon: Network,
    summary: "Orchestration for distributed workloads",
    points: [
      "Communication protocols",
      "Consensus mechanisms",
      "Workflow orchestration",
      "Load balancing",
      "Fault tolerance",
    ],
  },
  {
    number: 7,
    title: "Evaluation & Production",
    icon: LineChart,
    summary: "Enterprise-grade observability and deployment",
    points: [
      "Performance metrics & A/B testing",
      "Long-term stability monitoring",
      "Blue-green deployments",
      "Rollback automation",
      "SLA enforcement",
    ],
  },
];

export function ArchitectureTimeline() {
  return (
    <section id="architecture" className="py-20 lg:py-32">
      <div className="container mx-auto px-4 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="pill-accent mb-4 inline-block">
            Implementation Roadmap
          </span>
          <h2 className="section-heading mb-4">
            End-to-End <span className="gradient-text">Architecture</span>
          </h2>
          <p className="section-subheading mx-auto">
            Seven carefully designed modules that work together to create 
            a truly autonomous, self-healing agent runtime.
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="relative">
          {/* Connection line (desktop) */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-primary/20 via-accent/40 to-primary/20 -translate-y-1/2" />

          {/* Modules grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-6 lg:gap-4">
            {modules.map((module, index) => (
              <motion.div
                key={module.number}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                className="relative group"
              >
                {/* Card */}
                <div className="card-glass p-5 h-full flex flex-col group-hover:border-accent/40 transition-all duration-300">
                  {/* Module number badge */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center shadow-glow">
                      <module.icon className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <span className="text-xs font-bold text-accent">
                      Module {module.number}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className="font-bold text-lg mb-2 leading-tight">
                    {module.title}
                  </h3>

                  {/* Summary */}
                  <p className="text-sm text-muted-foreground mb-4">
                    {module.summary}
                  </p>

                  {/* Points */}
                  <ul className="space-y-2 mt-auto">
                    {module.points.map((point, i) => (
                      <li key={i} className="text-xs text-muted-foreground flex items-start gap-2">
                        <span className="w-1 h-1 rounded-full bg-accent mt-1.5 flex-shrink-0" />
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

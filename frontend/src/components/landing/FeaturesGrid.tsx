import { motion } from "framer-motion";
import { 
  RefreshCw, 
  GraduationCap, 
  Database, 
  Network, 
  BarChart3, 
  Cloud, 
  Puzzle, 
  Shield 
} from "lucide-react";

const features = [
  {
    icon: RefreshCw,
    title: "Autonomous Self-Correction",
    description: "Error detection, anomaly scoring, confidence thresholds, and automatic rollback.",
  },
  {
    icon: GraduationCap,
    title: "Meta-Learning & RL",
    description: "Few-shot adapters, policy optimization, and experience replay for continuous improvement.",
  },
  {
    icon: Database,
    title: "Unified Memory Layer",
    description: "Vector + graph memory for short-term context and long-term knowledge retrieval.",
  },
  {
    icon: Network,
    title: "Multi-Agent Orchestration",
    description: "Task graphs, dependency management, consensus protocols, and conflict resolution.",
  },
  {
    icon: BarChart3,
    title: "Evaluation & A/B Benchmarks",
    description: "Performance metrics, statistical tests, and automated benchmarking suite.",
  },
  {
    icon: Cloud,
    title: "Production-grade DevOps",
    description: "Docker, Kubernetes, autoscaling, observability, and SLA enforcement.",
  },
  {
    icon: Puzzle,
    title: "Research-ready Extensions",
    description: "Pluggable Self-Refine, Tree-of-Thoughts, Reflexion, CRITIC, and Self-Debug modules.",
  },
  {
    icon: Shield,
    title: "Secure Runtime",
    description: "AuthN/AuthZ, audit logs, isolated environments, and compliance-ready infrastructure.",
  },
];

export function FeaturesGrid() {
  return (
    <section id="agents" className="py-20 lg:py-32 bg-muted/30">
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
            Capabilities
          </span>
          <h2 className="section-heading mb-4">
            Everything You Need for{" "}
            <span className="gradient-text">Autonomous Agents</span>
          </h2>
          <p className="section-subheading mx-auto">
            A complete framework with production-ready components for 
            building, running, and self-healing intelligent systems.
          </p>
        </motion.div>

        {/* Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.5 }}
              className="group"
            >
              <div className="card-glass p-6 h-full group-hover:border-accent/40 transition-all duration-300">
                {/* Icon */}
                <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-4 group-hover:shadow-glow transition-shadow duration-300">
                  <feature.icon className="w-6 h-6 text-primary-foreground" />
                </div>

                {/* Title */}
                <h3 className="font-bold text-lg mb-2">{feature.title}</h3>

                {/* Description */}
                <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

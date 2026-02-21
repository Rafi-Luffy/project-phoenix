import { motion } from "framer-motion";
import { Eye, MessageSquare, Wrench, TrendingUp } from "lucide-react";

const steps = [
  {
    number: "01",
    title: "Observe",
    icon: Eye,
    description: "Agents run in production, streaming telemetry, traces, and errors in real-time.",
    artifacts: ["Logs", "Traces", "Error events", "Metrics"],
  },
  {
    number: "02",
    title: "Reflect",
    icon: MessageSquare,
    description: "Critic and meta-controller analyze behavior using Self-Refine and ToT branching.",
    artifacts: ["Analysis reports", "ToT branches", "Confidence scores"],
  },
  {
    number: "03",
    title: "Correct",
    icon: Wrench,
    description: "The system selects a correction strategy, applies changes, and validates results.",
    artifacts: ["Patches", "Test results", "Rollback points"],
  },
  {
    number: "04",
    title: "Reinforce",
    icon: TrendingUp,
    description: "Successful corrections feed into long-term memory and influence future policies.",
    artifacts: ["Memory entries", "Policy updates", "Experiment IDs"],
  },
];

export function HowItWorks() {
  return (
    <section id="self-correction" className="py-20 lg:py-32 bg-muted/30">
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
            Runtime Loop
          </span>
          <h2 className="section-heading mb-4">
            How <span className="gradient-text">Self-Healing</span> Works
          </h2>
          <p className="section-subheading mx-auto">
            A continuous feedback loop that detects, analyzes, corrects, 
            and learns from every runtime event.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15, duration: 0.5 }}
              className="relative group"
            >
              {/* Connector line (desktop) */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-12 -right-4 w-8 h-0.5 bg-gradient-to-r from-accent/50 to-transparent z-10" />
              )}

              <div className="card-glass p-6 h-full group-hover:border-accent/40 transition-all duration-300">
                {/* Step number & icon */}
                <div className="flex items-center justify-between mb-6">
                  <span className="text-4xl font-extrabold text-muted-foreground/30">
                    {step.number}
                  </span>
                  <div className="w-12 h-12 rounded-xl gradient-accent flex items-center justify-center shadow-glow-accent">
                    <step.icon className="w-6 h-6 text-accent-foreground" />
                  </div>
                </div>

                {/* Title */}
                <h3 className="font-bold text-xl mb-3">{step.title}</h3>

                {/* Description */}
                <p className="text-muted-foreground text-sm mb-4 leading-relaxed">
                  {step.description}
                </p>

                {/* Artifacts */}
                <div className="flex flex-wrap gap-2">
                  {step.artifacts.map((artifact) => (
                    <span
                      key={artifact}
                      className="text-xs px-2.5 py-1 rounded-full bg-muted text-muted-foreground"
                    >
                      {artifact}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

import { motion } from "framer-motion";
// Phoenix Runtime - Metrics Section
import { TrendingDown, Clock, CheckCircle, Zap } from "lucide-react";

const metrics = [
  {
    icon: TrendingDown,
    value: "65%",
    label: "Reduction in MTTR",
    description: "Mean Time To Recovery compared to traditional ops",
  },
  {
    icon: Clock,
    value: "<5 min",
    label: "Auto-Resolution Time",
    description: "80% of incidents resolved automatically",
  },
  {
    icon: CheckCircle,
    value: "94%",
    label: "Fix Success Rate",
    description: "Corrections validated without rollback",
  },
  {
    icon: Zap,
    value: "3.2x",
    label: "Faster Deployment",
    description: "From detection to production patch",
  },
];

export function MetricsSection() {
  return (
    <section id="evaluation" className="py-20 lg:py-32">
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
            Benchmarks
          </span>
          <h2 className="section-heading mb-4">
            Proven <span className="gradient-text">Performance</span>
          </h2>
          <p className="section-subheading mx-auto">
            Real-world benchmarks comparing Phoenix against naive agents 
            and traditional manual operations.
          </p>
        </motion.div>

        {/* Metrics grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="text-center"
            >
              <div className="card-glass p-8 h-full">
                <div className="w-14 h-14 mx-auto rounded-2xl gradient-accent flex items-center justify-center mb-6 shadow-glow-accent">
                  <metric.icon className="w-7 h-7 text-accent-foreground" />
                </div>
                <div className="text-4xl lg:text-5xl font-extrabold gradient-text mb-2">
                  {metric.value}
                </div>
                <div className="font-semibold text-foreground mb-2">
                  {metric.label}
                </div>
                <p className="text-sm text-muted-foreground">
                  {metric.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Chart placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="card-glass p-8"
        >
          <div className="flex flex-col lg:flex-row items-center gap-8">
            {/* Chart */}
            <div className="flex-1 w-full">
              <div className="text-sm font-medium text-muted-foreground mb-4">
                Mean Time To Recovery (MTTR) Comparison
              </div>
              <div className="space-y-4">
                {[
                  { label: "Manual Ops", value: 45, color: "bg-destructive/60" },
                  { label: "Naive Agents", value: 28, color: "bg-amber-500/60" },
                  { label: "Phoenix Runtime", value: 8, color: "gradient-accent" },
                ].map((bar) => (
                  <div key={bar.label} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{bar.label}</span>
                      <span className="font-semibold">{bar.value} min</span>
                    </div>
                    <div className="h-3 bg-muted rounded-full overflow-hidden">
                      <motion.div
                        className={`h-full rounded-full ${bar.color}`}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${(bar.value / 45) * 100}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1, delay: 0.3 }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Stats cards */}
            <div className="lg:w-80 space-y-4">
              <div className="p-4 rounded-xl bg-accent/10 border border-accent/20">
                <div className="text-2xl font-bold text-accent mb-1">80%</div>
                <div className="text-sm text-muted-foreground">
                  Incidents auto-resolved in under 5 minutes
                </div>
              </div>
              <div className="p-4 rounded-xl bg-primary/10 border border-primary/20">
                <div className="text-2xl font-bold text-primary mb-1">Zero</div>
                <div className="text-sm text-muted-foreground">
                  Human intervention required for standard fixes
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

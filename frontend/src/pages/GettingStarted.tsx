import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowRight, ArrowLeft, Check, Copy, Terminal, 
  Zap, Code2, Play, ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const steps = [
  {
    number: "01",
    title: "Install Phoenix SDK",
    description: "Add Phoenix to your project using npm, pip, or your preferred package manager.",
    code: `# Using npm
npm install @phoenix/sdk

# Using pip
pip install phoenix-runtime

# Using go
go get github.com/phoenix/phoenix-go`,
  },
  {
    number: "02",
    title: "Initialize Your First Agent",
    description: "Create a basic agent with self-healing capabilities enabled.",
    code: `import { Phoenix, Agent } from '@phoenix/sdk';

const phoenix = new Phoenix({
  apiKey: process.env.PHOENIX_API_KEY,
});

const agent = new Agent({
  name: 'my-first-agent',
  role: 'executor',
  selfHealing: true,
});

await phoenix.deploy(agent);`,
  },
  {
    number: "03",
    title: "Configure Self-Correction",
    description: "Set up automatic error detection and correction policies.",
    code: `agent.configure({
  correction: {
    strategy: 'hybrid', // 'rule-based', 'ml', 'hybrid'
    maxRetries: 3,
    confidenceThreshold: 0.85,
  },
  memory: {
    shortTerm: true,
    longTerm: true,
    vectorStore: 'pinecone',
  },
});`,
  },
  {
    number: "04",
    title: "Monitor & Observe",
    description: "Watch your agent learn and improve in real-time through the dashboard.",
    code: `// Enable monitoring
agent.enableMonitoring({
  metrics: ['errors', 'corrections', 'latency'],
  alerts: {
    errorRate: 0.05,
    correctionTime: 5000,
  },
});

// Stream events
agent.on('correction', (event) => {
  console.log('Auto-corrected:', event);
});`,
  },
];

const nextSteps = [
  { title: "Explore the API Reference", href: "/docs/api", icon: Code2 },
  { title: "Set up multi-agent workflows", href: "/docs/multi-agent", icon: Zap },
  { title: "Configure production deployment", href: "/docs/deployment", icon: Play },
];

export default function GettingStarted() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Link
              to="/docs"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Docs
            </Link>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                <Terminal className="w-6 h-6 text-primary" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Tutorial</span>
                <h1 className="text-3xl md:text-4xl font-bold text-foreground">Getting Started</h1>
              </div>
            </div>

            <p className="text-lg text-muted-foreground">
              Learn how to build your first self-healing agent with Phoenix Runtime in under 10 minutes.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Steps */}
      <section className="pb-20 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="space-y-12">
            {steps.map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="relative"
              >
                {/* Connector line */}
                {i < steps.length - 1 && (
                  <div className="absolute left-6 top-16 bottom-0 w-px bg-gradient-to-b from-primary/50 to-transparent" />
                )}

                <div className="flex gap-6">
                  {/* Step number */}
                  <div className="relative shrink-0">
                    <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
                      <span className="text-sm font-bold text-primary">{step.number}</span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-foreground mb-2">{step.title}</h3>
                    <p className="text-muted-foreground mb-4">{step.description}</p>

                    {/* Code block */}
                    <div className="relative rounded-xl overflow-hidden bg-dark border border-border">
                      <div className="flex items-center justify-between px-4 py-2 bg-charcoal border-b border-border">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-red-500/50" />
                          <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                          <div className="w-3 h-3 rounded-full bg-green-500/50" />
                        </div>
                        <button className="p-1.5 rounded-md hover:bg-muted/50 transition-colors text-muted-foreground hover:text-foreground">
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      <pre className="p-4 text-sm text-muted-foreground overflow-x-auto">
                        <code>{step.code}</code>
                      </pre>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Success */}
      <section className="pb-20 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-8 rounded-2xl bg-gradient-to-r from-primary/20 via-primary/10 to-transparent border border-primary/30"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
                <Check className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-foreground mb-2">
                  Congratulations!
                </h3>
                <p className="text-muted-foreground">
                  You've successfully deployed your first self-healing agent. It's now running 
                  autonomously and will automatically detect and fix issues without human intervention.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-2xl font-bold text-foreground mb-6"
          >
            Next Steps
          </motion.h2>

          <div className="grid md:grid-cols-3 gap-4">
            {nextSteps.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Link
                  to={item.href}
                  className="flex items-center gap-3 p-4 rounded-xl bg-muted/20 border border-border hover:border-primary/30 hover:bg-muted/30 transition-all group"
                >
                  <item.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                  <span className="flex-1 text-sm font-medium text-foreground group-hover:text-primary transition-colors">
                    {item.title}
                  </span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

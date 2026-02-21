import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, ArrowRight, Clock, User, Tag,
  Cpu, Database, Workflow, Shield, BarChart3, FileCode,
  Rocket, Settings, Zap, Lock, Cloud, Server
} from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const guides = [
  {
    slug: "first-self-healing-agent",
    title: "Building Your First Self-Healing Agent",
    description: "Learn how to create an autonomous agent that can detect and fix its own errors without human intervention.",
    icon: Cpu,
    time: "10 min",
    author: "Phoenix Team",
    tags: ["Beginner", "Agents"],
    category: "Getting Started",
  },
  {
    slug: "memory-persistence",
    title: "Configuring Memory Persistence",
    description: "Set up long-term memory for your agents to retain context across sessions and improve over time.",
    icon: Database,
    time: "8 min",
    author: "Phoenix Team",
    tags: ["Intermediate", "Memory"],
    category: "Core Features",
  },
  {
    slug: "multi-agent-workflows",
    title: "Setting Up Multi-Agent Workflows",
    description: "Orchestrate multiple specialized agents to work together on complex tasks.",
    icon: Workflow,
    time: "15 min",
    author: "Phoenix Team",
    tags: ["Advanced", "Multi-Agent"],
    category: "Architecture",
  },
  {
    slug: "custom-correction-policies",
    title: "Implementing Custom Correction Policies",
    description: "Define custom rules and strategies for how your agents handle and recover from errors.",
    icon: Shield,
    time: "12 min",
    author: "Phoenix Team",
    tags: ["Advanced", "Self-Correction"],
    category: "Core Features",
  },
  {
    slug: "monitoring-metrics",
    title: "Monitoring and Metrics Best Practices",
    description: "Set up comprehensive monitoring for your Phoenix agents in production.",
    icon: BarChart3,
    time: "7 min",
    author: "Phoenix Team",
    tags: ["Intermediate", "DevOps"],
    category: "Production",
  },
  {
    slug: "production-deployment",
    title: "Production Deployment Guide",
    description: "Deploy your Phoenix agents to production with high availability and scalability.",
    icon: FileCode,
    time: "20 min",
    author: "Phoenix Team",
    tags: ["Advanced", "DevOps"],
    category: "Production",
  },
  {
    slug: "quick-start",
    title: "Phoenix Quick Start",
    description: "Get up and running with Phoenix in under 5 minutes with this quickstart guide.",
    icon: Rocket,
    time: "5 min",
    author: "Phoenix Team",
    tags: ["Beginner", "Setup"],
    category: "Getting Started",
  },
  {
    slug: "configuration-deep-dive",
    title: "Configuration Deep Dive",
    description: "Master all configuration options available in Phoenix for fine-tuned control.",
    icon: Settings,
    time: "15 min",
    author: "Phoenix Team",
    tags: ["Intermediate", "Configuration"],
    category: "Core Features",
  },
  {
    slug: "performance-optimization",
    title: "Performance Optimization",
    description: "Optimize your agents for speed, cost efficiency, and resource utilization.",
    icon: Zap,
    time: "12 min",
    author: "Phoenix Team",
    tags: ["Advanced", "Performance"],
    category: "Production",
  },
  {
    slug: "security-best-practices",
    title: "Security Best Practices",
    description: "Secure your Phoenix deployment with authentication, rate limiting, and data protection.",
    icon: Lock,
    time: "10 min",
    author: "Phoenix Team",
    tags: ["Intermediate", "Security"],
    category: "Production",
  },
  {
    slug: "cloud-deployment",
    title: "Cloud Provider Integration",
    description: "Deploy Phoenix to AWS, GCP, or Azure with managed infrastructure.",
    icon: Cloud,
    time: "18 min",
    author: "Phoenix Team",
    tags: ["Advanced", "Cloud"],
    category: "Production",
  },
  {
    slug: "self-hosted-setup",
    title: "Self-Hosted Setup",
    description: "Run Phoenix on your own infrastructure for maximum control and privacy.",
    icon: Server,
    time: "25 min",
    author: "Phoenix Team",
    tags: ["Advanced", "Self-Hosted"],
    category: "Production",
  },
];

const categories = ["All", "Getting Started", "Core Features", "Architecture", "Production"];

export default function Guides() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(249,115,22,0.08),transparent_60%)]" />
        
        <div className="container mx-auto max-w-6xl relative z-10">
          <Link 
            to="/docs"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Docs
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Guides & Tutorials
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl">
              Step-by-step tutorials to help you master Phoenix and build production-ready AI agents.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Category Filter */}
      <section className="px-4 pb-8">
        <div className="container mx-auto max-w-6xl">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  category === "All"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted/20 text-muted-foreground hover:bg-muted/40 hover:text-foreground"
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Guides Grid */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {guides.map((guide, i) => (
              <motion.div
                key={guide.slug}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <Link
                  to={`/docs/guides/${guide.slug}`}
                  className="group block h-full p-6 rounded-2xl bg-muted/10 border border-border hover:border-primary/30 transition-all hover:shadow-xl hover:shadow-primary/5"
                >
                  {/* Icon & Category */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                      <guide.icon className="w-6 h-6 text-primary" />
                    </div>
                    <span className="text-xs text-muted-foreground bg-muted/30 px-2 py-1 rounded-md">
                      {guide.category}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                    {guide.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {guide.description}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {guide.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 rounded-md bg-muted/50 text-xs text-muted-foreground"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      {guide.time}
                    </div>
                    <div className="flex items-center gap-1 text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                      Read guide
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>
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

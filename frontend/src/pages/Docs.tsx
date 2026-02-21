import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  Book, Code2, Boxes, Terminal, Zap, ArrowRight, 
  FileCode, Cpu, Database, Shield, Workflow, BarChart3,
  Search, ExternalLink
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const docCategories = [
  {
    title: "Getting Started",
    description: "Quick start guides and tutorials to get you up and running",
    icon: Zap,
    href: "/docs/getting-started",
    items: ["Quick Start Guide", "Installation", "First Agent", "Configuration"],
  },
  {
    title: "Core Concepts",
    description: "Understand the fundamental building blocks of Phoenix",
    icon: Boxes,
    href: "/docs/concepts",
    items: ["Agents", "Memory System", "Self-Correction", "Multi-Agent"],
  },
  {
    title: "API Reference",
    description: "Complete API documentation with examples",
    icon: Code2,
    href: "/docs/api",
    items: ["REST API", "WebSocket API", "Authentication", "Rate Limits"],
  },
  {
    title: "SDK Documentation",
    description: "Language-specific SDK guides and reference",
    icon: Terminal,
    href: "/docs/sdk",
    items: ["Python SDK", "JavaScript SDK", "Go SDK", "CLI Tools"],
  },
  {
    title: "Examples & Templates",
    description: "Production-ready examples and starter templates",
    icon: FileCode,
    href: "/docs/examples",
    items: ["Chatbots", "Research Agents", "Automation", "Templates"],
  },
  {
    title: "Integrations",
    description: "Connect Phoenix with your favorite tools",
    icon: Workflow,
    href: "/docs/integrations",
    items: ["LLM Providers", "Vector DBs", "Deployment", "Observability"],
  },
];

const popularGuides = [
  { title: "Building Your First Self-Healing Agent", icon: Cpu, time: "10 min" },
  { title: "Configuring Memory Persistence", icon: Database, time: "8 min" },
  { title: "Setting Up Multi-Agent Workflows", icon: Workflow, time: "15 min" },
  { title: "Implementing Custom Correction Policies", icon: Shield, time: "12 min" },
  { title: "Monitoring and Metrics Best Practices", icon: BarChart3, time: "7 min" },
  { title: "Production Deployment Guide", icon: FileCode, time: "20 min" },
];

export default function Docs() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="pt-32 pb-16 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(249,115,22,0.1),transparent_60%)]" />
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="container mx-auto text-center relative z-10 max-w-4xl"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-6">
            <Book className="w-4 h-4" />
            Documentation
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
            Learn to build with Phoenix
          </h1>

          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Comprehensive guides, API references, and examples to help you build 
            autonomous self-healing AI agents.
          </p>

          {/* Search */}
          <div className="relative max-w-xl mx-auto">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              placeholder="Search documentation..."
              className="h-14 pl-12 pr-4 text-base bg-muted/30 border-border focus:border-primary rounded-2xl"
            />
          </div>
        </motion.div>
      </section>

      {/* Doc Categories */}
      <section className="pb-20 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {docCategories.map((category, i) => (
              <motion.div
                key={category.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + i * 0.1 }}
              >
                <Link
                  to={category.href}
                  className="block p-6 rounded-2xl bg-muted/20 border border-border hover:border-primary/50 hover:bg-muted/30 transition-all group"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center shrink-0 group-hover:bg-primary/20 transition-colors">
                      <category.icon className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors flex items-center gap-2">
                        {category.title}
                        <ArrowRight className="w-4 h-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1 mb-3">
                        {category.description}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {category.items.map((item) => (
                          <span
                            key={item}
                            className="px-2 py-1 rounded-md bg-muted/50 text-xs text-muted-foreground"
                          >
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Guides */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-10"
          >
            <h2 className="text-2xl font-bold text-foreground mb-2">Popular Guides</h2>
            <p className="text-muted-foreground">Most viewed tutorials and walkthroughs</p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {popularGuides.map((guide, i) => (
              <motion.a
                key={i}
                href="#"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-4 p-4 rounded-xl bg-muted/10 border border-border/50 hover:border-primary/30 hover:bg-muted/20 transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-muted/50 flex items-center justify-center shrink-0 group-hover:bg-primary/10 transition-colors">
                  <guide.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-foreground truncate group-hover:text-primary transition-colors">
                    {guide.title}
                  </h4>
                  <p className="text-xs text-muted-foreground">{guide.time} read</p>
                </div>
              </motion.a>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-8 md:p-12 rounded-3xl glass border border-border/50 text-center"
          >
            <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
              Can't find what you're looking for?
            </h2>
            <p className="text-muted-foreground mb-6">
              Join our community or contact our support team for help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="btn-primary">
                Join Discord
                <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
              <Link to="/docs/support">
                <Button variant="outline" className="border-border/50 hover:bg-muted/50">
                  Contact Support
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

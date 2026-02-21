import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, Github, ExternalLink, Star, GitFork,
  MessageSquare, Search, FileText, ShoppingCart, 
  BarChart3, Mail, Code2, Cpu
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const examples = [
  {
    title: "Conversational Agent",
    description: "A self-correcting chatbot that maintains context and improves responses based on feedback.",
    category: "Chatbot",
    icon: MessageSquare,
    stars: 1240,
    forks: 189,
    difficulty: "Beginner",
    languages: ["Python", "TypeScript"],
    github: "https://github.com/phoenix-ai/examples/conversational-agent",
    demo: "#",
  },
  {
    title: "Research Assistant",
    description: "Multi-agent system that researches topics, fact-checks information, and generates reports.",
    category: "Research",
    icon: Search,
    stars: 892,
    forks: 134,
    difficulty: "Intermediate",
    languages: ["Python"],
    github: "https://github.com/phoenix-ai/examples/research-assistant",
    demo: "#",
  },
  {
    title: "Document Processor",
    description: "Autonomous agent that extracts, summarizes, and indexes information from documents.",
    category: "Document",
    icon: FileText,
    stars: 756,
    forks: 98,
    difficulty: "Intermediate",
    languages: ["Python", "Go"],
    github: "https://github.com/phoenix-ai/examples/document-processor",
    demo: "#",
  },
  {
    title: "E-commerce Agent",
    description: "Shopping assistant that handles product search, recommendations, and order tracking.",
    category: "Commerce",
    icon: ShoppingCart,
    stars: 623,
    forks: 87,
    difficulty: "Advanced",
    languages: ["TypeScript"],
    github: "https://github.com/phoenix-ai/examples/ecommerce-agent",
    demo: "#",
  },
  {
    title: "Analytics Pipeline",
    description: "Data analysis agent that queries databases, generates insights, and creates visualizations.",
    category: "Analytics",
    icon: BarChart3,
    stars: 534,
    forks: 72,
    difficulty: "Advanced",
    languages: ["Python"],
    github: "https://github.com/phoenix-ai/examples/analytics-pipeline",
    demo: "#",
  },
  {
    title: "Email Automation",
    description: "Agent that drafts, schedules, and sends personalized emails with self-correction.",
    category: "Automation",
    icon: Mail,
    stars: 445,
    forks: 61,
    difficulty: "Beginner",
    languages: ["Python", "TypeScript"],
    github: "https://github.com/phoenix-ai/examples/email-automation",
    demo: "#",
  },
];

const templates = [
  {
    name: "Phoenix Starter",
    description: "Minimal template to get started with Phoenix",
    command: "phoenix create my-app --template starter",
  },
  {
    name: "Multi-Agent System",
    description: "Template with orchestrated agent architecture",
    command: "phoenix create my-app --template multi-agent",
  },
  {
    name: "Production Ready",
    description: "Full production setup with monitoring and logging",
    command: "phoenix create my-app --template production",
  },
];

const difficultyColors: Record<string, string> = {
  Beginner: "bg-green-500/20 text-green-400 border-green-500/30",
  Intermediate: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  Advanced: "bg-red-500/20 text-red-400 border-red-500/30",
};

export default function Examples() {
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
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-4">
              <Code2 className="w-4 h-4" />
              Examples & Templates
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Learn by Example
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl">
              Production-ready examples and templates to accelerate your Phoenix development.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Templates */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-2xl font-bold text-foreground mb-6">Quick Start Templates</h2>
          
          <div className="grid md:grid-cols-3 gap-4">
            {templates.map((template, i) => (
              <motion.div
                key={template.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="p-5 rounded-2xl bg-muted/20 border border-border hover:border-primary/30 transition-all"
              >
                <h3 className="font-semibold text-foreground mb-2">{template.name}</h3>
                <p className="text-sm text-muted-foreground mb-4">{template.description}</p>
                <div className="p-3 rounded-lg bg-black border border-border/50">
                  <code className="text-xs text-primary font-mono">{template.command}</code>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Examples Grid */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-2xl font-bold text-foreground mb-6">Featured Examples</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {examples.map((example, i) => (
              <motion.div
                key={example.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group rounded-2xl bg-muted/10 border border-border hover:border-primary/30 overflow-hidden transition-all hover:shadow-xl hover:shadow-primary/5"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                      <example.icon className="w-6 h-6 text-primary" />
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${difficultyColors[example.difficulty]}`}>
                      {example.difficulty}
                    </span>
                  </div>

                  {/* Content */}
                  <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                    {example.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {example.description}
                  </p>

                  {/* Languages */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {example.languages.map((lang) => (
                      <span key={lang} className="px-2 py-1 rounded-md bg-muted/50 text-xs text-muted-foreground">
                        {lang}
                      </span>
                    ))}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4" />
                      {example.stars}
                    </div>
                    <div className="flex items-center gap-1">
                      <GitFork className="w-4 h-4" />
                      {example.forks}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <a
                      href={example.github}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1"
                    >
                      <Button variant="outline" className="w-full border-border/50 hover:bg-muted/50">
                        <Github className="w-4 h-4 mr-2" />
                        View Code
                      </Button>
                    </a>
                    <a href={example.demo} target="_blank" rel="noopener noreferrer">
                      <Button className="btn-primary">
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    </a>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-8 md:p-12 rounded-3xl glass border border-border/50 text-center"
          >
            <Cpu className="w-12 h-12 text-primary mx-auto mb-4" />
            <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
              Want to contribute?
            </h2>
            <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
              Share your Phoenix projects with the community. We feature the best examples in our showcase.
            </p>
            <Button className="btn-primary">
              <Github className="w-4 h-4 mr-2" />
              Submit Your Example
            </Button>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

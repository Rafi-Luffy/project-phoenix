import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Terminal, ExternalLink } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={copy}
      className="p-2 rounded-lg hover:bg-muted/50 transition-colors text-muted-foreground hover:text-foreground"
    >
      {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}

const sections = [
  {
    title: "Installation",
    content: `# macOS / Linux
curl -sSL https://get.phoenix.dev | bash

# Windows (PowerShell)
iwr https://get.phoenix.dev/install.ps1 -useb | iex

# Using Homebrew
brew install phoenix-ai/tap/phoenix

# Using npm (global)
npm install -g @phoenix-ai/cli`,
  },
  {
    title: "Authentication",
    content: `# Login to Phoenix
phoenix auth login

# Login with API key
phoenix auth login --api-key YOUR_API_KEY

# Check authentication status
phoenix auth status

# Logout
phoenix auth logout`,
  },
  {
    title: "Project Management",
    content: `# Initialize a new project
phoenix init my-project
cd my-project

# Initialize in existing directory
phoenix init .

# List all projects
phoenix projects list

# Switch projects
phoenix projects switch my-other-project

# Delete a project
phoenix projects delete my-project --confirm`,
  },
  {
    title: "Agent Commands",
    content: `# Create a new agent
phoenix agent create my-agent --model gpt-4

# List all agents
phoenix agent list

# Get agent details
phoenix agent info my-agent

# Update agent configuration
phoenix agent update my-agent --model gpt-4-turbo

# Delete an agent
phoenix agent delete my-agent

# Run an agent locally
phoenix agent run my-agent "Analyze this data"

# Run with streaming output
phoenix agent run my-agent "Generate report" --stream`,
  },
  {
    title: "Deployment",
    content: `# Deploy to development
phoenix deploy --env dev

# Deploy to production
phoenix deploy --env production

# Deploy with specific config
phoenix deploy --config phoenix.prod.yaml

# Check deployment status
phoenix deploy status

# Rollback deployment
phoenix deploy rollback --version v1.2.3

# View deployment history
phoenix deploy history`,
  },
  {
    title: "Logs & Monitoring",
    content: `# Stream logs
phoenix logs --follow

# Filter by agent
phoenix logs --agent my-agent

# Filter by level
phoenix logs --level error

# View metrics
phoenix metrics

# View specific metrics
phoenix metrics --agent my-agent --period 24h

# Export metrics
phoenix metrics export --format json > metrics.json`,
  },
  {
    title: "Interactive REPL",
    content: `# Start interactive session
phoenix repl

# Start with specific agent
phoenix repl --agent my-agent

# REPL commands:
# > /help          - Show help
# > /agents        - List agents
# > /switch agent  - Switch agent
# > /history       - Show history
# > /export        - Export conversation
# > /clear         - Clear screen
# > /exit          - Exit REPL`,
  },
  {
    title: "Configuration",
    content: `# View current config
phoenix config list

# Set configuration
phoenix config set default_model gpt-4
phoenix config set default_env production

# Get specific config
phoenix config get default_model

# Reset to defaults
phoenix config reset

# Edit config file directly
phoenix config edit`,
  },
  {
    title: "Workflows",
    content: `# Create a workflow
phoenix workflow create my-workflow

# Run a workflow
phoenix workflow run my-workflow

# List workflows
phoenix workflow list

# View workflow details
phoenix workflow info my-workflow

# Validate workflow file
phoenix workflow validate workflow.yaml`,
  },
];

const commands = [
  { name: "phoenix init", description: "Initialize a new Phoenix project" },
  { name: "phoenix agent", description: "Manage agents (create, list, update, delete)" },
  { name: "phoenix deploy", description: "Deploy agents to environments" },
  { name: "phoenix logs", description: "View and stream logs" },
  { name: "phoenix metrics", description: "View performance metrics" },
  { name: "phoenix repl", description: "Interactive agent session" },
  { name: "phoenix config", description: "Manage CLI configuration" },
  { name: "phoenix workflow", description: "Manage multi-agent workflows" },
];

export default function CLIDocs() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(168,85,247,0.1),transparent_60%)]" />
        
        <div className="container mx-auto max-w-4xl relative z-10">
          <Link 
            to="/docs/sdk"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to SDKs
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center gap-4 mb-6"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 flex items-center justify-center">
              <Terminal className="w-8 h-8 text-purple-400" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-foreground">CLI Tools</h1>
              <p className="text-muted-foreground">v1.2.0 • Command-line interface for Phoenix</p>
            </div>
          </motion.div>

          <div className="flex gap-3">
            <Link to="/docs/install">
              <Button className="btn-primary">
                <Terminal className="w-4 h-4 mr-2" />
                Install
              </Button>
            </Link>
            <a href="https://github.com/phoenix-agent/phoenix-cli" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" className="border-border/50">
                <ExternalLink className="w-4 h-4 mr-2" />
                GitHub
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Command Reference */}
      <section className="px-4 pb-12">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-2xl font-bold text-foreground mb-6">Command Reference</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {commands.map((cmd, i) => (
              <motion.div
                key={cmd.name}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="p-4 rounded-xl bg-muted/20 border border-border hover:border-primary/30 transition-colors"
              >
                <code className="text-primary font-mono font-semibold">{cmd.name}</code>
                <p className="text-sm text-muted-foreground mt-1">{cmd.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-4xl space-y-12">
          {sections.map((section, i) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
            >
              <h2 className="text-2xl font-bold text-foreground mb-4">{section.title}</h2>
              <div className="rounded-xl bg-black border border-border/50 overflow-hidden">
                <div className="flex items-center justify-between px-4 py-2 border-b border-border/50 bg-muted/20">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
                    </div>
                    <span className="text-xs text-muted-foreground">terminal</span>
                  </div>
                  <CopyButton text={section.content} />
                </div>
                <pre className="p-4 overflow-x-auto text-sm">
                  <code className="text-green-400/90 font-mono whitespace-pre">
                    {section.content}
                  </code>
                </pre>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      <Footer />
    </div>
  );
}

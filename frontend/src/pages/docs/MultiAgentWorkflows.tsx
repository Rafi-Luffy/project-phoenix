import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Users, Network, MessageSquare, Workflow } from "lucide-react";
import { useState } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return <button onClick={copy} className="p-2 rounded-lg hover:bg-muted/50 transition-colors text-muted-foreground hover:text-foreground">{copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}</button>;
}

const basicExample = `from phoenix import Agent, Orchestrator

# Define specialized agents
researcher = Agent(name="researcher", role="Research and gather information", model="gpt-4", self_healing=True)
analyst = Agent(name="analyst", role="Analyze data and extract insights", model="gpt-4", self_healing=True)
writer = Agent(name="writer", role="Create reports and summaries", model="gpt-4", self_healing=True)

# Create orchestrator
orchestrator = Orchestrator(agents=[researcher, analyst, writer], strategy="sequential")

# Run multi-agent workflow
result = await orchestrator.run("Research AI trends and create a comprehensive report")
print(result.final_output)`;

export default function MultiAgentWorkflows() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-5xl">
          <Link to="/docs/getting-started" className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"><ArrowLeft className="w-4 h-4" />Back to Getting Started</Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-4"><Users className="w-4 h-4" />Multi-Agent</div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Multi-Agent Workflows</h1>
            <p className="text-lg text-muted-foreground max-w-2xl">Orchestrate multiple specialized agents to solve complex tasks collaboratively.</p>
          </motion.div>
        </div>
      </section>
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl grid md:grid-cols-2 gap-6">
          {[{icon: Network, title: "Agent Networks", desc: "Connect agents in hierarchical or mesh topologies"}, {icon: MessageSquare, title: "Inter-Agent Communication", desc: "Agents share context and delegate tasks"}, {icon: Workflow, title: "Workflow Patterns", desc: "Sequential, parallel, and conditional execution"}, {icon: Users, title: "Role Specialization", desc: "Each agent optimized for specific tasks"}].map((f, i) => (
            <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }} className="p-6 rounded-xl bg-muted/20 border border-border">
              <f.icon className="w-8 h-8 text-primary mb-3" /><h3 className="font-semibold text-foreground mb-2">{f.title}</h3><p className="text-sm text-muted-foreground">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-6">Basic Multi-Agent Setup</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border"><span className="text-xs text-muted-foreground">multi_agent.py</span><CopyButton text={basicExample} /></div>
            <pre className="p-4 overflow-x-auto text-sm"><code className="text-green-400/90 font-mono whitespace-pre">{basicExample}</code></pre>
          </div>
        </div>
      </section>
      <Footer />
    </div>
  );
}

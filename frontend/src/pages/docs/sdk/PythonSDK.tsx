import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Terminal, BookOpen, ExternalLink } from "lucide-react";
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
    content: `# Using pip
pip install phoenix-ai

# Using poetry
poetry add phoenix-ai

# Using conda
conda install -c conda-forge phoenix-ai`,
  },
  {
    title: "Quick Start",
    content: `from phoenix import Phoenix, Agent

# Initialize the client
phoenix = Phoenix(api_key="your-api-key")

# Create a basic agent
agent = Agent(
    name="my-agent",
    model="gpt-4",
    self_healing=True
)

# Run the agent
response = agent.run("Analyze the latest market trends")
print(response.content)`,
  },
  {
    title: "Configuration",
    content: `from phoenix import Phoenix, AgentConfig, CorrectionConfig

# Advanced configuration
config = AgentConfig(
    name="production-agent",
    model="gpt-4",
    correction=CorrectionConfig(
        strategy="hybrid",
        max_retries=3,
        confidence_threshold=0.85
    ),
    memory={
        "short_term": True,
        "long_term": True,
        "vector_store": "pinecone"
    }
)

agent = phoenix.create_agent(config)`,
  },
  {
    title: "Async Support",
    content: `import asyncio
from phoenix import AsyncPhoenix, Agent

async def main():
    async with AsyncPhoenix(api_key="your-api-key") as phoenix:
        agent = Agent(name="async-agent", model="gpt-4")
        
        # Run multiple tasks concurrently
        tasks = [
            agent.arun("Task 1"),
            agent.arun("Task 2"),
            agent.arun("Task 3"),
        ]
        
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result.content)

asyncio.run(main())`,
  },
  {
    title: "Event Handling",
    content: `from phoenix import Agent, Event

agent = Agent(name="monitored-agent", model="gpt-4")

@agent.on("correction")
def handle_correction(event: Event):
    print(f"Auto-corrected: {event.original_error}")
    print(f"Fix applied: {event.correction}")

@agent.on("memory_update")
def handle_memory(event: Event):
    print(f"Memory updated: {event.key}")

# Run with event monitoring
response = agent.run("Complex task requiring self-correction")`,
  },
  {
    title: "Multi-Agent Workflows",
    content: `from phoenix import Phoenix, Agent, Workflow

phoenix = Phoenix()

# Create specialized agents
planner = Agent(name="planner", role="planner", model="gpt-4")
executor = Agent(name="executor", role="executor", model="gpt-4")
critic = Agent(name="critic", role="critic", model="gpt-4")

# Create a workflow
workflow = Workflow([planner, executor, critic])

# Execute with automatic coordination
result = workflow.run(
    task="Build a data pipeline for customer analytics",
    max_iterations=5
)`,
  },
  {
    title: "Type Hints & Pydantic",
    content: `from phoenix import Agent
from pydantic import BaseModel
from typing import List

class AnalysisResult(BaseModel):
    summary: str
    key_points: List[str]
    confidence: float

agent = Agent(
    name="typed-agent",
    model="gpt-4",
    output_model=AnalysisResult
)

# Get typed response
result: AnalysisResult = agent.run("Analyze Q4 sales data")
print(f"Summary: {result.summary}")
print(f"Confidence: {result.confidence}")`,
  },
];

const apiReference = [
  { name: "Phoenix", description: "Main client class for API interactions" },
  { name: "Agent", description: "Core agent class with self-healing capabilities" },
  { name: "Workflow", description: "Multi-agent workflow orchestration" },
  { name: "Memory", description: "Memory management and persistence" },
  { name: "Tool", description: "Custom tool definition and integration" },
  { name: "Event", description: "Event handling and monitoring" },
];

export default function PythonSDK() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(55,118,171,0.15),transparent_60%)]" />
        
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
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-yellow-500/20 border border-blue-500/30 flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="w-10 h-10">
                <path fill="#3776AB" d="M11.914 0C5.82 0 6.2 2.656 6.2 2.656l.007 2.752h5.814v.826H3.9S0 5.789 0 11.969c0 6.18 3.403 5.96 3.403 5.96h2.03v-2.867s-.109-3.42 3.35-3.42h5.766s3.24.052 3.24-3.148V3.202S18.28 0 11.914 0zM8.708 1.85c.578 0 1.046.47 1.046 1.052 0 .58-.468 1.051-1.046 1.051-.579 0-1.047-.47-1.047-1.051 0-.581.468-1.052 1.047-1.052z"/>
                <path fill="#FFD43B" d="M12.086 24c6.094 0 5.714-2.656 5.714-2.656l-.007-2.752h-5.814v-.826h8.121s3.9.445 3.9-5.735c0-6.18-3.403-5.96-3.403-5.96h-2.03v2.867s.109 3.42-3.35 3.42H9.451s-3.24-.052-3.24 3.148v5.292S5.72 24 12.086 24zm3.206-1.85c-.578 0-1.046-.47-1.046-1.052 0-.58.468-1.051 1.046-1.051.579 0 1.047.47 1.047 1.051 0 .581-.468 1.052-1.047 1.052z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-foreground">Python SDK</h1>
              <p className="text-muted-foreground">v1.4.2 • Full-featured SDK with async support</p>
            </div>
          </motion.div>

          <div className="flex gap-3">
            <Link to="/docs/install">
              <Button className="btn-primary">
                <Terminal className="w-4 h-4 mr-2" />
                Install
              </Button>
            </Link>
            <a href="https://github.com/phoenix-agent/phoenix-python" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" className="border-border/50">
                <ExternalLink className="w-4 h-4 mr-2" />
                GitHub
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="px-4 pb-16">
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
                    <span className="text-xs text-muted-foreground">python</span>
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

      {/* API Reference */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-2xl font-bold text-foreground mb-6">API Reference</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {apiReference.map((item, i) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="p-4 rounded-xl bg-muted/20 border border-border hover:border-primary/30 transition-colors"
              >
                <code className="text-primary font-mono font-semibold">{item.name}</code>
                <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

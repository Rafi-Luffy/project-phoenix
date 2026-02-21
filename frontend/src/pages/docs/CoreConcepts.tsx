import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, ArrowRight, Cpu, Brain, RefreshCw, Users, 
  Workflow, Database, Shield, Zap
} from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

interface ConceptContent {
  text: string;
  bold?: boolean;
}

interface Concept {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  content: ConceptContent[][];
  code: string;
}

const concepts: Concept[] = [
  {
    id: "agents",
    title: "Agents",
    icon: Cpu,
    description: "Autonomous AI entities that perceive, reason, and act",
    content: [
      [
        { text: "Agents are the fundamental building blocks of Phoenix Runtime. Each agent is an autonomous AI entity capable of:" }
      ],
      [
        { text: "Perception", bold: true },
        { text: ": Gathering information from its environment through sensors, APIs, or data streams" }
      ],
      [
        { text: "Reasoning", bold: true },
        { text: ": Processing information using LLMs to make decisions" }
      ],
      [
        { text: "Action", bold: true },
        { text: ": Executing tasks and interacting with external systems" }
      ],
      [
        { text: "Learning", bold: true },
        { text: ": Improving performance through feedback loops" }
      ],
      [
        { text: "Phoenix agents are designed to be stateless by default but can leverage the Memory System for persistence. They communicate through a standardized protocol that enables seamless coordination." }
      ]
    ],
    code: `from phoenix import Agent, Tool

class ResearchAgent(Agent):
    """An agent that researches topics autonomously."""
    
    tools = [
        Tool.web_search,
        Tool.summarize,
        Tool.save_to_memory
    ]
    
    def run(self, query: str) -> str:
        # Phoenix handles self-correction automatically
        results = self.search(query)
        summary = self.summarize(results)
        self.save_to_memory(summary)
        return summary`,
  },
  {
    id: "memory",
    title: "Memory System",
    icon: Database,
    description: "Persistent context and knowledge management",
    content: [
      [
        { text: "The Memory System provides agents with persistent context that survives across sessions. Phoenix implements three types of memory:" }
      ],
      [
        { text: "Short-term Memory", bold: true },
        { text: ": Conversation context and recent interactions (session-scoped)" }
      ],
      [
        { text: "Long-term Memory", bold: true },
        { text: ": Persistent knowledge, learned preferences, and historical data" }
      ],
      [
        { text: "Episodic Memory", bold: true },
        { text: ": Specific experiences and outcomes for reflection" }
      ],
      [
        { text: "Memory is automatically indexed and retrievable through semantic search, allowing agents to recall relevant context without explicit programming." }
      ]
    ],
    code: `from phoenix import Memory, Agent

# Configure memory for an agent
memory = Memory(
    short_term_size=1000,  # tokens
    long_term_store="vector",  # or "graph"
    embedding_model="phoenix-embed-v2"
)

agent = Agent(memory=memory)

# Memories are automatically managed
agent.remember("User prefers concise responses")
context = agent.recall("user preferences")`,
  },
  {
    id: "self-correction",
    title: "Self-Correction",
    icon: RefreshCw,
    description: "Autonomous error detection and recovery",
    content: [
      [
        { text: "Self-Correction is Phoenix's core innovation - enabling agents to detect, diagnose, and fix their own errors without human intervention." }
      ],
      [
        { text: "The correction pipeline:" }
      ],
      [
        { text: "1. Detection", bold: true },
        { text: ": Identify when an action fails or produces unexpected results" }
      ],
      [
        { text: "2. Diagnosis", bold: true },
        { text: ": Analyze the root cause using reflection patterns" }
      ],
      [
        { text: "3. Correction", bold: true },
        { text: ": Generate and validate alternative approaches" }
      ],
      [
        { text: "4. Execution", bold: true },
        { text: ": Retry with corrected strategy" }
      ],
      [
        { text: "5. Learning", bold: true },
        { text: ": Store the correction for future reference" }
      ],
      [
        { text: "Phoenix supports multiple correction strategies including Self-Refine, Reflexion, and Tree-of-Thoughts." }
      ]
    ],
    code: `from phoenix import Agent, CorrectionPolicy

# Configure correction behavior
agent = Agent(
    correction=CorrectionPolicy(
        max_retries=3,
        strategy="reflexion",  # or "self-refine", "tot"
        fallback="human-escalation"
    )
)

# Corrections happen automatically
@agent.task
def process_data(data):
    # If this fails, Phoenix will:
    # 1. Analyze the error
    # 2. Generate a fix
    # 3. Retry automatically
    return transform(data)`,
  },
  {
    id: "multi-agent",
    title: "Multi-Agent Orchestration",
    icon: Users,
    description: "Coordinating multiple agents for complex tasks",
    content: [
      [
        { text: "Phoenix enables sophisticated multi-agent workflows where specialized agents collaborate to achieve complex goals." }
      ],
      [
        { text: "Orchestration Patterns:", bold: true }
      ],
      [
        { text: "Pipeline", bold: true },
        { text: ": Sequential processing where each agent handles a stage" }
      ],
      [
        { text: "Parallel", bold: true },
        { text: ": Concurrent execution for independent subtasks" }
      ],
      [
        { text: "Hierarchical", bold: true },
        { text: ": Manager agents delegate to worker agents" }
      ],
      [
        { text: "Consensus", bold: true },
        { text: ": Multiple agents vote on decisions" }
      ],
      [
        { text: "Agents communicate through typed messages and can share memory contexts for coordination." }
      ]
    ],
    code: `from phoenix import Swarm, Agent

# Define specialized agents
researcher = Agent(role="researcher")
analyst = Agent(role="analyst")  
writer = Agent(role="writer")

# Create a coordinated swarm
swarm = Swarm(
    agents=[researcher, analyst, writer],
    pattern="pipeline",
    shared_memory=True
)

# Execute complex workflow
result = swarm.run("""
    Research recent AI developments,
    analyze key trends,
    write a summary report
""")`,
  },
];

function RenderContent({ content }: { content: ConceptContent[][] }) {
  return (
    <>
      {content.map((line, i) => (
        <p key={i} className="text-muted-foreground leading-relaxed mb-2">
          {line.map((segment, j) => (
            segment.bold ? (
              <strong key={j} className="text-foreground font-semibold">{segment.text}</strong>
            ) : (
              <span key={j}>{segment.text}</span>
            )
          ))}
        </p>
      ))}
    </>
  );
}

export default function CoreConcepts() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(249,115,22,0.08),transparent_60%)]" />
        
        <div className="container mx-auto max-w-5xl relative z-10">
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
              <Brain className="w-4 h-4" />
              Core Concepts
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Understanding Phoenix
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl">
              Master the fundamental building blocks that power autonomous, 
              self-healing AI agents.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Quick Navigation */}
      <section className="px-4 pb-12">
        <div className="container mx-auto max-w-5xl">
          <div className="flex flex-wrap gap-3">
            {concepts.map((concept) => (
              <a
                key={concept.id}
                href={`#${concept.id}`}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-muted/20 border border-border hover:border-primary/50 hover:bg-muted/30 transition-all text-sm font-medium text-muted-foreground hover:text-foreground"
              >
                <concept.icon className="w-4 h-4" />
                {concept.title}
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Concepts */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl space-y-16">
          {concepts.map((concept, index) => (
            <motion.div
              key={concept.id}
              id={concept.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5 }}
              className="scroll-mt-32"
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center shrink-0 border border-primary/20">
                  <concept.icon className="w-7 h-7 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-foreground mb-1">
                    {concept.title}
                  </h2>
                  <p className="text-muted-foreground">{concept.description}</p>
                </div>
              </div>

              <div className="grid lg:grid-cols-2 gap-6">
                {/* Content */}
                <div className="p-6 rounded-2xl bg-muted/10 border border-border/50">
                  <RenderContent content={concept.content} />
                </div>

                {/* Code */}
                <div className="rounded-2xl bg-black border border-border/50 overflow-hidden">
                  <div className="flex items-center gap-2 px-4 py-3 border-b border-border/50">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-red-500/80" />
                      <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                      <div className="w-3 h-3 rounded-full bg-green-500/80" />
                    </div>
                    <span className="text-xs text-muted-foreground ml-2">example.py</span>
                  </div>
                  <pre className="p-4 overflow-x-auto text-sm">
                    <code className="text-green-400/90 font-mono">
                      {concept.code}
                    </code>
                  </pre>
                </div>
              </div>

              {index < concepts.length - 1 && (
                <div className="mt-12 pt-12 border-t border-border/30" />
              )}
            </motion.div>
          ))}
        </div>
      </section>

      {/* Next Steps */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-8 rounded-3xl bg-gradient-to-br from-primary/10 to-accent/5 border border-primary/20"
          >
            <h3 className="text-xl font-bold text-foreground mb-4">Continue Learning</h3>
            <div className="grid sm:grid-cols-2 gap-4">
              <Link
                to="/docs/sdk"
                className="flex items-center justify-between p-4 rounded-xl bg-muted/30 border border-border/50 hover:border-primary/50 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-primary" />
                  <span className="font-medium text-foreground">SDK Documentation</span>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
              </Link>
              <Link
                to="/docs/api"
                className="flex items-center justify-between p-4 rounded-xl bg-muted/30 border border-border/50 hover:border-primary/50 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <Workflow className="w-5 h-5 text-primary" />
                  <span className="font-medium text-foreground">API Reference</span>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Link2, Layers, Cpu, Database } from "lucide-react";
import { useState } from "react";
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

const LangChainLogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="currentColor">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
    <path d="M8 12l2 2 4-4" stroke="currentColor" strokeWidth="2" fill="none"/>
  </svg>
);

const features = [
  {
    icon: Link2,
    title: "Chain Integration",
    description: "Use Phoenix agents as components in LangChain chains"
  },
  {
    icon: Layers,
    title: "Tool Support",
    description: "Convert LangChain tools to Phoenix tools automatically"
  },
  {
    icon: Cpu,
    title: "Self-Healing Chains",
    description: "Add self-correction to any LangChain pipeline"
  },
  {
    icon: Database,
    title: "Memory Bridge",
    description: "Sync memory between Phoenix and LangChain"
  }
];

const installCode = `pip install phoenix-ai langchain langchain-openai`;

const basicExample = `from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from phoenix.langchain import PhoenixWrapper, PhoenixAgent

# Create a LangChain agent
llm = ChatOpenAI(model="gpt-4")

tools = [
    Tool(
        name="calculator",
        func=lambda x: eval(x),
        description="Useful for math calculations"
    )
]

# Wrap with Phoenix for self-healing capabilities
phoenix_agent = PhoenixAgent(
    llm=llm,
    tools=tools,
    self_healing=True,
    correction_strategy="hybrid"
)

# Run with automatic error recovery
result = phoenix_agent.invoke({
    "input": "Calculate 15% of 847 and round to 2 decimal places"
})

print(result["output"])
# Corrections are tracked automatically
print(f"Self-corrections applied: {result['corrections']}")`;

const chainExample = `from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from phoenix.langchain import PhoenixChainWrapper

llm = ChatOpenAI(model="gpt-4")

# Create a multi-step chain
research_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["topic"],
        template="Research the following topic: {topic}"
    ),
    output_key="research"
)

summarize_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["research"],
        template="Summarize this research: {research}"
    ),
    output_key="summary"
)

# Create sequential chain
pipeline = SequentialChain(
    chains=[research_chain, summarize_chain],
    input_variables=["topic"],
    output_variables=["research", "summary"]
)

# Wrap entire pipeline with Phoenix self-healing
phoenix_pipeline = PhoenixChainWrapper(
    chain=pipeline,
    self_healing=True,
    max_retries=3,
    fallback_strategy="simplify"
)

result = phoenix_pipeline.invoke({
    "topic": "Quantum computing applications in cryptography"
})`;

const toolsExample = `from langchain.tools import BaseTool
from phoenix import Agent
from phoenix.langchain import langchain_to_phoenix_tool, phoenix_to_langchain_tool

# Convert LangChain tools to Phoenix format
class SearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information"
    
    def _run(self, query: str) -> str:
        # Search implementation
        return f"Results for: {query}"

# Use LangChain tools in Phoenix
phoenix_agent = Agent(
    name="hybrid-agent",
    tools=[
        langchain_to_phoenix_tool(SearchTool()),
        # Mix with native Phoenix tools
        "code_interpreter",
        "file_reader"
    ]
)

# Or use Phoenix tools in LangChain
from langchain.agents import initialize_agent, AgentType

langchain_agent = initialize_agent(
    tools=[
        phoenix_to_langchain_tool(phoenix_agent.get_tool("self_correct")),
        phoenix_to_langchain_tool(phoenix_agent.get_tool("memory_recall"))
    ],
    llm=ChatOpenAI(model="gpt-4"),
    agent=AgentType.OPENAI_FUNCTIONS
)`;

const memoryExample = `from langchain.memory import ConversationBufferMemory
from phoenix import Agent
from phoenix.langchain import PhoenixMemoryBridge

# Create LangChain memory
langchain_memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="chat_history"
)

# Bridge to Phoenix memory system
memory_bridge = PhoenixMemoryBridge(
    langchain_memory=langchain_memory,
    phoenix_memory_type="episodic",
    sync_mode="bidirectional"
)

# Now both systems share memory
phoenix_agent = Agent(
    name="memory-agent",
    memory=memory_bridge.phoenix_memory
)

# Memories sync automatically
result = phoenix_agent.run("Remember that my name is Alice")

# Access from LangChain
print(langchain_memory.load_memory_variables({}))
# {"chat_history": [..., "Remember that my name is Alice", ...]}`;

export default function LangChainIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(34,197,94,0.1),transparent_60%)]" />
        
        <div className="container mx-auto max-w-5xl relative z-10">
          <Link 
            to="/docs/sdk"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to SDK Reference
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center gap-6 mb-6"
          >
            <LangChainLogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                LangChain Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Add self-healing capabilities to your LangChain applications
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-4 rounded-xl bg-muted/20 border border-border"
              >
                <feature.icon className="w-8 h-8 text-green-500 mb-3" />
                <h3 className="font-semibold text-foreground mb-1">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Installation */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-6">Installation</h2>
          <div className="flex items-center gap-2 p-4 rounded-xl bg-black border border-border">
            <code className="flex-1 font-mono text-sm text-primary">{installCode}</code>
            <CopyButton text={installCode} />
          </div>
        </div>
      </section>

      {/* Basic Example */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Phoenix-Wrapped Agent</h2>
          <p className="text-muted-foreground mb-6">
            Wrap any LangChain agent with Phoenix for automatic self-healing and error recovery.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">phoenix_agent.py</span>
              <CopyButton text={basicExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{basicExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Chain Wrapper */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Self-Healing Chains</h2>
          <p className="text-muted-foreground mb-6">
            Wrap entire chain pipelines with Phoenix for end-to-end error correction.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">chain_wrapper.py</span>
              <CopyButton text={chainExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{chainExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Tools */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Tool Interoperability</h2>
          <p className="text-muted-foreground mb-6">
            Convert tools between LangChain and Phoenix formats seamlessly.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">tools.py</span>
              <CopyButton text={toolsExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{toolsExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Memory */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Memory Synchronization</h2>
          <p className="text-muted-foreground mb-6">
            Bridge memory systems between Phoenix and LangChain for unified context.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">memory_bridge.py</span>
              <CopyButton text={memoryExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{memoryExample}</code>
            </pre>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

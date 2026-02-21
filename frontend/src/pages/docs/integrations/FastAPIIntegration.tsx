import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Zap, Server, Shield, Gauge } from "lucide-react";
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

const FastAPILogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="#009688">
    <path d="M12 0L3 7.5V18l9 6 9-6V7.5L12 0zm0 3.5l6 4v7l-6 4-6-4v-7l6-4z"/>
  </svg>
);

const features = [
  {
    icon: Zap,
    title: "Async Native",
    description: "Full async/await support for non-blocking agent execution"
  },
  {
    icon: Server,
    title: "Dependency Injection",
    description: "Use FastAPI's DI system to manage Phoenix agents"
  },
  {
    icon: Shield,
    title: "Automatic Validation",
    description: "Pydantic models for request/response validation"
  },
  {
    icon: Gauge,
    title: "OpenAPI Docs",
    description: "Auto-generated API documentation for your agents"
  }
];

const installCode = `pip install phoenix-ai fastapi uvicorn`;

const basicExample = `from fastapi import FastAPI, Depends
from phoenix import Agent, Phoenix
from pydantic import BaseModel

app = FastAPI()
phoenix = Phoenix()

class AgentRequest(BaseModel):
    message: str
    context: dict = {}

class AgentResponse(BaseModel):
    response: str
    corrections: int
    confidence: float

# Create a reusable agent dependency
def get_agent():
    return Agent(
        name="api-agent",
        model="gpt-4",
        self_healing=True
    )

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    agent: Agent = Depends(get_agent)
):
    result = await agent.run(
        request.message,
        context=request.context
    )
    
    return AgentResponse(
        response=result.content,
        corrections=result.corrections_count,
        confidence=result.confidence
    )`;

const middlewareExample = `from fastapi import FastAPI, Request
from phoenix import Phoenix
from phoenix.middleware import PhoenixMiddleware

app = FastAPI()
phoenix = Phoenix()

# Add Phoenix middleware for automatic tracing
app.add_middleware(
    PhoenixMiddleware,
    phoenix=phoenix,
    trace_all_requests=True
)

@app.middleware("http")
async def add_phoenix_context(request: Request, call_next):
    # Add Phoenix context to all requests
    request.state.phoenix = phoenix
    response = await call_next(request)
    return response`;

const streamingExample = `from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from phoenix import Agent

app = FastAPI()

@app.post("/agent/stream")
async def stream_agent_response(message: str):
    agent = Agent(name="stream-agent", model="gpt-4")
    
    async def generate():
        async for chunk in agent.stream(message):
            yield f"data: {chunk.content}\\n\\n"
            
            if chunk.correction_applied:
                yield f"data: [CORRECTION] {chunk.correction_reason}\\n\\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )`;

export default function FastAPIIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(0,150,136,0.15),transparent_60%)]" />
        
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
            <FastAPILogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                FastAPI Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Build high-performance APIs with Phoenix agents
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
                <feature.icon className="w-8 h-8 text-[#009688] mb-3" />
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
          <h2 className="text-2xl font-bold text-foreground mb-4">Basic Usage</h2>
          <p className="text-muted-foreground mb-6">
            Create a FastAPI endpoint that runs a Phoenix agent with automatic request validation and dependency injection.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">main.py</span>
              <CopyButton text={basicExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{basicExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Middleware */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Phoenix Middleware</h2>
          <p className="text-muted-foreground mb-6">
            Add Phoenix middleware for automatic request tracing and context management.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">middleware.py</span>
              <CopyButton text={middlewareExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{middlewareExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Streaming */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Streaming Responses</h2>
          <p className="text-muted-foreground mb-6">
            Stream agent responses using Server-Sent Events for real-time updates.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">streaming.py</span>
              <CopyButton text={streamingExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{streamingExample}</code>
            </pre>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

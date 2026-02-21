import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Globe, Zap, Database, Shield } from "lucide-react";
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

const CloudflareLogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="#F38020">
    <path d="M16.5 14.5c.5-.3.5-1 0-1.3l-3-1.7c-.5-.3-1.1 0-1.1.6v3.4c0 .6.6 1 1.1.6l3-1.6zm-9-2.5c0-2.2 1.8-4 4-4s4 1.8 4 4-1.8 4-4 4-4-1.8-4-4z"/>
    <path d="M19.35 10.04A7.49 7.49 0 0012 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 000 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" fill="none" stroke="currentColor" strokeWidth="1.5"/>
  </svg>
);

const features = [
  {
    icon: Globe,
    title: "Edge Network",
    description: "Run agents on 300+ edge locations worldwide"
  },
  {
    icon: Zap,
    title: "Workers",
    description: "V8 isolates for instant cold starts"
  },
  {
    icon: Database,
    title: "D1 & KV",
    description: "Integrated storage for agent memory"
  },
  {
    icon: Shield,
    title: "Workers AI",
    description: "Run models directly on Cloudflare's GPUs"
  }
];

const installCode = `npm install @phoenix-ai/cloudflare wrangler`;

const workerExample = `// src/index.ts
import { Phoenix, Agent } from '@phoenix-ai/cloudflare';

export interface Env {
  PHOENIX_API_KEY: string;
  AGENT_KV: KVNamespace;
  AGENT_D1: D1Database;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const phoenix = new Phoenix({
      apiKey: env.PHOENIX_API_KEY,
      storage: {
        kv: env.AGENT_KV,
        d1: env.AGENT_D1,
      },
    });

    const agent = new Agent({
      name: 'edge-agent',
      model: 'gpt-4',
      selfHealing: true,
      maxRetries: 3,
    });

    try {
      const { message } = await request.json() as { message: string };
      
      const result = await agent.run(message);

      return Response.json({
        response: result.content,
        corrections: result.correctionsCount,
        edge: request.cf?.colo,
      });
    } catch (error) {
      return Response.json(
        { error: 'Agent execution failed' },
        { status: 500 }
      );
    }
  },
};`;

const wranglerConfig = `# wrangler.toml
name = "phoenix-agent"
main = "src/index.ts"
compatibility_date = "2024-01-01"
node_compat = true

[vars]
ENVIRONMENT = "production"

# Secrets (set via wrangler secret put)
# PHOENIX_API_KEY

# KV Namespace for agent memory
[[kv_namespaces]]
binding = "AGENT_KV"
id = "your-kv-namespace-id"

# D1 Database for structured storage
[[d1_databases]]
binding = "AGENT_D1"
database_name = "phoenix-agent-db"
database_id = "your-d1-database-id"

# Durable Objects for stateful agents
[[durable_objects.bindings]]
name = "AGENT_STATE"
class_name = "AgentState"

[[migrations]]
tag = "v1"
new_classes = ["AgentState"]`;

const durableObjectExample = `// src/agent-state.ts
import { Agent } from '@phoenix-ai/cloudflare';

export class AgentState {
  private state: DurableObjectState;
  private agent: Agent;
  private conversationHistory: string[] = [];

  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
    this.agent = new Agent({
      name: 'stateful-agent',
      model: 'gpt-4',
      selfHealing: true,
    });
  }

  async fetch(request: Request): Promise<Response> {
    const { message } = await request.json() as { message: string };
    
    // Load conversation history
    this.conversationHistory = 
      await this.state.storage.get('history') || [];
    
    // Run agent with context
    const result = await this.agent.run(message, {
      context: {
        history: this.conversationHistory,
      },
    });
    
    // Update history
    this.conversationHistory.push(message, result.content);
    await this.state.storage.put('history', this.conversationHistory);
    
    return Response.json({
      response: result.content,
      historyLength: this.conversationHistory.length,
    });
  }
}`;

const streamingExample = `// src/streaming.ts
import { Agent } from '@phoenix-ai/cloudflare';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { message } = await request.json() as { message: string };
    
    const agent = new Agent({
      name: 'stream-agent',
      model: 'gpt-4',
      selfHealing: true,
    });

    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();
    const encoder = new TextEncoder();

    // Stream in background
    (async () => {
      for await (const chunk of agent.stream(message)) {
        const data = JSON.stringify({
          content: chunk.content,
          done: chunk.done,
          correction: chunk.correctionApplied,
        });
        await writer.write(encoder.encode(\`data: \${data}\\n\\n\`));
      }
      await writer.close();
    })();

    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
    });
  },
};`;

const deployCommands = `# Login to Cloudflare
wrangler login

# Create KV namespace
wrangler kv:namespace create AGENT_KV

# Create D1 database
wrangler d1 create phoenix-agent-db

# Set secrets
wrangler secret put PHOENIX_API_KEY

# Deploy
wrangler deploy

# Tail logs
wrangler tail`;

export default function CloudflareIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(243,128,32,0.15),transparent_60%)]" />
        
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
            <CloudflareLogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                Cloudflare Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Deploy Phoenix agents globally on Cloudflare Workers
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
                <feature.icon className="w-8 h-8 text-[#F38020] mb-3" />
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

      {/* Worker */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Worker Handler</h2>
          <p className="text-muted-foreground mb-6">
            Basic Worker with Phoenix agent, KV storage, and D1 database.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">src/index.ts</span>
              <CopyButton text={workerExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{workerExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Wrangler Config */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Wrangler Configuration</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">wrangler.toml</span>
              <CopyButton text={wranglerConfig} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{wranglerConfig}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Durable Objects */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Stateful Agents with Durable Objects</h2>
          <p className="text-muted-foreground mb-6">
            Use Durable Objects to maintain conversation state across requests.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">src/agent-state.ts</span>
              <CopyButton text={durableObjectExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{durableObjectExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Streaming */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Streaming Responses</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">src/streaming.ts</span>
              <CopyButton text={streamingExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{streamingExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Deploy */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Deploy</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">Terminal</span>
              <CopyButton text={deployCommands} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{deployCommands}</code>
            </pre>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

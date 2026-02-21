import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Globe, Zap, Shield, BarChart3 } from "lucide-react";
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

const VercelLogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="currentColor">
    <path d="M12 1L24 22H0L12 1z"/>
  </svg>
);

const features = [
  {
    icon: Globe,
    title: "Edge Runtime",
    description: "Run agents at the edge for sub-100ms latency worldwide"
  },
  {
    icon: Zap,
    title: "Serverless",
    description: "Auto-scaling serverless functions with zero cold starts"
  },
  {
    icon: Shield,
    title: "Environment Variables",
    description: "Secure secret management for API keys"
  },
  {
    icon: BarChart3,
    title: "Analytics",
    description: "Built-in observability and performance monitoring"
  }
];

const installCode = `npm install @phoenix-ai/sdk @vercel/kv`;

const envExample = `# .env.local
PHOENIX_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key`;

const edgeFunctionExample = `// api/agent/route.ts
import { Agent } from '@phoenix-ai/sdk';

export const runtime = 'edge';

export async function POST(request: Request) {
  const { message, context } = await request.json();
  
  const agent = new Agent({
    name: 'edge-agent',
    model: 'gpt-4',
    selfHealing: true,
    maxRetries: 3,
  });

  try {
    const result = await agent.run(message, { context });
    
    return new Response(JSON.stringify({
      success: true,
      response: result.content,
      corrections: result.correctionsCount,
      latency: result.latencyMs,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: 'Agent execution failed',
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}`;

const streamingExample = `// api/agent/stream/route.ts
import { Agent } from '@phoenix-ai/sdk';

export const runtime = 'edge';

export async function POST(request: Request) {
  const { message } = await request.json();
  
  const agent = new Agent({
    name: 'stream-agent',
    model: 'gpt-4',
    selfHealing: true,
  });

  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      for await (const chunk of agent.stream(message)) {
        const data = JSON.stringify({
          content: chunk.content,
          done: chunk.done,
          correction: chunk.correctionApplied,
        });
        
        controller.enqueue(encoder.encode(\`data: \${data}\\n\\n\`));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}`;

const kvCacheExample = `// lib/agent-cache.ts
import { kv } from '@vercel/kv';
import { Agent } from '@phoenix-ai/sdk';

interface CachedResponse {
  content: string;
  timestamp: number;
  corrections: number;
}

export async function getCachedAgentResponse(
  message: string,
  ttlSeconds: number = 3600
): Promise<string> {
  const cacheKey = \`agent:\${Buffer.from(message).toString('base64')}\`;
  
  // Check cache
  const cached = await kv.get<CachedResponse>(cacheKey);
  if (cached) {
    console.log('Cache hit');
    return cached.content;
  }
  
  // Run agent
  const agent = new Agent({
    name: 'cached-agent',
    model: 'gpt-4',
    selfHealing: true,
  });
  
  const result = await agent.run(message);
  
  // Cache result
  await kv.set(cacheKey, {
    content: result.content,
    timestamp: Date.now(),
    corrections: result.correctionsCount,
  }, { ex: ttlSeconds });
  
  return result.content;
}`;

const vercelJsonExample = `{
  "functions": {
    "api/agent/**/*.ts": {
      "maxDuration": 60,
      "memory": 1024
    }
  },
  "env": {
    "PHOENIX_API_KEY": "@phoenix-api-key",
    "OPENAI_API_KEY": "@openai-api-key"
  }
}`;

export default function VercelIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(255,255,255,0.1),transparent_60%)]" />
        
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
            <VercelLogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                Vercel Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Deploy Phoenix agents globally with Vercel's edge network
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
                <feature.icon className="w-8 h-8 text-foreground mb-3" />
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
          <div className="flex items-center gap-2 p-4 rounded-xl bg-black border border-border mb-4">
            <code className="flex-1 font-mono text-sm text-primary">{installCode}</code>
            <CopyButton text={installCode} />
          </div>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">.env.local</span>
              <CopyButton text={envExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{envExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Edge Function */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Edge Functions</h2>
          <p className="text-muted-foreground mb-6">
            Deploy Phoenix agents as Vercel Edge Functions for ultra-low latency.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">api/agent/route.ts</span>
              <CopyButton text={edgeFunctionExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{edgeFunctionExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Streaming */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Streaming Responses</h2>
          <p className="text-muted-foreground mb-6">
            Stream agent responses using Server-Sent Events from the edge.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">api/agent/stream/route.ts</span>
              <CopyButton text={streamingExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{streamingExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* KV Cache */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Response Caching with Vercel KV</h2>
          <p className="text-muted-foreground mb-6">
            Cache agent responses using Vercel KV for faster repeated queries.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">lib/agent-cache.ts</span>
              <CopyButton text={kvCacheExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{kvCacheExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* vercel.json */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Configuration</h2>
          <p className="text-muted-foreground mb-6">
            Configure function settings and environment variables in vercel.json.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">vercel.json</span>
              <CopyButton text={vercelJsonExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{vercelJsonExample}</code>
            </pre>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Zap, Server, Shield, Gauge } from "lucide-react";
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

const NextJSLogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="currentColor">
    <path d="M11.572 0c-.176 0-.31.001-.358.007a19.76 19.76 0 0 1-.364.033C7.443.346 4.25 2.185 2.228 5.012a11.875 11.875 0 0 0-2.119 5.243c-.096.659-.108.854-.108 1.747s.012 1.089.108 1.748c.652 4.506 3.86 8.292 8.209 9.695.779.251 1.6.422 2.534.525.363.04 1.935.04 2.299 0 1.611-.178 2.977-.577 4.323-1.264.207-.106.247-.134.219-.158-.02-.013-.9-1.193-1.955-2.62l-1.919-2.592-2.404-3.558a338.739 338.739 0 0 0-2.422-3.556c-.009-.002-.018 1.579-.023 3.51-.007 3.38-.01 3.515-.052 3.595a.426.426 0 0 1-.206.214c-.075.037-.14.044-.495.044H7.81l-.108-.068a.438.438 0 0 1-.157-.171l-.049-.106.006-4.703.007-4.705.073-.091a.637.637 0 0 1 .174-.143c.096-.047.134-.051.54-.051.478 0 .558.018.682.154.035.038 1.337 1.999 2.895 4.361a10760.433 10760.433 0 0 0 4.735 7.17l1.9 2.879.096-.063a12.317 12.317 0 0 0 2.466-2.163 11.944 11.944 0 0 0 2.824-6.134c.096-.66.108-.854.108-1.748 0-.893-.012-1.088-.108-1.747-.652-4.506-3.859-8.292-8.208-9.695a12.597 12.597 0 0 0-2.499-.523A33.119 33.119 0 0 0 11.573 0zm4.069 7.217c.347 0 .408.005.486.047a.473.473 0 0 1 .237.277c.018.06.023 1.365.018 4.304l-.006 4.218-.744-1.14-.746-1.14v-3.066c0-1.982.01-3.097.023-3.15a.478.478 0 0 1 .233-.296c.096-.05.13-.054.5-.054z"/>
  </svg>
);

const features = [
  {
    icon: Zap,
    title: "App Router Ready",
    description: "Full support for Next.js 13+ App Router and Server Components"
  },
  {
    icon: Server,
    title: "API Routes",
    description: "Run Phoenix agents in Next.js API routes and Route Handlers"
  },
  {
    icon: Shield,
    title: "Edge Runtime",
    description: "Deploy agents to Vercel Edge for ultra-low latency"
  },
  {
    icon: Gauge,
    title: "React Hooks",
    description: "usePhoenix and useAgent hooks for seamless integration"
  }
];

const installCode = `npm install @phoenix-ai/sdk @phoenix-ai/next`;

const apiRouteExample = `// app/api/agent/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { Phoenix, Agent } from '@phoenix-ai/sdk';

const phoenix = new Phoenix({
  apiKey: process.env.PHOENIX_API_KEY!,
});

const agent = new Agent({
  name: 'nextjs-agent',
  model: 'gpt-4',
  selfHealing: true,
});

export async function POST(request: NextRequest) {
  const { message } = await request.json();
  
  const result = await agent.run(message);
  
  return NextResponse.json({
    response: result.content,
    corrections: result.correctionsCount,
    confidence: result.confidence,
  });
}`;

const serverComponentExample = `// app/agent/page.tsx
import { Phoenix, Agent } from '@phoenix-ai/sdk';

const phoenix = new Phoenix({
  apiKey: process.env.PHOENIX_API_KEY!,
});

async function getAgentResponse(query: string) {
  const agent = new Agent({
    name: 'server-agent',
    model: 'gpt-4',
    selfHealing: true,
  });
  
  return await agent.run(query);
}

export default async function AgentPage({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  const query = searchParams.q || 'Hello!';
  const result = await getAgentResponse(query);
  
  return (
    <div className="p-8">
      <h1>Agent Response</h1>
      <p>{result.content}</p>
      <span>Corrections: {result.correctionsCount}</span>
    </div>
  );
}`;

const clientHookExample = `// components/AgentChat.tsx
'use client';

import { useAgent } from '@phoenix-ai/next';
import { useState } from 'react';

export function AgentChat() {
  const [input, setInput] = useState('');
  const { 
    messages, 
    sendMessage, 
    isLoading, 
    corrections 
  } = useAgent({
    name: 'chat-agent',
    model: 'gpt-4',
    selfHealing: true,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>
            {msg.content}
          </div>
        ))}
      </div>
      
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the agent..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
      
      {corrections > 0 && (
        <p>Self-corrections applied: {corrections}</p>
      )}
    </div>
  );
}`;

const streamingExample = `// app/api/agent/stream/route.ts
import { NextRequest } from 'next/server';
import { Agent } from '@phoenix-ai/sdk';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  const { message } = await request.json();
  
  const agent = new Agent({
    name: 'stream-agent',
    model: 'gpt-4',
  });

  const stream = new ReadableStream({
    async start(controller) {
      for await (const chunk of agent.stream(message)) {
        const data = JSON.stringify({
          content: chunk.content,
          correction: chunk.correctionApplied,
        });
        controller.enqueue(\`data: \${data}\\n\\n\`);
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  });
}`;

export default function NextJSIntegration() {
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
            <NextJSLogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                Next.js Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Build full-stack AI applications with Phoenix and Next.js
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
          <div className="flex items-center gap-2 p-4 rounded-xl bg-black border border-border">
            <code className="flex-1 font-mono text-sm text-primary">{installCode}</code>
            <CopyButton text={installCode} />
          </div>
        </div>
      </section>

      {/* API Routes */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">API Route Handlers</h2>
          <p className="text-muted-foreground mb-6">
            Create API endpoints that run Phoenix agents using Next.js Route Handlers.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">app/api/agent/route.ts</span>
              <CopyButton text={apiRouteExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{apiRouteExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Server Components */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Server Components</h2>
          <p className="text-muted-foreground mb-6">
            Run Phoenix agents directly in React Server Components for SEO-friendly AI content.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">app/agent/page.tsx</span>
              <CopyButton text={serverComponentExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{serverComponentExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* React Hooks */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">React Hooks</h2>
          <p className="text-muted-foreground mb-6">
            Use the useAgent hook for interactive client-side agent experiences.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">components/AgentChat.tsx</span>
              <CopyButton text={clientHookExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{clientHookExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Streaming */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Edge Streaming</h2>
          <p className="text-muted-foreground mb-6">
            Stream agent responses from the Edge Runtime for the fastest possible experience.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">app/api/agent/stream/route.ts</span>
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

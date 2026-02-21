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
    content: `# Using npm
npm install @phoenix-ai/sdk

# Using yarn
yarn add @phoenix-ai/sdk

# Using pnpm
pnpm add @phoenix-ai/sdk`,
  },
  {
    title: "Quick Start",
    content: `import { Phoenix, Agent } from '@phoenix-ai/sdk';

// Initialize the client
const phoenix = new Phoenix({
  apiKey: process.env.PHOENIX_API_KEY
});

// Create a basic agent
const agent = new Agent({
  name: 'my-agent',
  model: 'gpt-4',
  selfHealing: true
});

// Run the agent
const response = await agent.run('Analyze the latest market trends');
console.log(response.content);`,
  },
  {
    title: "TypeScript Support",
    content: `import { Phoenix, Agent, AgentConfig, RunResult } from '@phoenix-ai/sdk';

interface AnalysisResult {
  summary: string;
  keyPoints: string[];
  confidence: number;
}

const config: AgentConfig = {
  name: 'typed-agent',
  model: 'gpt-4',
  correction: {
    strategy: 'hybrid',
    maxRetries: 3
  }
};

const agent = new Agent<AnalysisResult>(config);

const result: RunResult<AnalysisResult> = await agent.run(
  'Analyze Q4 performance',
  { outputSchema: AnalysisResult }
);

console.log(result.data.summary);`,
  },
  {
    title: "React Hooks",
    content: `import { useAgent, usePhoenix } from '@phoenix-ai/sdk/react';

function ChatComponent() {
  const phoenix = usePhoenix();
  const { agent, run, isLoading, error } = useAgent({
    name: 'chat-agent',
    model: 'gpt-4'
  });

  const handleSubmit = async (message: string) => {
    const response = await run(message);
    console.log(response);
  };

  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <button onClick={() => handleSubmit('Hello!')} disabled={isLoading}>
        {isLoading ? 'Thinking...' : 'Send'}
      </button>
    </div>
  );
}`,
  },
  {
    title: "Streaming Responses",
    content: `import { Agent } from '@phoenix-ai/sdk';

const agent = new Agent({
  name: 'streaming-agent',
  model: 'gpt-4'
});

// Stream responses
const stream = await agent.stream('Write a long analysis');

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}

// Or with callback
await agent.stream('Write analysis', {
  onToken: (token) => console.log(token),
  onComplete: (result) => console.log('Done:', result),
  onError: (error) => console.error(error)
});`,
  },
  {
    title: "Multi-Agent Workflows",
    content: `import { Phoenix, Agent, Workflow } from '@phoenix-ai/sdk';

const phoenix = new Phoenix();

// Create specialized agents
const planner = new Agent({ name: 'planner', role: 'planner' });
const executor = new Agent({ name: 'executor', role: 'executor' });
const critic = new Agent({ name: 'critic', role: 'critic' });

// Create and run workflow
const workflow = new Workflow([planner, executor, critic]);

const result = await workflow.run({
  task: 'Build a marketing campaign',
  maxIterations: 5,
  onProgress: (step) => console.log(\`Step \${step.index}: \${step.status}\`)
});`,
  },
  {
    title: "Event Handling",
    content: `import { Agent } from '@phoenix-ai/sdk';

const agent = new Agent({
  name: 'monitored-agent',
  model: 'gpt-4'
});

// Subscribe to events
agent.on('correction', (event) => {
  console.log('Auto-corrected:', event.originalError);
  console.log('Fix applied:', event.correction);
});

agent.on('memory:update', (event) => {
  console.log('Memory updated:', event.key);
});

agent.on('token', (token) => {
  process.stdout.write(token);
});

await agent.run('Complex task');`,
  },
  {
    title: "Next.js Integration",
    content: `// app/api/agent/route.ts
import { Phoenix, Agent } from '@phoenix-ai/sdk';
import { NextResponse } from 'next/server';

const phoenix = new Phoenix({
  apiKey: process.env.PHOENIX_API_KEY
});

export async function POST(request: Request) {
  const { message } = await request.json();
  
  const agent = new Agent({
    name: 'api-agent',
    model: 'gpt-4',
    selfHealing: true
  });

  const response = await agent.run(message);
  
  return NextResponse.json({ 
    content: response.content,
    corrections: response.corrections 
  });
}`,
  },
];

const apiReference = [
  { name: "Phoenix", description: "Main client class for API interactions" },
  { name: "Agent", description: "Core agent class with self-healing capabilities" },
  { name: "Workflow", description: "Multi-agent workflow orchestration" },
  { name: "useAgent", description: "React hook for agent management" },
  { name: "usePhoenix", description: "React context hook for Phoenix client" },
  { name: "StreamResult", description: "Async iterator for streaming responses" },
];

export default function JavaScriptSDK() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(247,223,30,0.1),transparent_60%)]" />
        
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
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="w-10 h-10">
                <rect width="24" height="24" fill="#F7DF1E"/>
                <path d="M6.375 19.646l1.82-1.102c.35.62.67 1.146 1.436 1.146.734 0 1.197-.288 1.197-1.406v-7.59h2.236v7.623c0 2.315-1.358 3.37-3.342 3.37-1.792 0-2.832-.928-3.347-2.04zm7.912-.237l1.82-1.054c.478.782 1.1 1.358 2.2 1.358.923 0 1.513-.462 1.513-1.1 0-.764-.606-1.035-1.625-1.48l-.558-.24c-1.61-.686-2.68-1.546-2.68-3.367 0-1.676 1.276-2.953 3.273-2.953 1.42 0 2.44.494 3.177 1.79l-1.74 1.117c-.383-.687-.797-.958-1.437-.958-.654 0-1.068.415-1.068.958 0 .67.414.942 1.37 1.358l.558.24c1.896.812 2.966 1.64 2.966 3.5 0 2.006-1.576 3.103-3.693 3.103-2.07 0-3.41-1.003-4.076-2.272z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-foreground">JavaScript SDK</h1>
              <p className="text-muted-foreground">v1.3.0 • TypeScript-first with React hooks</p>
            </div>
          </motion.div>

          <div className="flex gap-3">
            <Link to="/docs/install">
              <Button className="btn-primary">
                <Terminal className="w-4 h-4 mr-2" />
                Install
              </Button>
            </Link>
            <a href="https://github.com/phoenix-agent/phoenix-js" target="_blank" rel="noopener noreferrer">
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
                    <span className="text-xs text-muted-foreground">typescript</span>
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

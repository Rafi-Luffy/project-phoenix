import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Container, Layers, Shield, Terminal } from "lucide-react";
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

const DockerLogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="#2496ED">
    <path d="M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185zm-2.954-5.43h2.118a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.186zm0 2.716h2.118a.187.187 0 00.186-.186V6.29a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.887c0 .102.082.185.185.186zm-2.93 0h2.12a.186.186 0 00.184-.186V6.29a.185.185 0 00-.185-.185H8.1a.185.185 0 00-.185.185v1.887c0 .102.083.185.185.186zm-2.964 0h2.119a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H5.136a.186.186 0 00-.186.185v1.887c0 .102.084.185.186.186zm5.893 2.715h2.118a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185zm-2.93 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.083.185.185.185zm-2.964 0h2.119a.185.185 0 00.185-.185V9.006a.185.185 0 00-.184-.186h-2.12a.186.186 0 00-.186.186v1.887c0 .102.084.185.186.185zm-2.92 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.082.185.185.185zM23.763 9.89c-.065-.051-.672-.51-1.954-.51-.338.001-.676.03-1.01.087-.248-1.7-1.653-2.53-1.716-2.566l-.344-.199-.226.327c-.284.438-.49.922-.612 1.43-.23.97-.09 1.882.403 2.661-.595.332-1.55.413-1.744.42H.751a.751.751 0 00-.75.748 11.376 11.376 0 00.692 4.062c.545 1.428 1.355 2.48 2.41 3.124 1.18.723 3.1 1.137 5.275 1.137.983.003 1.963-.086 2.93-.266a12.248 12.248 0 003.823-1.389c.98-.567 1.86-1.288 2.61-2.136 1.252-1.418 1.998-2.997 2.553-4.4h.221c1.372 0 2.215-.549 2.68-1.009.309-.293.55-.65.707-1.046l.098-.288z"/>
  </svg>
);

const features = [
  {
    icon: Container,
    title: "Containerized Agents",
    description: "Package agents with all dependencies for consistent deployment"
  },
  {
    icon: Layers,
    title: "Multi-Stage Builds",
    description: "Optimized images with minimal footprint"
  },
  {
    icon: Shield,
    title: "Secrets Management",
    description: "Secure handling of API keys and credentials"
  },
  {
    icon: Terminal,
    title: "Docker Compose",
    description: "Multi-container setups with orchestration"
  }
];

const dockerfileExample = `# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 phoenix && chown -R phoenix:phoenix /app
USER phoenix

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python -c "from phoenix import Phoenix; Phoenix().health_check()"

# Run the agent
CMD ["python", "agent.py"]`;

const requirementsExample = `phoenix-ai>=1.4.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0`;

const agentCodeExample = `# agent.py
import os
from phoenix import Agent, Phoenix

phoenix = Phoenix(api_key=os.environ["PHOENIX_API_KEY"])

agent = Agent(
    name="docker-agent",
    model="gpt-4",
    self_healing=True,
    config={
        "max_retries": 3,
        "timeout": 30,
        "memory": {
            "type": "redis",
            "url": os.environ.get("REDIS_URL", "redis://redis:6379")
        }
    }
)

if __name__ == "__main__":
    # Run as standalone agent
    result = agent.run("Hello from Docker!")
    print(result.content)`;

const dockerComposeExample = `version: '3.8'

services:
  phoenix-agent:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - PHOENIX_API_KEY=\${PHOENIX_API_KEY}
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Optional: Phoenix monitoring UI
  phoenix-dashboard:
    image: phoenixai/dashboard:latest
    ports:
      - "3000:3000"
    environment:
      - PHOENIX_API_KEY=\${PHOENIX_API_KEY}
    depends_on:
      - phoenix-agent

volumes:
  redis_data:`;

const buildCommandsExample = `# Build the image
docker build -t phoenix-agent:latest .

# Run with environment variables
docker run -d \\
  --name my-agent \\
  -e PHOENIX_API_KEY=$PHOENIX_API_KEY \\
  -e OPENAI_API_KEY=$OPENAI_API_KEY \\
  phoenix-agent:latest

# Run with Docker Compose
docker-compose up -d

# Scale agents
docker-compose up -d --scale phoenix-agent=5

# View logs
docker-compose logs -f phoenix-agent`;

export default function DockerIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(36,150,237,0.15),transparent_60%)]" />
        
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
            <DockerLogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                Docker Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Containerize and deploy Phoenix agents anywhere
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
                <feature.icon className="w-8 h-8 text-[#2496ED] mb-3" />
                <h3 className="font-semibold text-foreground mb-1">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Dockerfile */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Optimized Dockerfile</h2>
          <p className="text-muted-foreground mb-6">
            Multi-stage build for minimal image size with all Phoenix dependencies.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">Dockerfile</span>
              <CopyButton text={dockerfileExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{dockerfileExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Requirements */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Dependencies</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">requirements.txt</span>
              <CopyButton text={requirementsExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{requirementsExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Agent Code */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Agent Code</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">agent.py</span>
              <CopyButton text={agentCodeExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{agentCodeExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Docker Compose */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Docker Compose</h2>
          <p className="text-muted-foreground mb-6">
            Multi-container setup with Redis for memory and optional dashboard.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">docker-compose.yml</span>
              <CopyButton text={dockerComposeExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{dockerComposeExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Build Commands */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Build and Run</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">Terminal</span>
              <CopyButton text={buildCommandsExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{buildCommandsExample}</code>
            </pre>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

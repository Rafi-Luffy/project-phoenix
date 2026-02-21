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
    content: `go get github.com/phoenix-ai/phoenix-go`,
  },
  {
    title: "Quick Start",
    content: `package main

import (
    "context"
    "fmt"
    "os"
    
    phoenix "github.com/phoenix-ai/phoenix-go"
)

func main() {
    // Initialize the client
    client := phoenix.NewClient(
        phoenix.WithAPIKey(os.Getenv("PHOENIX_API_KEY")),
    )
    defer client.Close()

    // Create an agent
    agent := client.NewAgent(phoenix.AgentConfig{
        Name:        "my-agent",
        Model:       "gpt-4",
        SelfHealing: true,
    })

    // Run the agent
    resp, err := agent.Run(context.Background(), "Analyze market trends")
    if err != nil {
        panic(err)
    }
    
    fmt.Println(resp.Content)
}`,
  },
  {
    title: "Configuration",
    content: `package main

import (
    phoenix "github.com/phoenix-ai/phoenix-go"
)

func main() {
    client := phoenix.NewClient(
        phoenix.WithAPIKey(os.Getenv("PHOENIX_API_KEY")),
        phoenix.WithBaseURL("https://api.phoenix.dev"),
        phoenix.WithTimeout(30 * time.Second),
        phoenix.WithRetries(3),
    )

    agent := client.NewAgent(phoenix.AgentConfig{
        Name:  "production-agent",
        Model: "gpt-4",
        Correction: phoenix.CorrectionConfig{
            Strategy:            "hybrid",
            MaxRetries:          3,
            ConfidenceThreshold: 0.85,
        },
        Memory: phoenix.MemoryConfig{
            ShortTerm:   true,
            LongTerm:    true,
            VectorStore: "pinecone",
        },
    })
}`,
  },
  {
    title: "Context Support",
    content: `package main

import (
    "context"
    "time"
    
    phoenix "github.com/phoenix-ai/phoenix-go"
)

func main() {
    client := phoenix.NewClient(phoenix.WithAPIKey(os.Getenv("PHOENIX_API_KEY")))
    agent := client.NewAgent(phoenix.AgentConfig{Name: "ctx-agent"})

    // With timeout
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    resp, err := agent.Run(ctx, "Long running task")
    if err != nil {
        if ctx.Err() == context.DeadlineExceeded {
            fmt.Println("Request timed out")
        }
        return
    }

    fmt.Println(resp.Content)
}`,
  },
  {
    title: "Streaming Responses",
    content: `package main

import (
    "context"
    "fmt"
    
    phoenix "github.com/phoenix-ai/phoenix-go"
)

func main() {
    client := phoenix.NewClient(phoenix.WithAPIKey(os.Getenv("PHOENIX_API_KEY")))
    agent := client.NewAgent(phoenix.AgentConfig{Name: "stream-agent"})

    stream, err := agent.Stream(context.Background(), "Write a detailed analysis")
    if err != nil {
        panic(err)
    }
    defer stream.Close()

    for {
        chunk, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            panic(err)
        }
        fmt.Print(chunk.Content)
    }
}`,
  },
  {
    title: "gRPC Transport",
    content: `package main

import (
    phoenix "github.com/phoenix-ai/phoenix-go"
    "google.golang.org/grpc"
)

func main() {
    // Use gRPC for lower latency
    client := phoenix.NewClient(
        phoenix.WithAPIKey(os.Getenv("PHOENIX_API_KEY")),
        phoenix.WithGRPC(
            grpc.WithInsecure(),
            grpc.WithBlock(),
        ),
    )

    agent := client.NewAgent(phoenix.AgentConfig{
        Name:  "grpc-agent",
        Model: "gpt-4",
    })

    // All operations use gRPC
    resp, _ := agent.Run(context.Background(), "Fast request")
    fmt.Println(resp.Content)
}`,
  },
  {
    title: "Prometheus Metrics",
    content: `package main

import (
    "net/http"
    
    phoenix "github.com/phoenix-ai/phoenix-go"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
    client := phoenix.NewClient(
        phoenix.WithAPIKey(os.Getenv("PHOENIX_API_KEY")),
        phoenix.WithMetrics(phoenix.MetricsConfig{
            Enabled:   true,
            Namespace: "phoenix",
            Subsystem: "agent",
        }),
    )

    // Expose metrics endpoint
    http.Handle("/metrics", promhttp.Handler())
    go http.ListenAndServe(":9090", nil)

    agent := client.NewAgent(phoenix.AgentConfig{Name: "monitored-agent"})
    
    // Metrics automatically collected
    resp, _ := agent.Run(context.Background(), "Task")
    fmt.Println(resp.Content)
}`,
  },
  {
    title: "Multi-Agent Workflows",
    content: `package main

import (
    "context"
    
    phoenix "github.com/phoenix-ai/phoenix-go"
)

func main() {
    client := phoenix.NewClient(phoenix.WithAPIKey(os.Getenv("PHOENIX_API_KEY")))

    // Create specialized agents
    planner := client.NewAgent(phoenix.AgentConfig{Name: "planner", Role: "planner"})
    executor := client.NewAgent(phoenix.AgentConfig{Name: "executor", Role: "executor"})
    critic := client.NewAgent(phoenix.AgentConfig{Name: "critic", Role: "critic"})

    // Create workflow
    workflow := client.NewWorkflow(planner, executor, critic)

    result, err := workflow.Run(context.Background(), phoenix.WorkflowInput{
        Task:          "Build data pipeline",
        MaxIterations: 5,
    })
    if err != nil {
        panic(err)
    }

    fmt.Println(result.Output)
}`,
  },
];

const apiReference = [
  { name: "Client", description: "Main client for API interactions" },
  { name: "Agent", description: "Core agent with self-healing capabilities" },
  { name: "Workflow", description: "Multi-agent workflow orchestration" },
  { name: "Stream", description: "Streaming response iterator" },
  { name: "AgentConfig", description: "Agent configuration options" },
  { name: "CorrectionConfig", description: "Self-correction settings" },
];

export default function GoSDK() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(0,173,216,0.1),transparent_60%)]" />
        
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
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="w-10 h-10" fill="#00ADD8">
                <path d="M1.811 10.231c-.047 0-.058-.023-.035-.059l.246-.315c.023-.035.081-.058.128-.058h4.172c.046 0 .058.035.035.07l-.199.303c-.023.036-.082.07-.117.07zM.047 11.306c-.047 0-.059-.023-.035-.058l.245-.316c.023-.035.082-.058.129-.058h5.328c.047 0 .07.035.058.07l-.093.28c-.012.047-.058.07-.105.07zm2.828 1.075c-.047 0-.059-.035-.035-.07l.163-.292c.023-.035.07-.07.117-.07h2.337c.047 0 .07.035.07.082l-.023.28c0 .047-.047.082-.082.082zm12.129-2.36c-.736.187-1.239.327-1.963.514-.176.046-.187.058-.34-.117-.175-.199-.303-.327-.548-.444-.737-.362-1.45-.257-2.115.175-.795.514-1.204 1.274-1.192 2.22.011.935.654 1.706 1.577 1.835.795.105 1.46-.175 1.987-.771.105-.13.198-.27.315-.434H10.47c-.245 0-.304-.152-.222-.35.152-.362.432-.97.596-1.274a.315.315 0 01.292-.187h4.253c-.023.316-.023.631-.07.947a4.983 4.983 0 01-.958 2.29c-.841 1.11-1.94 1.8-3.33 1.986-1.145.152-2.209-.07-3.143-.77-.865-.655-1.356-1.52-1.484-2.595-.152-1.274.222-2.419.993-3.424.83-1.086 1.928-1.776 3.272-2.02 1.098-.2 2.15-.07 3.096.571.62.398 1.11.947 1.449 1.614.082.128.012.199-.129.245z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-foreground">Go SDK</h1>
              <p className="text-muted-foreground">v0.9.1 • High-performance with gRPC support</p>
            </div>
          </motion.div>

          <div className="flex gap-3">
            <Link to="/docs/install">
              <Button className="btn-primary">
                <Terminal className="w-4 h-4 mr-2" />
                Install
              </Button>
            </Link>
            <a href="https://github.com/phoenix-ai/phoenix-go" target="_blank" rel="noopener noreferrer">
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
                    <span className="text-xs text-muted-foreground">go</span>
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

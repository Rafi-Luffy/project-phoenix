import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, Terminal, Copy, Check, ExternalLink,
  BookOpen, Package
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

// SDK Logo components
const PythonLogo = () => (
  <svg viewBox="0 0 24 24" className="w-10 h-10">
    <path fill="#3776AB" d="M11.914 0C5.82 0 6.2 2.656 6.2 2.656l.007 2.752h5.814v.826H3.9S0 5.789 0 11.969c0 6.18 3.403 5.96 3.403 5.96h2.03v-2.867s-.109-3.42 3.35-3.42h5.766s3.24.052 3.24-3.148V3.202S18.28 0 11.914 0zM8.708 1.85c.578 0 1.046.47 1.046 1.052 0 .58-.468 1.051-1.046 1.051-.579 0-1.047-.47-1.047-1.051 0-.581.468-1.052 1.047-1.052z"/>
    <path fill="#FFD43B" d="M12.086 24c6.094 0 5.714-2.656 5.714-2.656l-.007-2.752h-5.814v-.826h8.121s3.9.445 3.9-5.735c0-6.18-3.403-5.96-3.403-5.96h-2.03v2.867s.109 3.42-3.35 3.42H9.451s-3.24-.052-3.24 3.148v5.292S5.72 24 12.086 24zm3.206-1.85c-.578 0-1.046-.47-1.046-1.052 0-.58.468-1.051 1.046-1.051.579 0 1.047.47 1.047 1.051 0 .581-.468 1.052-1.047 1.052z"/>
  </svg>
);

const JavaScriptLogo = () => (
  <svg viewBox="0 0 24 24" className="w-10 h-10">
    <rect width="24" height="24" fill="#F7DF1E"/>
    <path d="M6.375 19.646l1.82-1.102c.35.62.67 1.146 1.436 1.146.734 0 1.197-.288 1.197-1.406v-7.59h2.236v7.623c0 2.315-1.358 3.37-3.342 3.37-1.792 0-2.832-.928-3.347-2.04zm7.912-.237l1.82-1.054c.478.782 1.1 1.358 2.2 1.358.923 0 1.513-.462 1.513-1.1 0-.764-.606-1.035-1.625-1.48l-.558-.24c-1.61-.686-2.68-1.546-2.68-3.367 0-1.676 1.276-2.953 3.273-2.953 1.42 0 2.44.494 3.177 1.79l-1.74 1.117c-.383-.687-.797-.958-1.437-.958-.654 0-1.068.415-1.068.958 0 .67.414.942 1.37 1.358l.558.24c1.896.812 2.966 1.64 2.966 3.5 0 2.006-1.576 3.103-3.693 3.103-2.07 0-3.41-1.003-4.076-2.272z"/>
  </svg>
);

const GoLogo = () => (
  <svg viewBox="0 0 24 24" className="w-10 h-10" fill="#00ADD8">
    <path d="M1.811 10.231c-.047 0-.058-.023-.035-.059l.246-.315c.023-.035.081-.058.128-.058h4.172c.046 0 .058.035.035.07l-.199.303c-.023.036-.082.07-.117.07zM.047 11.306c-.047 0-.059-.023-.035-.058l.245-.316c.023-.035.082-.058.129-.058h5.328c.047 0 .07.035.058.07l-.093.28c-.012.047-.058.07-.105.07zm2.828 1.075c-.047 0-.059-.035-.035-.07l.163-.292c.023-.035.07-.07.117-.07h2.337c.047 0 .07.035.07.082l-.023.28c0 .047-.047.082-.082.082zm12.129-2.36c-.736.187-1.239.327-1.963.514-.176.046-.187.058-.34-.117-.175-.199-.303-.327-.548-.444-.737-.362-1.45-.257-2.115.175-.795.514-1.204 1.274-1.192 2.22.011.935.654 1.706 1.577 1.835.795.105 1.46-.175 1.987-.771.105-.13.198-.27.315-.434H10.47c-.245 0-.304-.152-.222-.35.152-.362.432-.97.596-1.274a.315.315 0 01.292-.187h4.253c-.023.316-.023.631-.07.947a4.983 4.983 0 01-.958 2.29c-.841 1.11-1.94 1.8-3.33 1.986-1.145.152-2.209-.07-3.143-.77-.865-.655-1.356-1.52-1.484-2.595-.152-1.274.222-2.419.993-3.424.83-1.086 1.928-1.776 3.272-2.02 1.098-.2 2.15-.07 3.096.571.62.398 1.11.947 1.449 1.614.082.128.012.199-.129.245z"/>
  </svg>
);

const CLILogo = () => (
  <svg viewBox="0 0 24 24" className="w-10 h-10" fill="currentColor">
    <rect x="2" y="3" width="20" height="18" rx="2" stroke="currentColor" strokeWidth="2" fill="none"/>
    <path d="M6 9l3 3-3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <line x1="12" y1="15" x2="18" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

const sdks = [
  {
    id: "python",
    name: "Python SDK",
    version: "1.4.2",
    Logo: PythonLogo,
    color: "from-blue-500/20 to-yellow-500/20",
    borderColor: "border-blue-500/30",
    install: "pip install phoenix-ai",
    description: "Full-featured SDK with async support, type hints, and Pydantic models.",
    features: ["Async/await support", "Type hints", "Pydantic models", "Streaming responses"],
    quickstart: `from phoenix import Agent, Tool

# Create an agent
agent = Agent(
    name="assistant",
    model="gpt-4",
    tools=[Tool.web_search, Tool.calculator]
)

# Run with self-correction enabled
response = agent.run("Calculate the GDP growth rate for 2024")
print(response)`,
    docs: "/docs/sdk/python",
    installLink: "/docs/install",
  },
  {
    id: "javascript",
    name: "JavaScript SDK",
    version: "1.3.0",
    Logo: JavaScriptLogo,
    color: "from-yellow-500/20 to-orange-500/20",
    borderColor: "border-yellow-500/30",
    install: "npm install @phoenix-ai/sdk",
    description: "TypeScript-first SDK for Node.js and browser environments.",
    features: ["TypeScript support", "Browser compatible", "React hooks", "Next.js ready"],
    quickstart: `import { Phoenix, Agent } from '@phoenix-ai/sdk';

// Initialize Phoenix
const phoenix = new Phoenix({ apiKey: process.env.PHOENIX_KEY });

// Create and run an agent
const agent = new Agent({
  name: 'assistant',
  model: 'gpt-4',
  tools: ['web_search', 'calculator']
});

const response = await agent.run('Analyze market trends');
console.log(response);`,
    docs: "/docs/sdk/javascript",
    installLink: "/docs/install",
  },
  {
    id: "go",
    name: "Go SDK",
    version: "0.9.1",
    Logo: GoLogo,
    color: "from-cyan-500/20 to-blue-500/20",
    borderColor: "border-cyan-500/30",
    install: "go get github.com/phoenix-ai/phoenix-go",
    description: "High-performance SDK for production systems and microservices.",
    features: ["Zero allocations", "Context support", "gRPC transport", "Prometheus metrics"],
    quickstart: `package main

import (
    "context"
    "fmt"
    phoenix "github.com/phoenix-ai/phoenix-go"
)

func main() {
    client := phoenix.NewClient(phoenix.WithAPIKey(os.Getenv("PHOENIX_KEY")))
    
    agent := client.NewAgent(phoenix.AgentConfig{
        Name:  "assistant",
        Model: "gpt-4",
    })
    
    resp, _ := agent.Run(context.Background(), "Analyze system performance")
    fmt.Println(resp.Content)
}`,
    docs: "/docs/sdk/go",
    installLink: "/docs/install",
  },
  {
    id: "cli",
    name: "CLI Tools",
    version: "1.2.0",
    Logo: CLILogo,
    color: "from-purple-500/20 to-pink-500/20",
    borderColor: "border-purple-500/30",
    install: "curl -sSL https://get.phoenix.dev | bash",
    description: "Command-line tools for managing agents, deployments, and monitoring.",
    features: ["Agent management", "Deployment automation", "Log streaming", "Interactive REPL"],
    quickstart: `# Initialize a new project
phoenix init my-agent-project

# Run an agent locally
phoenix run agent.yaml

# Deploy to production
phoenix deploy --env production

# Stream logs
phoenix logs --follow`,
    docs: "/docs/cli",
    installLink: "/docs/install",
  },
];

// Framework integration logos
const FastAPILogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="#009688">
    <path d="M12 0L3 7.5V18l9 6 9-6V7.5L12 0zm0 3.5l6 4v7l-6 4-6-4v-7l6-4z"/>
  </svg>
);

const NextJSLogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
    <path d="M12 1.5C6.21 1.5 1.5 6.21 1.5 12S6.21 22.5 12 22.5 22.5 17.79 22.5 12 17.79 1.5 12 1.5zM9.75 15.75V8.25l6.75 4.5-6.75 3z"/>
  </svg>
);

const LangChainLogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
    <path d="M8 12l2 2 4-4" stroke="currentColor" strokeWidth="2" fill="none"/>
  </svg>
);

const VercelLogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
    <path d="M12 1L24 22H0L12 1z"/>
  </svg>
);

const DockerLogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="#2496ED">
    <path d="M13 11h2v2h-2zm-3 0h2v2h-2zm-3 0h2v2H7zm-3 0h2v2H4zm3-3h2v2H7zm3 0h2v2h-2zm3 0h2v2h-2zm0-3h2v2h-2zM4 14h18c-1 5-5 8-10 8S2 19 1 14h3z"/>
  </svg>
);

const KubernetesLogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="#326CE5">
    <path d="M12 2L4 6v12l8 4 8-4V6l-8-4zm0 3l5 2.5v7L12 17l-5-2.5v-7L12 5z"/>
  </svg>
);

const AWSLogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6 text-primary">
    <text x="6" y="16" fontSize="12" fontWeight="bold" fill="currentColor">λ</text>
  </svg>
);

const CloudflareLogo = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="#F38020">
    <path d="M16.5 14.5c.5-.3.5-1 0-1.3l-3-1.7c-.5-.3-1.1 0-1.1.6v3.4c0 .6.6 1 1.1.6l3-1.6zm-9-2.5c0-2.2 1.8-4 4-4s4 1.8 4 4-1.8 4-4 4-4-1.8-4-4z"/>
  </svg>
);

const frameworkLogos: Record<string, React.FC> = {
  "FastAPI": FastAPILogo,
  "Next.js": NextJSLogo,
  "LangChain": LangChainLogo,
  "Vercel": VercelLogo,
  "Docker": DockerLogo,
  "Kubernetes": KubernetesLogo,
  "AWS Lambda": AWSLogo,
  "Cloudflare": CloudflareLogo,
};

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

export default function SDKReference() {
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
              <Terminal className="w-4 h-4" />
              SDK Documentation
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Build with Phoenix
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl">
              Official SDKs and CLI tools to integrate Phoenix into your applications 
              across multiple languages and platforms.
            </p>
          </motion.div>
        </div>
      </section>

      {/* SDKs */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl space-y-8">
          {sdks.map((sdk, index) => (
            <motion.div
              key={sdk.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`rounded-3xl bg-gradient-to-br ${sdk.color} border ${sdk.borderColor} overflow-hidden`}
            >
              <div className="p-6 md:p-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                  <div className="flex items-center gap-4">
                    <sdk.Logo />
                    <div>
                      <h2 className="text-2xl font-bold text-foreground">{sdk.name}</h2>
                      <p className="text-sm text-muted-foreground">v{sdk.version}</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <Link to={sdk.docs}>
                      <Button variant="outline" className="border-border/50 hover:bg-muted/50">
                        <BookOpen className="w-4 h-4 mr-2" />
                        Full Docs
                      </Button>
                    </Link>
                    <Link to={sdk.installLink || "/docs/install"}>
                      <Button className="btn-primary">
                        <Package className="w-4 h-4 mr-2" />
                        Install
                      </Button>
                    </Link>
                  </div>
                </div>

                <p className="text-muted-foreground mb-4">{sdk.description}</p>

                {/* Features */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {sdk.features.map((feature) => (
                    <span
                      key={feature}
                      className="px-3 py-1 rounded-full bg-muted/30 text-xs font-medium text-foreground"
                    >
                      {feature}
                    </span>
                  ))}
                </div>

                {/* Install Command */}
                <div className="mb-6">
                  <p className="text-sm text-muted-foreground mb-2">Installation</p>
                  <div className="flex items-center gap-2 p-3 rounded-xl bg-black border border-border/50">
                    <code className="flex-1 font-mono text-sm text-primary">{sdk.install}</code>
                    <CopyButton text={sdk.install} />
                  </div>
                </div>

                {/* Quick Start */}
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Quick Start</p>
                  <div className="rounded-xl bg-black border border-border/50 overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-border/50">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1.5">
                          <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                          <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                          <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
                        </div>
                        <span className="text-xs text-muted-foreground">quickstart</span>
                      </div>
                      <CopyButton text={sdk.quickstart} />
                    </div>
                    <pre className="p-4 overflow-x-auto text-sm">
                      <code className="text-green-400/90 font-mono whitespace-pre">
                        {sdk.quickstart}
                      </code>
                    </pre>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Integration Examples */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Framework Integrations
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Phoenix works seamlessly with popular frameworks and platforms
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { name: "FastAPI", href: "/docs/integrations/fastapi" },
              { name: "Next.js", href: "/docs/integrations/nextjs" },
              { name: "LangChain", href: "/docs/integrations/langchain" },
              { name: "Vercel", href: "/docs/integrations/vercel" },
              { name: "Docker", href: "/docs/integrations/docker" },
              { name: "Kubernetes", href: "/docs/integrations/k8s" },
              { name: "AWS Lambda", href: "/docs/integrations/lambda" },
              { name: "Cloudflare", href: "/docs/integrations/cloudflare" },
            ].map((integration, i) => {
              const LogoComponent = frameworkLogos[integration.name];
              return (
                <motion.div
                  key={integration.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    to={integration.href}
                    className="flex items-center gap-3 p-4 rounded-xl bg-muted/10 border border-border/50 hover:border-primary/30 hover:bg-muted/20 transition-all group"
                  >
                    <div className="text-muted-foreground group-hover:text-primary transition-colors">
                      {LogoComponent && <LogoComponent />}
                    </div>
                    <span className="font-medium text-foreground group-hover:text-primary transition-colors">
                      {integration.name}
                    </span>
                    <ExternalLink className="w-4 h-4 ml-auto text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </Link>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

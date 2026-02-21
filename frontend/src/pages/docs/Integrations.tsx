import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, ExternalLink, CheckCircle2,
  Zap, Code2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

// SVG Logo components
const OpenAILogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.8956zm16.0993 3.8558L12.6 8.3829l2.02-1.1638a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.1408 1.6465 4.4708 4.4708 0 0 1 .5765 3.0137zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z"/>
  </svg>
);

const AnthropicLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M17.304 3.541h-3.48l6.201 16.918h3.48L17.304 3.541zm-10.609 0L.494 20.459h3.48l1.309-3.678h6.221l1.309 3.678h3.48L10.092 3.541H6.695zm-.607 10.387 2.21-6.202 2.21 6.202H6.088z"/>
  </svg>
);

const GoogleLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
);

const MistralLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <rect x="2" y="2" width="5" height="5" />
    <rect x="17" y="2" width="5" height="5" />
    <rect x="2" y="9" width="5" height="5" />
    <rect x="9" y="9" width="5" height="5" />
    <rect x="17" y="9" width="5" height="5" />
    <rect x="2" y="17" width="5" height="5" />
    <rect x="9" y="17" width="5" height="5" />
    <rect x="17" y="17" width="5" height="5" />
  </svg>
);

const OllamaLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
    <circle cx="12" cy="12" r="4" />
  </svg>
);

const AzureLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#0078D4">
    <path d="M13.05 4.24L6.56 18.05l-3.81.66 9.3-14.47h1zm-1.69 14.91l6.47-2.02L14.75 6.9l-3.13 5.28 3.37 6.23-3.63.74z"/>
  </svg>
);

const PineconeLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M12 2L4 6v12l8 4 8-4V6l-8-4zm0 2.5L18 8v8l-6 3-6-3V8l6-3.5z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const WeaviateLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <polygon points="12,2 22,8 22,16 12,22 2,16 2,8"/>
  </svg>
);

const QdrantLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 3l6 3-6 3-6-3 6-3z"/>
  </svg>
);

const ChromaLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8">
    <circle cx="8" cy="8" r="4" fill="#FF6B6B"/>
    <circle cx="16" cy="8" r="4" fill="#4ECDC4"/>
    <circle cx="12" cy="16" r="4" fill="#45B7D1"/>
  </svg>
);

const LangChainLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l7.59-7.59L20 8l-9 9z"/>
  </svg>
);

const LlamaIndexLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
  </svg>
);

const CrewAILogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <circle cx="8" cy="8" r="3"/>
    <circle cx="16" cy="8" r="3"/>
    <circle cx="12" cy="16" r="3"/>
    <line x1="8" y1="11" x2="12" y2="13" stroke="currentColor" strokeWidth="1"/>
    <line x1="16" y1="11" x2="12" y2="13" stroke="currentColor" strokeWidth="1"/>
  </svg>
);

const AutoGenLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46A7.93 7.93 0 0020 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74A7.93 7.93 0 004 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
  </svg>
);

const VercelLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <path d="M12 1L24 22H0L12 1z"/>
  </svg>
);

const AWSLambdaLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8 text-primary">
    <text x="6" y="18" fontSize="16" fontWeight="bold" fill="currentColor">λ</text>
  </svg>
);

const DockerLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#2496ED">
    <path d="M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185zm-2.954-5.43h2.118a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.186zm0 2.716h2.118a.187.187 0 00.186-.186V6.29a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.887c0 .102.082.185.185.186zm-2.93 0h2.12a.186.186 0 00.184-.186V6.29a.185.185 0 00-.185-.185H8.1a.185.185 0 00-.185.185v1.887c0 .102.083.185.185.186zm-2.964 0h2.119a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H5.136a.186.186 0 00-.186.185v1.887c0 .102.084.185.186.186zm5.893 2.715h2.118a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185zm-2.93 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.083.185.185.185zm-2.964 0h2.119a.185.185 0 00.185-.185V9.006a.185.185 0 00-.184-.186h-2.12a.186.186 0 00-.186.186v1.887c0 .102.084.185.186.185zm-2.92 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.082.185.185.185zM23.763 9.89c-.065-.051-.672-.51-1.954-.51-.338.001-.676.03-1.01.087-.248-1.7-1.653-2.53-1.716-2.566l-.344-.199-.226.327c-.284.438-.49.922-.612 1.43-.23.97-.09 1.882.403 2.661-.595.332-1.55.413-1.744.42H.751a.751.751 0 00-.75.748 11.376 11.376 0 00.692 4.062c.545 1.428 1.355 2.48 2.41 3.124 1.18.723 3.1 1.137 5.275 1.137.983.003 1.963-.086 2.93-.266a12.248 12.248 0 003.823-1.389c.98-.567 1.86-1.288 2.61-2.136 1.252-1.418 1.998-2.997 2.553-4.4h.221c1.372 0 2.215-.549 2.68-1.009.309-.293.55-.65.707-1.046l.098-.288z"/>
  </svg>
);

const KubernetesLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#326CE5">
    <path d="M10.204 14.35l.007.01-.999 2.413a5.171 5.171 0 01-2.075-2.597l2.578-.437.004.005a.44.44 0 01.485.606zm-.833-2.129a.44.44 0 00.173-.756l.002-.011L7.585 9.7a5.143 5.143 0 00-.73 3.255l2.514-.725.002-.009zm1.145-1.98a.44.44 0 00.699-.337l-.01-.002.3-2.627a5.07 5.07 0 00-2.85 1.534l1.86 1.43.001.002zm8.143-.576a5.167 5.167 0 00-.73-3.255l-1.963 1.754.002.011a.44.44 0 00.173.756l.002.01 2.514.724h.002zM12 16.018c-.14 0-.28.014-.417.04l-.007.007-1.093 2.341a5.158 5.158 0 002.985.029l-1.053-2.376-.007-.007A1.52 1.52 0 0012 16.018zm-.182-3.285a.44.44 0 00-.609-.147.44.44 0 00-.147.609l1.063 1.846a1.49 1.49 0 00-.307-2.308z"/>
  </svg>
);

const DatadogLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#632CA6">
    <path d="M12.012 0L0 8.555v6.89L12.012 24l12.012-8.555v-6.89L12.012 0zM5.06 12.53a1.587 1.587 0 110-3.174 1.587 1.587 0 010 3.174z"/>
  </svg>
);

const LangSmithLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
    <circle cx="12" cy="12" r="3"/>
    <line x1="12" y1="2" x2="12" y2="6" stroke="currentColor" strokeWidth="2"/>
    <line x1="12" y1="18" x2="12" y2="22" stroke="currentColor" strokeWidth="2"/>
    <line x1="2" y1="12" x2="6" y2="12" stroke="currentColor" strokeWidth="2"/>
    <line x1="18" y1="12" x2="22" y2="12" stroke="currentColor" strokeWidth="2"/>
  </svg>
);

const WandBLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="currentColor">
    <rect x="3" y="14" width="4" height="6" rx="1"/>
    <rect x="10" y="8" width="4" height="12" rx="1"/>
    <rect x="17" y="4" width="4" height="16" rx="1"/>
  </svg>
);

const PrometheusLogo = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#E6522C">
    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 22.5c-5.799 0-10.5-4.701-10.5-10.5S6.201 1.5 12 1.5 22.5 6.201 22.5 12 17.799 22.5 12 22.5z"/>
    <path d="M12 4.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM12 16.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM18 10.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM6 10.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/>
  </svg>
);

const logoComponents: Record<string, React.FC> = {
  "OpenAI": OpenAILogo,
  "Anthropic": AnthropicLogo,
  "Google AI": GoogleLogo,
  "Mistral": MistralLogo,
  "Ollama": OllamaLogo,
  "Azure OpenAI": AzureLogo,
  "Pinecone": PineconeLogo,
  "Weaviate": WeaviateLogo,
  "Qdrant": QdrantLogo,
  "Chroma": ChromaLogo,
  "LangChain": LangChainLogo,
  "LlamaIndex": LlamaIndexLogo,
  "CrewAI": CrewAILogo,
  "AutoGen": AutoGenLogo,
  "Vercel": VercelLogo,
  "AWS Lambda": AWSLambdaLogo,
  "Docker": DockerLogo,
  "Kubernetes": KubernetesLogo,
  "Datadog": DatadogLogo,
  "LangSmith": LangSmithLogo,
  "Weights & Biases": WandBLogo,
  "Prometheus": PrometheusLogo,
};

const integrations = [
  {
    category: "LLM Providers",
    items: [
      {
        name: "OpenAI",
        description: "GPT-4, GPT-3.5, and embedding models",
        features: ["Streaming", "Function calling", "Vision"],
        status: "Stable",
      },
      {
        name: "Anthropic",
        description: "Claude 3 Opus, Sonnet, and Haiku models",
        features: ["Long context", "Tool use", "Vision"],
        status: "Stable",
      },
      {
        name: "Google AI",
        description: "Gemini Pro and Ultra models",
        features: ["Multimodal", "Long context", "Grounding"],
        status: "Stable",
      },
      {
        name: "Mistral",
        description: "Mistral Large, Medium, and Small",
        features: ["Fast inference", "Open weights", "EU hosted"],
        status: "Stable",
      },
      {
        name: "Ollama",
        description: "Run local models with full Phoenix support",
        features: ["Local inference", "Privacy", "No API costs"],
        status: "Stable",
      },
      {
        name: "Azure OpenAI",
        description: "Enterprise-grade OpenAI deployment",
        features: ["Compliance", "Private endpoints", "SLA"],
        status: "Stable",
      },
    ],
  },
  {
    category: "Vector Databases",
    items: [
      {
        name: "Pinecone",
        description: "Managed vector database for production",
        features: ["Serverless", "Metadata filtering", "Namespaces"],
        status: "Stable",
      },
      {
        name: "Weaviate",
        description: "Open-source vector search engine",
        features: ["GraphQL", "Hybrid search", "Modules"],
        status: "Stable",
      },
      {
        name: "Qdrant",
        description: "High-performance vector similarity search",
        features: ["Fast", "Filtering", "Payload support"],
        status: "Stable",
      },
      {
        name: "Chroma",
        description: "Lightweight embedding database",
        features: ["Simple API", "Python native", "In-memory"],
        status: "Stable",
      },
    ],
  },
  {
    category: "Frameworks",
    items: [
      {
        name: "LangChain",
        description: "Use Phoenix agents within LangChain pipelines",
        features: ["Chains", "Agents", "Memory"],
        status: "Stable",
      },
      {
        name: "LlamaIndex",
        description: "RAG integration for document processing",
        features: ["Indexing", "Retrieval", "Agents"],
        status: "Beta",
      },
      {
        name: "CrewAI",
        description: "Multi-agent collaboration framework",
        features: ["Crews", "Tasks", "Processes"],
        status: "Beta",
      },
      {
        name: "AutoGen",
        description: "Microsoft's multi-agent framework",
        features: ["Conversations", "Code execution", "Human loop"],
        status: "Beta",
      },
    ],
  },
  {
    category: "Deployment",
    items: [
      {
        name: "Vercel",
        description: "Deploy Phoenix agents as serverless functions",
        features: ["Edge runtime", "Auto-scaling", "Analytics"],
        status: "Stable",
      },
      {
        name: "AWS Lambda",
        description: "Run agents in AWS serverless environment",
        features: ["VPC support", "Layers", "Event triggers"],
        status: "Stable",
      },
      {
        name: "Docker",
        description: "Container-based deployment",
        features: ["Portable", "Orchestration", "Scaling"],
        status: "Stable",
      },
      {
        name: "Kubernetes",
        description: "Production-grade orchestration",
        features: ["Helm charts", "Auto-scaling", "Rolling updates"],
        status: "Stable",
      },
    ],
  },
  {
    category: "Observability",
    items: [
      {
        name: "Datadog",
        description: "APM and monitoring integration",
        features: ["Traces", "Metrics", "Logs"],
        status: "Stable",
      },
      {
        name: "LangSmith",
        description: "LLM observability and debugging",
        features: ["Tracing", "Evaluation", "Datasets"],
        status: "Stable",
      },
      {
        name: "Weights & Biases",
        description: "Experiment tracking and evaluation",
        features: ["Runs", "Artifacts", "Tables"],
        status: "Beta",
      },
      {
        name: "Prometheus",
        description: "Metrics collection and alerting",
        features: ["Custom metrics", "Grafana", "Alerts"],
        status: "Stable",
      },
    ],
  },
];

const statusColors: Record<string, string> = {
  Stable: "bg-green-500/20 text-green-400",
  Beta: "bg-yellow-500/20 text-yellow-400",
  Alpha: "bg-orange-500/20 text-orange-400",
};

export default function Integrations() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(249,115,22,0.08),transparent_60%)]" />
        
        <div className="container mx-auto max-w-6xl relative z-10">
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
              <Zap className="w-4 h-4" />
              Integrations
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Connect Everything
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl">
              Phoenix integrates with your favorite tools, LLM providers, vector databases, 
              and deployment platforms.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Integrations by Category */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-6xl space-y-16">
          {integrations.map((category, categoryIndex) => (
            <motion.div
              key={category.category}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: categoryIndex * 0.1 }}
            >
              <h2 className="text-2xl font-bold text-foreground mb-6">{category.category}</h2>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {category.items.map((item, i) => {
                  const LogoComponent = logoComponents[item.name];
                  return (
                    <motion.div
                      key={item.name}
                      initial={{ opacity: 0, scale: 0.95 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.05 }}
                      className="group p-5 rounded-2xl bg-muted/10 border border-border hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5"
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors">
                          {LogoComponent ? <LogoComponent /> : <Code2 className="w-8 h-8" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                              {item.name}
                            </h3>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[item.status]}`}>
                              {item.status}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            {item.description}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {item.features.map((feature) => (
                              <span
                                key={feature}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-muted/30 text-xs text-muted-foreground"
                              >
                                <CheckCircle2 className="w-3 h-3 text-primary" />
                                {feature}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Request Integration */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-8 md:p-12 rounded-3xl glass border border-border/50 text-center"
          >
            <Code2 className="w-12 h-12 text-primary mx-auto mb-4" />
            <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
              Need a different integration?
            </h2>
            <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
              Let us know what integration you need and we'll prioritize it on our roadmap.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/docs/integrations/request">
                <Button className="btn-primary">
                  Request Integration
                </Button>
              </Link>
              <Link to="/docs/integrations/custom">
                <Button variant="outline" className="border-border/50 hover:bg-muted/50">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Build Custom Integration
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

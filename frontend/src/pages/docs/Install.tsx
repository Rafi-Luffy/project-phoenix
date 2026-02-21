import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Terminal, Package, Download, CheckCircle2 } from "lucide-react";
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

// Language/Framework icons as SVG components
const PythonIcon = () => (
  <svg viewBox="0 0 256 255" className="w-8 h-8">
    <defs>
      <linearGradient id="python-a" x1="12.959%" x2="79.639%" y1="12.039%" y2="78.201%">
        <stop offset="0%" stopColor="#387EB8"/>
        <stop offset="100%" stopColor="#366994"/>
      </linearGradient>
      <linearGradient id="python-b" x1="19.128%" x2="90.742%" y1="20.579%" y2="88.429%">
        <stop offset="0%" stopColor="#FFE052"/>
        <stop offset="100%" stopColor="#FFC331"/>
      </linearGradient>
    </defs>
    <path fill="url(#python-a)" d="M126.916.072c-64.832 0-60.784 28.115-60.784 28.115l.072 29.128h61.868v8.745H41.631S.145 61.355.145 126.77c0 65.417 36.21 63.097 36.21 63.097h21.61v-30.356s-1.165-36.21 35.632-36.21h61.362s34.475.557 34.475-33.319V33.97S194.67.072 126.916.072zM92.802 19.66a11.12 11.12 0 0 1 11.13 11.13 11.12 11.12 0 0 1-11.13 11.13 11.12 11.12 0 0 1-11.13-11.13 11.12 11.12 0 0 1 11.13-11.13z"/>
    <path fill="url(#python-b)" d="M128.757 254.126c64.832 0 60.784-28.115 60.784-28.115l-.072-29.127H127.6v-8.745h86.441s41.486 4.705 41.486-60.712c0-65.416-36.21-63.096-36.21-63.096h-21.61v30.355s1.165 36.21-35.632 36.21h-61.362s-34.475-.557-34.475 33.32v56.013s-5.235 33.897 62.518 33.897zm34.114-19.586a11.12 11.12 0 0 1-11.13-11.13 11.12 11.12 0 0 1 11.13-11.131 11.12 11.12 0 0 1 11.13 11.13 11.12 11.12 0 0 1-11.13 11.13z"/>
  </svg>
);

const JavaScriptIcon = () => (
  <svg viewBox="0 0 256 256" className="w-8 h-8">
    <rect fill="#F7DF1E" width="256" height="256"/>
    <path d="M67.312 213.932l19.59-11.856c3.78 6.701 7.218 12.371 15.465 12.371 7.905 0 12.89-3.092 12.89-15.12v-81.798h24.057v82.138c0 24.917-14.606 36.259-35.916 36.259-19.245 0-30.416-9.967-36.087-21.996M152.381 211.354l19.588-11.341c5.157 8.421 11.859 14.607 23.715 14.607 9.969 0 16.325-4.984 16.325-11.858 0-8.248-6.53-11.17-17.528-15.98l-6.013-2.58c-17.357-7.387-28.87-16.667-28.87-36.257 0-18.044 13.747-31.792 35.228-31.792 15.294 0 26.292 5.328 34.196 19.247L210.29 147.43c-4.125-7.389-8.591-10.31-15.465-10.31-7.046 0-11.514 4.468-11.514 10.31 0 7.217 4.468 10.14 14.778 14.608l6.014 2.577c20.45 8.765 31.963 17.7 31.963 37.804 0 21.654-17.012 33.51-39.867 33.51-22.339 0-36.774-10.654-43.819-24.574"/>
  </svg>
);

const GoIcon = () => (
  <svg viewBox="0 0 256 348" className="w-8 h-8">
    <path fill="#00ADD8" d="M0 173.657c.04-23.689 9.016-45.063 23.898-60.876 14.882-15.813 35.224-25.587 58.075-25.587 22.851 0 43.193 9.774 58.075 25.587 14.882 15.813 23.858 37.187 23.898 60.876-.04 23.689-9.016 45.063-23.898 60.876-14.882 15.813-35.224 25.587-58.075 25.587-22.851 0-43.193-9.774-58.075-25.587C9.016 218.72.04 197.346 0 173.657zm174.054 0c.04-23.689 9.016-45.063 23.898-60.876 14.882-15.813 35.224-25.587 58.075-25.587v172.926c-22.851 0-43.193-9.774-58.075-25.587-14.882-15.813-23.858-37.187-23.898-60.876z"/>
  </svg>
);

const TerminalIcon = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8 text-primary" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="4 17 10 11 4 5"/>
    <line x1="12" y1="19" x2="20" y2="19"/>
  </svg>
);

const installMethods = [
  {
    id: "python",
    name: "Python",
    icon: PythonIcon,
    color: "from-blue-500/20 to-yellow-500/20",
    borderColor: "border-blue-500/30",
    methods: [
      { name: "pip", command: "pip install phoenix-ai", recommended: true },
      { name: "poetry", command: "poetry add phoenix-ai" },
      { name: "conda", command: "conda install -c conda-forge phoenix-ai" },
      { name: "pipenv", command: "pipenv install phoenix-ai" },
    ],
    verification: `python -c "import phoenix; print(phoenix.__version__)"`,
    docsLink: "/docs/sdk/python",
  },
  {
    id: "javascript",
    name: "JavaScript / TypeScript",
    icon: JavaScriptIcon,
    color: "from-yellow-500/20 to-orange-500/20",
    borderColor: "border-yellow-500/30",
    methods: [
      { name: "npm", command: "npm install @phoenix-ai/sdk", recommended: true },
      { name: "yarn", command: "yarn add @phoenix-ai/sdk" },
      { name: "pnpm", command: "pnpm add @phoenix-ai/sdk" },
      { name: "bun", command: "bun add @phoenix-ai/sdk" },
    ],
    verification: `npx phoenix --version`,
    docsLink: "/docs/sdk/javascript",
  },
  {
    id: "go",
    name: "Go",
    icon: GoIcon,
    color: "from-cyan-500/20 to-blue-500/20",
    borderColor: "border-cyan-500/30",
    methods: [
      { name: "go get", command: "go get github.com/phoenix-ai/phoenix-go", recommended: true },
    ],
    verification: `go list -m github.com/phoenix-ai/phoenix-go`,
    docsLink: "/docs/sdk/go",
  },
  {
    id: "cli",
    name: "CLI Tools",
    icon: TerminalIcon,
    color: "from-purple-500/20 to-pink-500/20",
    borderColor: "border-purple-500/30",
    methods: [
      { name: "curl", command: "curl -sSL https://get.phoenix.dev | bash", recommended: true },
      { name: "Homebrew", command: "brew install phoenix-ai/tap/phoenix" },
      { name: "npm", command: "npm install -g @phoenix-ai/cli" },
      { name: "Windows", command: "iwr https://get.phoenix.dev/install.ps1 -useb | iex" },
    ],
    verification: `phoenix --version`,
    docsLink: "/docs/cli",
  },
];

const requirements = [
  { sdk: "Python", requirements: ["Python 3.8+", "pip or conda"] },
  { sdk: "JavaScript", requirements: ["Node.js 16+", "npm, yarn, or pnpm"] },
  { sdk: "Go", requirements: ["Go 1.19+", "go modules enabled"] },
  { sdk: "CLI", requirements: ["macOS, Linux, or Windows", "Shell access"] },
];

export default function Install() {
  const [selectedMethod, setSelectedMethod] = useState<Record<string, number>>({
    python: 0,
    javascript: 0,
    go: 0,
    cli: 0,
  });

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(249,115,22,0.08),transparent_60%)]" />
        
        <div className="container mx-auto max-w-5xl relative z-10">
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
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-4">
              <Download className="w-4 h-4" />
              Installation Guide
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Install Phoenix
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl">
              Get started with Phoenix in your preferred language. All SDKs are 
              open-source and designed for production use.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Quick Install */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-6 rounded-2xl bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 mb-12"
          >
            <h3 className="text-xl font-bold text-foreground mb-2">Quick Install</h3>
            <p className="text-muted-foreground mb-4">
              Get the CLI installed in one command:
            </p>
            <div className="flex items-center gap-2 p-3 rounded-xl bg-black border border-border/50">
              <code className="flex-1 font-mono text-sm text-primary">
                curl -sSL https://get.phoenix.dev | bash
              </code>
              <CopyButton text="curl -sSL https://get.phoenix.dev | bash" />
            </div>
          </motion.div>

          {/* Installation Methods */}
          <div className="space-y-8">
            {installMethods.map((method, idx) => (
              <motion.div
                key={method.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className={`rounded-2xl bg-gradient-to-br ${method.color} border ${method.borderColor} overflow-hidden`}
              >
                <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <method.icon />
                      <h2 className="text-2xl font-bold text-foreground">{method.name}</h2>
                    </div>
                    <Link to={method.docsLink}>
                      <Button variant="outline" size="sm" className="border-border/50">
                        Full Docs
                      </Button>
                    </Link>
                  </div>

                  {/* Method Tabs */}
                  <div className="flex gap-2 mb-4 flex-wrap">
                    {method.methods.map((m, i) => (
                      <button
                        key={m.name}
                        onClick={() => setSelectedMethod({ ...selectedMethod, [method.id]: i })}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                          selectedMethod[method.id] === i
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted/30 text-muted-foreground hover:bg-muted/50"
                        }`}
                      >
                        {m.name}
                        {m.recommended && (
                          <span className="ml-1.5 text-xs opacity-70">✓</span>
                        )}
                      </button>
                    ))}
                  </div>

                  {/* Install Command */}
                  <div className="mb-4">
                    <div className="flex items-center gap-2 p-3 rounded-xl bg-black border border-border/50">
                      <Terminal className="w-4 h-4 text-muted-foreground" />
                      <code className="flex-1 font-mono text-sm text-primary">
                        {method.methods[selectedMethod[method.id]].command}
                      </code>
                      <CopyButton text={method.methods[selectedMethod[method.id]].command} />
                    </div>
                  </div>

                  {/* Verification */}
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Verify installation:</p>
                    <div className="flex items-center gap-2 p-3 rounded-xl bg-black/50 border border-border/30">
                      <code className="flex-1 font-mono text-sm text-green-400">
                        {method.verification}
                      </code>
                      <CopyButton text={method.verification} />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Requirements */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-2xl font-bold text-foreground mb-6"
          >
            System Requirements
          </motion.h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {requirements.map((req, i) => (
              <motion.div
                key={req.sdk}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="p-4 rounded-xl bg-muted/20 border border-border"
              >
                <h3 className="font-semibold text-foreground mb-3">{req.sdk}</h3>
                <ul className="space-y-2">
                  {req.requirements.map((r) => (
                    <li key={r} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                      {r}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

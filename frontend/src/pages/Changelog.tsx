import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Zap, Bug, Sparkles, Shield, ArrowUp } from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const releases = [
  {
    version: "2.4.0",
    date: "December 28, 2024",
    tag: "Latest",
    changes: [
      { type: "feature", text: "Added Tree-of-Thoughts planning for complex decision making" },
      { type: "feature", text: "New vector store integration with Pinecone and Weaviate" },
      { type: "improvement", text: "50% faster correction cycle through optimized reflection" },
      { type: "fix", text: "Fixed memory leak in long-running multi-agent workflows" },
    ],
  },
  {
    version: "2.3.2",
    date: "December 15, 2024",
    changes: [
      { type: "fix", text: "Resolved race condition in concurrent agent deployments" },
      { type: "fix", text: "Fixed incorrect confidence scoring in edge cases" },
      { type: "security", text: "Patched vulnerability in WebSocket authentication" },
    ],
  },
  {
    version: "2.3.0",
    date: "December 1, 2024",
    changes: [
      { type: "feature", text: "Introduced hybrid correction strategies (rule-based + ML)" },
      { type: "feature", text: "Real-time streaming for correction events" },
      { type: "improvement", text: "Reduced API latency by 30%" },
      { type: "improvement", text: "Enhanced dashboard with live metrics" },
    ],
  },
  {
    version: "2.2.0",
    date: "November 15, 2024",
    changes: [
      { type: "feature", text: "Multi-agent orchestration with consensus protocols" },
      { type: "feature", text: "Added support for custom LLM providers" },
      { type: "improvement", text: "Improved memory retrieval accuracy" },
      { type: "fix", text: "Fixed timezone handling in scheduled corrections" },
    ],
  },
  {
    version: "2.1.0",
    date: "October 28, 2024",
    changes: [
      { type: "feature", text: "Self-Refine implementation for iterative improvement" },
      { type: "feature", text: "Go SDK released" },
      { type: "improvement", text: "Better error messages and debugging tools" },
    ],
  },
];

const typeIcons = {
  feature: Sparkles,
  improvement: ArrowUp,
  fix: Bug,
  security: Shield,
};

const typeColors = {
  feature: "text-primary bg-primary/10",
  improvement: "text-blue-400 bg-blue-400/10",
  fix: "text-amber-400 bg-amber-400/10",
  security: "text-red-400 bg-red-400/10",
};

export default function Changelog() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Link
              to="/"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-foreground">Changelog</h1>
            </div>

            <p className="text-lg text-muted-foreground">
              All notable changes to Phoenix Runtime. We release updates frequently.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Releases */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="space-y-12">
            {releases.map((release, i) => (
              <motion.div
                key={release.version}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="relative pl-8 border-l-2 border-border"
              >
                {/* Version dot */}
                <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-primary border-4 border-background" />

                {/* Header */}
                <div className="flex items-center gap-4 mb-4">
                  <h2 className="text-2xl font-bold text-foreground">v{release.version}</h2>
                  {release.tag && (
                    <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary text-xs font-medium">
                      {release.tag}
                    </span>
                  )}
                  <span className="text-sm text-muted-foreground">{release.date}</span>
                </div>

                {/* Changes */}
                <div className="space-y-3">
                  {release.changes.map((change, j) => {
                    const Icon = typeIcons[change.type as keyof typeof typeIcons];
                    const colorClass = typeColors[change.type as keyof typeof typeColors];
                    
                    return (
                      <div key={j} className="flex items-start gap-3">
                        <div className={`w-6 h-6 rounded-md flex items-center justify-center shrink-0 ${colorClass}`}>
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-muted-foreground">{change.text}</span>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

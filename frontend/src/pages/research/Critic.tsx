import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { ArrowLeft, ArrowRight, ExternalLink, Shield, Search, Code, FileCheck, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Critic() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-amber-500/5 via-transparent to-transparent" />
        <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 lg:px-8 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Link 
              to="/research" 
              className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Research
            </Link>
            
            <div className="flex items-center gap-4 mb-6">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-500/60">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                  CRITIC
                </h1>
                <p className="text-xl text-muted-foreground mt-2">
                  Self-Correction with Tool-Interactive Critiquing
                </p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Gou et al., 2023</span>
              <span>|</span>
              <span>arXiv:2305.11738</span>
              <span>|</span>
              <a 
                href="https://arxiv.org/abs/2305.11738" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-primary hover:underline"
              >
                View on arXiv
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Abstract */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="max-w-4xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="p-8 rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm"
            >
              <h2 className="text-2xl font-bold mb-4">Abstract</h2>
              <p className="text-muted-foreground leading-relaxed">
                CRITIC enables large language models to self-correct their outputs by interacting with 
                external tools such as search engines, code interpreters, and calculators. Unlike pure 
                self-refinement approaches, CRITIC grounds the correction process in external verification, 
                allowing the model to check facts, validate code execution, and verify mathematical 
                computations before producing final outputs.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Tool Integration */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold mb-8"
          >
            External Tool Integration
          </motion.h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                title: "Search Engine",
                icon: Search,
                description: "Fact-checks claims and statements by querying external knowledge sources like web search or knowledge bases.",
                examples: ["Wikipedia verification", "Real-time data lookup", "Citation checking"],
                color: "from-blue-500 to-blue-600"
              },
              {
                title: "Code Interpreter",
                icon: Code,
                description: "Executes generated code to verify correctness, catching runtime errors and logical bugs before deployment.",
                examples: ["Unit test execution", "Syntax validation", "Output verification"],
                color: "from-green-500 to-green-600"
              },
              {
                title: "Calculator/Verifier",
                icon: FileCheck,
                description: "Validates mathematical computations and logical reasoning through external computation tools.",
                examples: ["Math verification", "Logic checking", "Constraint validation"],
                color: "from-amber-500 to-amber-600"
              }
            ].map((item, index) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="p-6 rounded-xl border border-border/50 bg-card/50"
              >
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${item.color} mb-4`}>
                  <item.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground mb-4">{item.description}</p>
                <div className="space-y-1">
                  {item.examples.map((ex, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <div className="w-1 h-1 rounded-full bg-primary" />
                      {ex}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CRITIC Pipeline */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="text-3xl font-bold mb-8 text-center">The CRITIC Pipeline</h2>
            
            <div className="p-8 rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm">
              {/* Pipeline steps */}
              <div className="space-y-6">
                {[
                  {
                    step: 1,
                    title: "Initial Generation",
                    description: "LLM produces an initial response to the given query or task",
                    color: "bg-blue-500"
                  },
                  {
                    step: 2,
                    title: "Tool Interaction",
                    description: "System identifies claims/code to verify and queries appropriate external tools",
                    color: "bg-amber-500"
                  },
                  {
                    step: 3,
                    title: "Evidence Collection",
                    description: "External tools return verification results, execution outputs, or search results",
                    color: "bg-green-500"
                  },
                  {
                    step: 4,
                    title: "Critique Generation",
                    description: "LLM analyzes discrepancies between its output and external evidence",
                    color: "bg-purple-500"
                  },
                  {
                    step: 5,
                    title: "Corrected Output",
                    description: "LLM produces revised response incorporating verified information",
                    color: "bg-primary"
                  }
                ].map((item, index) => (
                  <motion.div
                    key={item.step}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-4"
                  >
                    <div className={`w-10 h-10 rounded-full ${item.color} flex items-center justify-center text-white font-bold flex-shrink-0`}>
                      {item.step}
                    </div>
                    <div className="pt-1">
                      <h4 className="font-semibold text-foreground">{item.title}</h4>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Key Findings */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold mb-8"
          >
            Key Improvements
          </motion.h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                title: "Fact-Checking",
                description: "Significant reduction in factual errors by grounding claims in external knowledge sources",
                improvement: "Reduced hallucinations"
              },
              {
                title: "Program Synthesis",
                description: "Higher success rates in code generation through execution-based verification",
                improvement: "Fewer runtime errors"
              },
              {
                title: "Toxicity Reduction",
                description: "Decreased harmful content generation through content policy verification",
                improvement: "Safer outputs"
              }
            ].map((item, index) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="p-6 rounded-xl border border-border/50 bg-card/50"
              >
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground mb-4">{item.description}</p>
                <div className="inline-flex px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 text-sm">
                  {item.improvement}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison with Self-Refine */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl"
          >
            <h2 className="text-3xl font-bold mb-8">CRITIC vs Self-Refine</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border/50">
                    <th className="text-left py-4 px-4 text-foreground font-semibold">Aspect</th>
                    <th className="text-left py-4 px-4 text-foreground font-semibold">Self-Refine</th>
                    <th className="text-left py-4 px-4 text-foreground font-semibold">CRITIC</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { aspect: "Verification Source", selfRefine: "Self-generated feedback", critic: "External tools" },
                    { aspect: "Grounding", selfRefine: "Model's internal knowledge", critic: "Real-world data" },
                    { aspect: "Best For", selfRefine: "Style, clarity, coherence", critic: "Facts, code, math" },
                    { aspect: "Latency", selfRefine: "Lower (no external calls)", critic: "Higher (tool calls)" }
                  ].map((row, i) => (
                    <tr key={i} className="border-b border-border/30">
                      <td className="py-4 px-4 text-foreground font-medium">{row.aspect}</td>
                      <td className="py-4 px-4 text-muted-foreground">{row.selfRefine}</td>
                      <td className="py-4 px-4 text-muted-foreground">{row.critic}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Phoenix Implementation */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl"
          >
            <h2 className="text-3xl font-bold mb-6">How Phoenix Uses CRITIC</h2>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              Phoenix combines CRITIC's tool-based verification with Self-Refine's iterative improvement 
              for comprehensive self-healing:
            </p>
            
            <div className="space-y-4">
              {[
                "Hybrid Validation: Uses both self-feedback (fast) and tool verification (accurate) based on task requirements",
                "Tool Registry: Configurable set of verification tools including code runners, API validators, and fact-checkers",
                "Confidence Routing: Automatically routes to external tools when model confidence is below threshold",
                "Cached Verification: Stores verification results to avoid redundant external calls"
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <CheckCircle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">{item}</span>
                </motion.div>
              ))}
            </div>
            
            {/* Code Example */}
            <div className="mt-8 rounded-xl overflow-hidden border border-border/50">
              <div className="bg-muted/50 px-4 py-2 border-b border-border/50">
                <span className="text-sm text-muted-foreground">Phoenix CRITIC Tool Configuration</span>
              </div>
              <pre className="p-4 bg-black/50 overflow-x-auto">
                <code className="text-sm text-muted-foreground">
{`from phoenix import Agent, CriticTools, CodeExecutor, WebSearch

agent = Agent(
    name="verified-agent",
    critic_tools=CriticTools([
        CodeExecutor(
            runtime="python",
            timeout=30,
            sandbox=True
        ),
        WebSearch(
            provider="serp",
            verify_sources=True
        ),
        Calculator(precision=10)
    ]),
    verification_threshold=0.7,  # Use tools when confidence < 70%
    cache_verifications=True
)

# Agent automatically verifies outputs before returning
result = await agent.execute(
    task="Calculate compound interest and verify formula"
)`}
                </code>
              </pre>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Navigation */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="flex flex-col sm:flex-row gap-4 justify-between">
            <Button variant="outline" size="lg" asChild>
              <Link to="/research/reflexion">
                <ArrowLeft className="mr-2 w-4 h-4" />
                Previous: Reflexion
              </Link>
            </Button>
            <Button size="lg" asChild>
              <Link to="/research">
                View All Research
                <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

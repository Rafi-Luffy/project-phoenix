import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { ArrowLeft, ArrowRight, ExternalLink, Zap, RefreshCw, MessageSquare, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SelfRefine() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
        <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        
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
              <div className="p-4 rounded-2xl bg-gradient-to-br from-primary to-primary/60">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                  Self-Refine
                </h1>
                <p className="text-xl text-muted-foreground mt-2">
                  Iterative Refinement with Self-Feedback
                </p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Madaan et al., 2023</span>
              <span>|</span>
              <span>arXiv:2303.17651</span>
              <span>|</span>
              <a 
                href="https://arxiv.org/abs/2303.17651" 
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
                Self-Refine introduces a framework for improving large language model outputs through 
                iterative feedback and refinement. Unlike traditional approaches that require additional 
                training, reinforcement learning, or supervised data, Self-Refine uses a single LLM to 
                generate an initial output, provide multi-aspect feedback on its own output, and then 
                refine the output based on that feedback. This process continues iteratively until the 
                output meets quality criteria or a maximum number of iterations is reached.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Key Methodology */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold mb-8"
          >
            Core Methodology
          </motion.h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                step: "1",
                title: "Generate",
                icon: Zap,
                description: "The LLM produces an initial draft or output based on the given task or prompt.",
                detail: "This is the baseline generation that will be iteratively improved."
              },
              {
                step: "2",
                title: "Feedback",
                icon: MessageSquare,
                description: "The same LLM provides multi-aspect, actionable feedback on its own output.",
                detail: "Feedback is specific and actionable, e.g., 'The sentiment is neutral; use more vivid adjectives.'"
              },
              {
                step: "3",
                title: "Refine",
                icon: RefreshCw,
                description: "The LLM rewrites the output incorporating the feedback to produce an improved version.",
                detail: "The refined output is then evaluated again, creating an iterative improvement loop."
              }
            ].map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative p-6 rounded-xl border border-border/50 bg-card/50"
              >
                <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
                  {item.step}
                </div>
                <div className="mb-4">
                  <item.icon className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground mb-3">{item.description}</p>
                <p className="text-sm text-muted-foreground/80 italic">{item.detail}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Visual Diagram */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="text-3xl font-bold mb-8 text-center">The Self-Refine Loop</h2>
            
            <div className="relative p-8 rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm">
              {/* Flow diagram */}
              <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8">
                <div className="flex flex-col items-center text-center">
                  <div className="w-24 h-24 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center mb-3">
                    <span className="text-3xl font-bold text-primary">M</span>
                  </div>
                  <span className="text-sm font-medium">Input</span>
                </div>
                
                <ArrowRight className="w-6 h-6 text-muted-foreground rotate-90 md:rotate-0" />
                
                <div className="flex flex-col items-center text-center">
                  <div className="w-24 h-24 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center mb-3">
                    <Zap className="w-10 h-10 text-white" />
                  </div>
                  <span className="text-sm font-medium">Generate y0</span>
                </div>
                
                <ArrowRight className="w-6 h-6 text-muted-foreground rotate-90 md:rotate-0" />
                
                <div className="flex flex-col items-center text-center">
                  <div className="w-24 h-24 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center mb-3">
                    <MessageSquare className="w-10 h-10 text-cyan-400" />
                  </div>
                  <span className="text-sm font-medium">Feedback fb</span>
                </div>
                
                <ArrowRight className="w-6 h-6 text-muted-foreground rotate-90 md:rotate-0" />
                
                <div className="flex flex-col items-center text-center">
                  <div className="w-24 h-24 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center mb-3">
                    <RefreshCw className="w-10 h-10 text-purple-400" />
                  </div>
                  <span className="text-sm font-medium">Refine yt</span>
                </div>
              </div>
              
              {/* Iteration arrow */}
              <div className="mt-6 flex justify-center">
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50 text-sm text-muted-foreground">
                  <RefreshCw className="w-4 h-4" />
                  Iterate until stopping condition
                </div>
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
            Key Findings
          </motion.h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                metric: "~20%",
                description: "Improvement in human preference over direct generation across tasks"
              },
              {
                metric: "7",
                description: "Diverse tasks validated: code optimization, math reasoning, review rewriting, and more"
              },
              {
                metric: "GPT-4",
                description: "Effective even with the most powerful models, showing universal applicability"
              },
              {
                metric: "0",
                description: "Additional training required - works with off-the-shelf LLMs"
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start gap-4 p-6 rounded-xl border border-border/50 bg-card/50"
              >
                <div className="text-3xl font-bold text-primary">{item.metric}</div>
                <p className="text-muted-foreground pt-1">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Phoenix Implementation */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl"
          >
            <h2 className="text-3xl font-bold mb-6">How Phoenix Uses Self-Refine</h2>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              Phoenix integrates Self-Refine principles into its core self-healing pipeline. When an 
              agent encounters an error or suboptimal output, the framework automatically triggers 
              the refinement loop:
            </p>
            
            <div className="space-y-4">
              {[
                "Detection: Phoenix monitors agent outputs for errors, anomalies, or quality issues",
                "Self-Feedback: The agent generates actionable feedback about what went wrong and how to fix it",
                "Refinement: The agent produces a corrected output based on the feedback",
                "Validation: External tools verify the refined output before deployment"
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">{item}</span>
                </motion.div>
              ))}
            </div>
            
            {/* Code Example */}
            <div className="mt-8 rounded-xl overflow-hidden border border-border/50">
              <div className="bg-muted/50 px-4 py-2 border-b border-border/50">
                <span className="text-sm text-muted-foreground">Phoenix Self-Refine Implementation</span>
              </div>
              <pre className="p-4 bg-black/50 overflow-x-auto">
                <code className="text-sm text-muted-foreground">
{`from phoenix import Agent, SelfRefineLoop

agent = Agent(
    name="code-reviewer",
    model="gpt-4",
    self_refine=SelfRefineLoop(
        max_iterations=3,
        feedback_aspects=["correctness", "efficiency", "readability"],
        stop_condition=lambda fb: fb.score >= 0.9
    )
)

# Agent automatically refines outputs until quality threshold
result = await agent.execute(task="Review and optimize this function")`}
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
              <Link to="/research">
                <ArrowLeft className="mr-2 w-4 h-4" />
                All Research Papers
              </Link>
            </Button>
            <Button size="lg" asChild>
              <Link to="/research/tree-of-thoughts">
                Next: Tree of Thoughts
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

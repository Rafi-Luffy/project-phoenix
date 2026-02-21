import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { ArrowRight, BookOpen, ExternalLink, GitBranch, Brain, Zap, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

const papers = [
  {
    id: "self-refine",
    title: "Self-Refine",
    subtitle: "Iterative Refinement with Self-Feedback",
    description: "A framework for improving LLM outputs through iterative feedback and refinement using a single LLM without additional training or reinforcement learning.",
    authors: "Madaan et al., 2023",
    arxiv: "arXiv:2303.17651",
    icon: Zap,
    color: "from-primary to-primary/60",
    keyFindings: [
      "20% improvement in human preference over direct generation",
      "Effective across 7 diverse tasks",
      "Works with powerful models like GPT-4"
    ]
  },
  {
    id: "tree-of-thoughts",
    title: "Tree of Thoughts",
    subtitle: "Deliberate Problem Solving with Large Language Models",
    description: "Generalizes Chain-of-Thought by allowing LMs to explore multiple reasoning paths simultaneously, enabling strategic lookahead and backtracking.",
    authors: "Yao et al., 2023",
    arxiv: "arXiv:2305.10601",
    icon: GitBranch,
    color: "from-cyan-500 to-cyan-500/60",
    keyFindings: [
      "74% success rate vs 4% with standard CoT",
      "Enables backtracking and lookahead",
      "Supports BFS and DFS search strategies"
    ]
  },
  {
    id: "reflexion",
    title: "Reflexion",
    subtitle: "Language Agents with Verbal Reinforcement Learning",
    description: "A framework that reinforces language agents through verbal reinforcement learning, updating a linguistic memory rather than model weights.",
    authors: "Shinn et al., 2023",
    arxiv: "arXiv:2303.11366",
    icon: Brain,
    color: "from-purple-500 to-purple-500/60",
    keyFindings: [
      "91% pass@1 on HumanEval benchmark",
      "Surpasses GPT-4's 80% baseline",
      "Persistent episodic memory for learning"
    ]
  },
  {
    id: "critic",
    title: "CRITIC",
    subtitle: "Self-Correction with Tool-Interactive Critiquing",
    description: "Enables LLMs to self-correct by interacting with external tools like search engines and code interpreters to validate their own outputs.",
    authors: "Gou et al., 2023",
    arxiv: "arXiv:2305.11738",
    icon: Shield,
    color: "from-amber-500 to-amber-500/60",
    keyFindings: [
      "Significant gains in fact-checking",
      "Improved program synthesis",
      "Reduced toxicity through external validation"
    ]
  }
];

export default function Research() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 lg:px-8 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6">
              <BookOpen className="w-4 h-4" />
              Research Foundation
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="text-foreground">Built on </span>
              <span className="bg-gradient-to-r from-primary via-cyan-400 to-primary bg-clip-text text-transparent">
                Cutting-Edge Research
              </span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Phoenix is grounded in peer-reviewed research from leading AI labs. 
              Explore the foundational papers that power our autonomous agent framework.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Papers Grid */}
      <section className="py-20">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="grid md:grid-cols-2 gap-8">
            {papers.map((paper, index) => (
              <motion.div
                key={paper.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Link to={`/research/${paper.id}`}>
                  <div className="group relative h-full p-8 rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
                    {/* Gradient accent */}
                    <div className={`absolute top-0 left-0 right-0 h-1 rounded-t-2xl bg-gradient-to-r ${paper.color} opacity-0 group-hover:opacity-100 transition-opacity`} />
                    
                    <div className="flex items-start gap-4 mb-6">
                      <div className={`p-3 rounded-xl bg-gradient-to-br ${paper.color} bg-opacity-10`}>
                        <paper.icon className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold text-foreground group-hover:text-primary transition-colors">
                          {paper.title}
                        </h3>
                        <p className="text-sm text-muted-foreground mt-1">{paper.subtitle}</p>
                      </div>
                    </div>
                    
                    <p className="text-muted-foreground mb-6 leading-relaxed">
                      {paper.description}
                    </p>
                    
                    <div className="space-y-2 mb-6">
                      {paper.keyFindings.map((finding, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                          <span className="text-muted-foreground">{finding}</span>
                        </div>
                      ))}
                    </div>
                    
                    <div className="flex items-center justify-between pt-4 border-t border-border/50">
                      <div className="text-sm text-muted-foreground">
                        <span className="font-medium text-foreground">{paper.authors}</span>
                        <span className="mx-2">|</span>
                        <span>{paper.arxiv}</span>
                      </div>
                      <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How Phoenix Uses Research */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How Phoenix Integrates These Concepts
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Phoenix synthesizes insights from multiple research directions to create 
              a unified framework for autonomous agent operation.
            </p>
          </motion.div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Self-Healing Pipeline",
                description: "Combines Self-Refine's iterative improvement with CRITIC's tool-based validation for autonomous error correction.",
                papers: ["Self-Refine", "CRITIC"]
              },
              {
                title: "Reasoning Engine",
                description: "Uses Tree of Thoughts for complex problem decomposition with multiple solution path exploration.",
                papers: ["Tree of Thoughts"]
              },
              {
                title: "Memory System",
                description: "Implements Reflexion's episodic memory for persistent learning across agent sessions.",
                papers: ["Reflexion"]
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
                <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                <p className="text-muted-foreground mb-4">{item.description}</p>
                <div className="flex flex-wrap gap-2">
                  {item.papers.map(paper => (
                    <span key={paper} className="px-3 py-1 text-xs rounded-full bg-primary/10 text-primary">
                      {paper}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center max-w-3xl mx-auto"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Build with Phoenix?
            </h2>
            <p className="text-muted-foreground mb-8">
              Experience the power of research-backed autonomous agents in your applications.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <Link to="/get-started">
                  Get Started
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link to="/docs">
                  <BookOpen className="mr-2 w-4 h-4" />
                  Read Documentation
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

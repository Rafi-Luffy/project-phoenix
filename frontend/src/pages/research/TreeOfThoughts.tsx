import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { ArrowLeft, ArrowRight, ExternalLink, GitBranch, Search, Undo2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TreeOfThoughts() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 via-transparent to-transparent" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        
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
              <div className="p-4 rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-500/60">
                <GitBranch className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                  Tree of Thoughts
                </h1>
                <p className="text-xl text-muted-foreground mt-2">
                  Deliberate Problem Solving with Large Language Models
                </p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Yao et al., 2023</span>
              <span>|</span>
              <span>arXiv:2305.10601</span>
              <span>|</span>
              <a 
                href="https://arxiv.org/abs/2305.10601" 
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
                Tree of Thoughts (ToT) generalizes the Chain-of-Thought prompting approach by allowing 
                language models to explore multiple reasoning paths simultaneously. This framework enables 
                deliberate decision-making through strategic lookahead and backtracking, treating problem-solving 
                as a search over a tree of possible thoughts. ToT dramatically improves performance on tasks 
                requiring planning, search, and complex reasoning.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Core Concepts */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold mb-8"
          >
            Core Concepts
          </motion.h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                title: "Thought Decomposition",
                icon: GitBranch,
                description: "Problems are broken down into intermediate 'thoughts' - coherent units of reasoning that serve as steps toward the solution.",
                color: "from-cyan-500 to-cyan-600"
              },
              {
                title: "Strategic Search",
                icon: Search,
                description: "Uses search algorithms like BFS (Breadth-First Search) or DFS (Depth-First Search) to navigate the tree of possible solutions.",
                color: "from-blue-500 to-blue-600"
              },
              {
                title: "Thought Evaluation",
                icon: CheckCircle,
                description: "Each node in the tree is evaluated for its promise, helping decide whether to continue, backtrack, or prune the path.",
                color: "from-green-500 to-green-600"
              },
              {
                title: "Backtracking",
                icon: Undo2,
                description: "Unlike linear Chain-of-Thought, ToT can backtrack from unpromising paths and explore alternative solutions.",
                color: "from-purple-500 to-purple-600"
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
                <p className="text-muted-foreground">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Visual Tree Diagram */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="text-3xl font-bold mb-8 text-center">Tree of Thoughts Structure</h2>
            
            <div className="p-8 rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm">
              {/* Tree visualization */}
              <div className="flex flex-col items-center">
                {/* Root */}
                <div className="w-20 h-20 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                  Input
                </div>
                
                {/* Connectors to level 1 */}
                <div className="flex items-center justify-center gap-32 my-4">
                  <div className="w-px h-8 bg-border" />
                  <div className="w-px h-8 bg-border" />
                  <div className="w-px h-8 bg-border" />
                </div>
                
                {/* Level 1 thoughts */}
                <div className="flex gap-8 md:gap-16">
                  <div className="flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-medium text-sm">
                      T1.1
                    </div>
                    <div className="flex gap-4 mt-4">
                      <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400/70 text-xs">
                        T2.1
                      </div>
                      <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400/70 text-xs">
                        T2.2
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center text-green-400 font-medium text-sm">
                      T1.2
                    </div>
                    <div className="flex gap-4 mt-4">
                      <div className="w-12 h-12 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center text-green-400 text-xs font-medium">
                        T2.3
                      </div>
                      <div className="w-12 h-12 rounded-full bg-green-500/10 border border-green-500/30 flex items-center justify-center text-green-400/70 text-xs">
                        T2.4
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-red-500/20 border border-red-500/40 flex items-center justify-center text-red-400 font-medium text-sm line-through opacity-50">
                      T1.3
                    </div>
                    <span className="text-xs text-muted-foreground mt-2">Pruned</span>
                  </div>
                </div>
                
                {/* Legend */}
                <div className="mt-8 flex flex-wrap gap-4 justify-center">
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-muted-foreground">Best path</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full bg-cyan-500/50" />
                    <span className="text-muted-foreground">Explored</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full bg-red-500/50" />
                    <span className="text-muted-foreground">Pruned</span>
                  </div>
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
            Benchmark Results
          </motion.h2>
          
          <div className="max-w-4xl">
            <div className="p-8 rounded-2xl border border-border/50 bg-card/50">
              <h3 className="text-xl font-semibold mb-6">Game of 24 Task</h3>
              
              {/* Comparison bars */}
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-muted-foreground">Standard GPT-4 (Chain of Thought)</span>
                    <span className="font-bold text-foreground">4%</span>
                  </div>
                  <div className="h-4 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: "4%" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1 }}
                      className="h-full bg-muted-foreground/50 rounded-full"
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-foreground font-medium">Tree of Thoughts (ToT)</span>
                    <span className="font-bold text-cyan-400">74%</span>
                  </div>
                  <div className="h-4 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: "74%" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: 0.3 }}
                      className="h-full bg-gradient-to-r from-cyan-500 to-cyan-400 rounded-full"
                    />
                  </div>
                </div>
              </div>
              
              <p className="text-muted-foreground mt-6 text-sm">
                The Game of 24 requires using 4 numbers and basic arithmetic operations to reach 24. 
                ToT's ability to explore and backtrack dramatically outperforms linear reasoning.
              </p>
            </div>
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
            <h2 className="text-3xl font-bold mb-6">How Phoenix Uses Tree of Thoughts</h2>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              Phoenix leverages Tree of Thoughts in its reasoning engine for complex problem-solving 
              and decision-making scenarios:
            </p>
            
            <div className="space-y-4">
              {[
                "Multi-Path Exploration: When facing complex tasks, agents explore multiple solution strategies in parallel",
                "Evaluation Heuristics: Each thought path is scored for feasibility, efficiency, and likelihood of success",
                "Dynamic Pruning: Unpromising paths are identified early and pruned to focus resources on viable solutions",
                "Adaptive Depth: Search depth adjusts based on problem complexity and available compute budget"
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <CheckCircle className="w-5 h-5 text-cyan-400 mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">{item}</span>
                </motion.div>
              ))}
            </div>
            
            {/* Code Example */}
            <div className="mt-8 rounded-xl overflow-hidden border border-border/50">
              <div className="bg-muted/50 px-4 py-2 border-b border-border/50">
                <span className="text-sm text-muted-foreground">Phoenix ToT Configuration</span>
              </div>
              <pre className="p-4 bg-black/50 overflow-x-auto">
                <code className="text-sm text-muted-foreground">
{`from phoenix import Agent, TreeOfThoughts

agent = Agent(
    name="problem-solver",
    reasoning_engine=TreeOfThoughts(
        search_algorithm="bfs",  # or "dfs"
        branching_factor=3,
        max_depth=5,
        evaluation_fn="self_consistency",
        prune_threshold=0.3
    )
)

# Agent explores multiple solution paths
result = await agent.solve(
    problem="Complex multi-step task",
    return_path=True  # Returns the successful thought path
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
              <Link to="/research/self-refine">
                <ArrowLeft className="mr-2 w-4 h-4" />
                Previous: Self-Refine
              </Link>
            </Button>
            <Button size="lg" asChild>
              <Link to="/research/reflexion">
                Next: Reflexion
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

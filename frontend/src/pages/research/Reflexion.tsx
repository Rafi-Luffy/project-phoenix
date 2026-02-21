import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { ArrowLeft, ArrowRight, ExternalLink, Brain, User, BarChart3, Database, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Reflexion() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-purple-500/5 via-transparent to-transparent" />
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        
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
              <div className="p-4 rounded-2xl bg-gradient-to-br from-purple-500 to-purple-500/60">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                  Reflexion
                </h1>
                <p className="text-xl text-muted-foreground mt-2">
                  Language Agents with Verbal Reinforcement Learning
                </p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Shinn et al., 2023</span>
              <span>|</span>
              <span>arXiv:2303.11366</span>
              <span>|</span>
              <a 
                href="https://arxiv.org/abs/2303.11366" 
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
                Reflexion introduces a novel framework that reinforces language agents not through 
                traditional weight updates, but through "verbal reinforcement learning" - the agent 
                reflects on task feedback, stores these reflections in an episodic memory buffer, 
                and uses this accumulated experience to improve performance on future attempts. This 
                approach enables rapid learning without gradient descent or fine-tuning.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Architecture Components */}
      <section className="py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold mb-8"
          >
            Architecture Components
          </motion.h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                title: "Actor",
                icon: User,
                description: "The agent component that performs the actual task, generating actions based on the current state and memory.",
                color: "from-blue-500 to-blue-600"
              },
              {
                title: "Evaluator",
                icon: BarChart3,
                description: "Provides feedback signals on the actor's performance - can be scalar rewards or free-form text critiques.",
                color: "from-green-500 to-green-600"
              },
              {
                title: "Self-Reflection + Memory",
                icon: Database,
                description: "The agent reflects on errors and stores 'lessons learned' in a persistent text buffer to guide future trials.",
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

      {/* Reflexion Loop Diagram */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="text-3xl font-bold mb-8 text-center">The Reflexion Learning Loop</h2>
            
            <div className="p-8 rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm">
              <div className="grid md:grid-cols-2 gap-8">
                {/* Left: Flow */}
                <div className="space-y-4">
                  {[
                    { step: 1, label: "Actor attempts task", color: "bg-blue-500" },
                    { step: 2, label: "Evaluator provides feedback", color: "bg-green-500" },
                    { step: 3, label: "Agent generates self-reflection", color: "bg-purple-500" },
                    { step: 4, label: "Reflection stored in memory", color: "bg-amber-500" },
                    { step: 5, label: "Next attempt uses memory", color: "bg-primary" }
                  ].map((item, index) => (
                    <motion.div
                      key={item.step}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center gap-4"
                    >
                      <div className={`w-8 h-8 rounded-full ${item.color} flex items-center justify-center text-white font-bold text-sm`}>
                        {item.step}
                      </div>
                      <span className="text-foreground">{item.label}</span>
                    </motion.div>
                  ))}
                </div>
                
                {/* Right: Memory visualization */}
                <div className="p-4 rounded-xl bg-black/30 border border-border/30">
                  <div className="text-sm text-muted-foreground mb-3 flex items-center gap-2">
                    <Database className="w-4 h-4" />
                    Episodic Memory Buffer
                  </div>
                  <div className="space-y-2">
                    {[
                      "Trial 1: Failed because I didn't handle edge case for empty input",
                      "Trial 2: Timeout error - need to optimize loop complexity",
                      "Trial 3: Success after adding input validation and using hashmap"
                    ].map((reflection, i) => (
                      <div key={i} className="p-2 rounded bg-muted/30 text-xs text-muted-foreground">
                        {reflection}
                      </div>
                    ))}
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
              <h3 className="text-xl font-semibold mb-6">HumanEval Coding Benchmark (pass@1)</h3>
              
              {/* Comparison bars */}
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-muted-foreground">GPT-4 Baseline</span>
                    <span className="font-bold text-foreground">80%</span>
                  </div>
                  <div className="h-4 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: "80%" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1 }}
                      className="h-full bg-muted-foreground/50 rounded-full"
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-foreground font-medium">Reflexion + GPT-4</span>
                    <span className="font-bold text-purple-400">91%</span>
                  </div>
                  <div className="h-4 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: "91%" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: 0.3 }}
                      className="h-full bg-gradient-to-r from-purple-500 to-purple-400 rounded-full"
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-8 grid grid-cols-3 gap-4">
                {[
                  { metric: "+11%", label: "Improvement over baseline" },
                  { metric: "91%", label: "State-of-the-art pass@1" },
                  { metric: "0", label: "Weight updates required" }
                ].map((item, i) => (
                  <div key={i} className="text-center p-4 rounded-lg bg-muted/30">
                    <div className="text-2xl font-bold text-purple-400">{item.metric}</div>
                    <div className="text-xs text-muted-foreground mt-1">{item.label}</div>
                  </div>
                ))}
              </div>
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
            <h2 className="text-3xl font-bold mb-6">How Phoenix Uses Reflexion</h2>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              Phoenix implements Reflexion as its core memory and learning system, enabling agents 
              to accumulate knowledge across sessions:
            </p>
            
            <div className="space-y-4">
              {[
                "Persistent Memory: Agent reflections are stored in a vector database for efficient retrieval across sessions",
                "Contextual Recall: When facing similar tasks, agents retrieve relevant past experiences and learnings",
                "Continuous Improvement: Each interaction adds to the agent's knowledge base without retraining",
                "Cross-Agent Learning: Insights can be shared across agent instances for collective improvement"
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <CheckCircle className="w-5 h-5 text-purple-400 mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">{item}</span>
                </motion.div>
              ))}
            </div>
            
            {/* Code Example */}
            <div className="mt-8 rounded-xl overflow-hidden border border-border/50">
              <div className="bg-muted/50 px-4 py-2 border-b border-border/50">
                <span className="text-sm text-muted-foreground">Phoenix Reflexion Memory System</span>
              </div>
              <pre className="p-4 bg-black/50 overflow-x-auto">
                <code className="text-sm text-muted-foreground">
{`from phoenix import Agent, ReflexionMemory

memory = ReflexionMemory(
    storage="vector_db",
    embedding_model="text-embedding-3-small",
    max_reflections=1000,
    retrieval_k=5
)

agent = Agent(
    name="learning-agent",
    memory=memory,
    reflection_prompt="What worked? What didn't? What should I do differently?"
)

# Agent learns from each interaction
result = await agent.execute(task)
await agent.reflect(result, feedback)  # Stores reflection in memory`}
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
              <Link to="/research/tree-of-thoughts">
                <ArrowLeft className="mr-2 w-4 h-4" />
                Previous: Tree of Thoughts
              </Link>
            </Button>
            <Button size="lg" asChild>
              <Link to="/research/critic">
                Next: CRITIC
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

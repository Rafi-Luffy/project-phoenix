import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Server, Shield, Activity, Settings } from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function ProductionDeployment() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-5xl">
          <Link to="/docs/getting-started" className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"><ArrowLeft className="w-4 h-4" />Back to Getting Started</Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-4"><Server className="w-4 h-4" />Production</div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Production Deployment</h1>
            <p className="text-lg text-muted-foreground max-w-2xl">Best practices for deploying Phoenix agents to production environments.</p>
          </motion.div>
        </div>
      </section>
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl space-y-8">
          {[{icon: Shield, title: "Security Configuration", items: ["Use environment variables for API keys", "Enable rate limiting", "Configure CORS policies", "Implement authentication"]},
            {icon: Activity, title: "Monitoring & Observability", items: ["Set up health check endpoints", "Configure metrics collection", "Enable distributed tracing", "Set up alerting rules"]},
            {icon: Settings, title: "Performance Optimization", items: ["Configure connection pooling", "Enable response caching", "Set appropriate timeouts", "Implement circuit breakers"]}
          ].map((section, i) => (
            <motion.div key={section.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }} className="p-6 rounded-xl bg-muted/20 border border-border">
              <div className="flex items-center gap-3 mb-4"><section.icon className="w-6 h-6 text-primary" /><h3 className="text-xl font-bold text-foreground">{section.title}</h3></div>
              <ul className="space-y-2">{section.items.map((item, j) => <li key={j} className="text-muted-foreground flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-primary" />{item}</li>)}</ul>
            </motion.div>
          ))}
        </div>
      </section>
      <Footer />
    </div>
  );
}

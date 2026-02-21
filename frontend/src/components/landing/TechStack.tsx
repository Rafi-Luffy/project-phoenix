import { motion } from "framer-motion";

const techCategories = [
  {
    category: "Frontend",
    items: ["React", "TypeScript", "Tailwind CSS", "Next.js"],
  },
  {
    category: "Backend",
    items: ["Python", "FastAPI", "Node.js", "gRPC"],
  },
  {
    category: "AI/ML",
    items: ["PyTorch", "Hugging Face", "LangChain", "Vector DB"],
  },
  {
    category: "Infrastructure",
    items: ["Docker", "Kubernetes", "AWS/GCP", "Prometheus"],
  },
];

export function TechStack() {
  return (
    <section className="py-20 lg:py-24 border-y border-border/50 bg-muted/20">
      <div className="container mx-auto px-4 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h3 className="text-2xl font-bold mb-2">Built for Engineers</h3>
          <p className="text-muted-foreground">
            Production-ready integrations with your existing stack
          </p>
        </motion.div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {techCategories.map((cat, catIndex) => (
            <motion.div
              key={cat.category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: catIndex * 0.1, duration: 0.5 }}
              className="text-center"
            >
              <div className="text-sm font-semibold text-accent mb-4">
                {cat.category}
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {cat.items.map((item) => (
                  <span
                    key={item}
                    className="px-3 py-1.5 text-xs font-medium bg-card border border-border/50 rounded-full text-muted-foreground hover:text-foreground hover:border-accent/30 transition-colors"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

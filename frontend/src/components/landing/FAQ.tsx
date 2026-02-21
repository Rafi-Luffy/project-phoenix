import { motion } from "framer-motion";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    question: "How is this different from standard observability platforms?",
    answer:
      "Traditional observability tools detect and alert - but humans still investigate and fix. Phoenix Runtime closes the loop: it detects, analyzes root causes, generates fixes, applies them, and validates recovery automatically. You get observability plus autonomous remediation in one system.",
  },
  {
    question: "Does it really run with zero human intervention?",
    answer:
      "Yes, for the core correction loop. The system detects issues, reflects using AI reasoning (Self-Refine, Tree-of-Thoughts), applies corrections, and validates outcomes without human input. Optional governance rules let you require approval for high-stakes changes, but most incidents resolve autonomously.",
  },
  {
    question: "How does it avoid unsafe corrections?",
    answer:
      "Multiple safety layers: confidence thresholds block low-certainty fixes, a Critic agent validates every proposed patch, changes are tested in isolated sandboxes before production deployment, and automatic rollback triggers if validation fails. You can also define governance policies for specific correction types.",
  },
  {
    question: "What models and environments does it support?",
    answer:
      "Phoenix Runtime is model-agnostic - use OpenAI, Anthropic, open-source LLMs, or custom models. It supports containerized workloads on Kubernetes, serverless functions, and traditional VM deployments. The framework integrates with major cloud providers and on-premise infrastructure.",
  },
  {
    question: "How does the learning system work?",
    answer:
      "The system uses meta-learning and reinforcement learning to improve over time. Successful corrections are stored in long-term memory and influence future policy decisions. Few-shot learning enables rapid adaptation to new error types, while reward shaping optimizes for fast, reliable recovery.",
  },
  {
    question: "Can I integrate with my existing monitoring stack?",
    answer:
      "Absolutely. Phoenix Runtime ingests telemetry from Prometheus, Datadog, New Relic, CloudWatch, and custom sources. It exposes metrics and traces compatible with OpenTelemetry, so you can keep your existing dashboards and alerting while adding autonomous correction capabilities.",
  },
];

export function FAQ() {
  return (
    <section id="docs" className="py-20 lg:py-32 bg-secondary/50">
      <div className="container mx-auto px-4 lg:px-8 max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <span className="pill-accent mb-4 inline-block">FAQ</span>
          <h2 className="section-heading mb-4">
            Common <span className="gradient-text">Questions</span>
          </h2>
        </motion.div>

        {/* Accordion */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="card-glass px-6 border-none"
              >
                <AccordionTrigger className="text-left font-semibold hover:no-underline py-5 text-foreground hover:text-primary transition-colors">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground pb-5 leading-relaxed">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  );
}
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Check, Zap, Building2, Rocket, ArrowRight, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const plans = [
  {
    name: "Starter",
    description: "Perfect for individual developers and small projects",
    price: 0,
    priceLabel: "Free forever",
    cta: "Get Started",
    ctaVariant: "outline" as const,
    icon: Zap,
    popular: false,
    features: [
      "Up to 3 agents",
      "100 self-corrections/month",
      "Basic memory system",
      "Community support",
      "Standard monitoring",
      "7-day data retention",
    ],
  },
  {
    name: "Pro",
    description: "For growing teams building production-ready systems",
    price: 99,
    priceLabel: "/month",
    cta: "Start Free Trial",
    ctaVariant: "default" as const,
    icon: Rocket,
    popular: true,
    features: [
      "Unlimited agents",
      "50,000 self-corrections/month",
      "Advanced memory + vector store",
      "Priority email support",
      "Real-time monitoring",
      "30-day data retention",
      "Custom correction policies",
      "API access",
      "Team collaboration (5 seats)",
    ],
  },
  {
    name: "Enterprise",
    description: "For organizations with advanced security and scale needs",
    price: null,
    priceLabel: "Custom pricing",
    cta: "Contact Sales",
    ctaVariant: "outline" as const,
    icon: Building2,
    popular: false,
    features: [
      "Everything in Pro",
      "Unlimited self-corrections",
      "Dedicated infrastructure",
      "24/7 priority support",
      "Custom SLAs",
      "Unlimited data retention",
      "Advanced RBAC",
      "SSO/SAML integration",
      "On-premise deployment",
      "Custom integrations",
      "Dedicated success manager",
    ],
  },
];

const faqs = [
  {
    q: "What counts as a self-correction?",
    a: "A self-correction occurs whenever the Phoenix Runtime automatically detects and fixes an issue in your agent's behavior. This includes error recovery, output refinement, and strategy adjustments.",
  },
  {
    q: "Can I upgrade or downgrade at any time?",
    a: "Yes! You can upgrade, downgrade, or cancel your plan at any time. Changes take effect at the start of your next billing cycle.",
  },
  {
    q: "Is there a free trial for Pro?",
    a: "Absolutely. All Pro features are available free for 14 days. No credit card required to start.",
  },
  {
    q: "What happens if I exceed my limits?",
    a: "We'll notify you when you're approaching your limit. You can upgrade anytime, or we'll gracefully pause self-corrections until your next billing cycle.",
  },
];

export default function Pricing() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="pt-32 pb-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(249,115,22,0.15),transparent_60%)]" />
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="container mx-auto text-center relative z-10"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-6"
          >
            <Zap className="w-4 h-4" />
            Simple, transparent pricing
          </motion.div>

          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            Scale your agents,
            <br />
            <span className="text-primary">not your costs</span>
          </h1>

          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Start free, upgrade when you're ready. All plans include our core self-healing 
            technology with zero hidden fees.
          </p>
        </motion.div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-24 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
            {plans.map((plan, i) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.1, duration: 0.5 }}
                className={`relative rounded-3xl p-8 ${
                  plan.popular
                    ? "bg-gradient-to-b from-primary/20 via-primary/10 to-transparent border-2 border-primary/50"
                    : "bg-muted/20 border border-border"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1.5 rounded-full bg-primary text-primary-foreground text-sm font-medium shadow-lg shadow-primary/30">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                    plan.popular ? "bg-primary/20" : "bg-muted"
                  }`}>
                    <plan.icon className={`w-6 h-6 ${plan.popular ? "text-primary" : "text-muted-foreground"}`} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-foreground">{plan.name}</h3>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground mb-6 min-h-[40px]">
                  {plan.description}
                </p>

                <div className="mb-6">
                  {plan.price !== null ? (
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold text-foreground">${plan.price}</span>
                      <span className="text-muted-foreground">{plan.priceLabel}</span>
                    </div>
                  ) : (
                    <span className="text-2xl font-bold text-foreground">{plan.priceLabel}</span>
                  )}
                </div>

                <Link to={plan.name === "Enterprise" ? "/book-onboarding" : "/get-started"}>
                  <Button
                    className={`w-full h-12 text-base mb-8 ${
                      plan.popular ? "btn-primary" : "bg-muted hover:bg-muted/80 text-foreground"
                    }`}
                  >
                    {plan.cta}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>

                <ul className="space-y-3">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-3 text-sm">
                      <Check className={`w-5 h-5 shrink-0 mt-0.5 ${
                        plan.popular ? "text-primary" : "text-muted-foreground"
                      }`} />
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Frequently asked questions
            </h2>
            <p className="text-muted-foreground">
              Everything you need to know about Phoenix pricing
            </p>
          </motion.div>

          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-2xl bg-muted/20 border border-border"
              >
                <div className="flex items-start gap-3">
                  <HelpCircle className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <div>
                    <h3 className="font-semibold text-foreground mb-2">{faq.q}</h3>
                    <p className="text-sm text-muted-foreground">{faq.a}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="pb-24 px-4">
        <div className="container mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative max-w-4xl mx-auto rounded-3xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-primary/30 via-accent/20 to-primary/30" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.5)_100%)]" />
            
            <div className="relative z-10 p-12 text-center">
              <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
                Ready to build self-healing agents?
              </h2>
              <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">
                Join thousands of developers building the next generation of autonomous AI systems.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/get-started">
                  <Button className="btn-primary h-12 px-8 text-base">
                    Start Building Free
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
                <Link to="/book-onboarding">
                  <Button variant="outline" className="h-12 px-8 text-base border-border/50 bg-background/50 hover:bg-background/80">
                    Talk to Sales
                  </Button>
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

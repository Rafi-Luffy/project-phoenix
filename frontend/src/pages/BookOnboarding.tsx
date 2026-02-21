import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "react-router-dom";
import { Calendar, Clock, Users, ArrowRight, Check, Building2, Zap, Shield, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const benefits = [
  { icon: Calendar, title: "30-min deep dive", desc: "Personalized demo of Phoenix capabilities" },
  { icon: Users, title: "Meet the team", desc: "Direct access to our engineering experts" },
  { icon: Shield, title: "Custom architecture", desc: "Tailored solution for your use case" },
];

const companies = [
  "TechCorp", "InnovateLabs", "DataFlow", "CloudScale", "AIFirst", "NextGen"
];

export default function BookOnboarding() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    role: "",
    teamSize: "",
    message: "",
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <section className="pt-32 pb-24 px-4">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 max-w-6xl mx-auto">
            {/* Left - Info */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-6">
                <Building2 className="w-4 h-4" />
                Enterprise Solutions
              </div>

              <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6 leading-tight">
                Book your personalized
                <span className="text-primary"> Phoenix demo</span>
              </h1>

              <p className="text-lg text-muted-foreground mb-10">
                See how Phoenix Runtime can transform your AI infrastructure with autonomous 
                self-healing agents. Our team will create a custom demo tailored to your needs.
              </p>

              <div className="space-y-6 mb-12">
                {benefits.map((benefit, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 + i * 0.1 }}
                    className="flex items-start gap-4"
                  >
                    <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
                      <benefit.icon className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground">{benefit.title}</h3>
                      <p className="text-sm text-muted-foreground">{benefit.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="p-6 rounded-2xl glass border border-border/50">
                <p className="text-sm text-muted-foreground mb-4">
                  Trusted by engineering teams at
                </p>
                <div className="flex flex-wrap gap-4">
                  {companies.map((company, i) => (
                    <span
                      key={i}
                      className="px-4 py-2 rounded-lg bg-muted/50 text-sm font-medium text-muted-foreground"
                    >
                      {company}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Right - Form */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent rounded-3xl blur-3xl" />
              
              <div className="relative p-8 rounded-3xl glass border border-border/50">
                <h2 className="text-2xl font-bold text-foreground mb-2">
                  Schedule your demo
                </h2>
                <p className="text-muted-foreground mb-8">
                  Fill out the form and we'll be in touch within 24 hours
                </p>

                <AnimatePresence mode="wait">
                  {isSubmitted ? (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      className="flex flex-col items-center justify-center py-12 text-center"
                    >
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", delay: 0.2 }}
                        className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mb-6"
                      >
                        <CheckCircle2 className="w-10 h-10 text-green-500" />
                      </motion.div>
                      <h3 className="text-2xl font-bold text-foreground mb-2">
                        Successfully submitted your info
                      </h3>
                      <p className="text-muted-foreground mb-6">
                        Our team will contact you within 24 hours to schedule your personalized demo.
                      </p>
                      <Link to="/">
                        <Button variant="outline">Back to Home</Button>
                      </Link>
                    </motion.div>
                  ) : (
                    <motion.form 
                      initial={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="space-y-5"
                      onSubmit={handleSubmit}
                    >
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-foreground">Full name</Label>
                          <Input
                            placeholder="John Doe"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="h-12 bg-muted/30 border-border focus:border-primary"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-foreground">Work email</Label>
                          <Input
                            type="email"
                            placeholder="john@company.com"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            className="h-12 bg-muted/30 border-border focus:border-primary"
                            required
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-foreground">Company</Label>
                          <Input
                            placeholder="Acme Inc."
                            value={formData.company}
                            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                            className="h-12 bg-muted/30 border-border focus:border-primary"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-foreground">Your role</Label>
                          <Input
                            placeholder="CTO"
                            value={formData.role}
                            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                            className="h-12 bg-muted/30 border-border focus:border-primary"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label className="text-foreground">Team size</Label>
                        <div className="grid grid-cols-4 gap-2">
                          {["1-10", "11-50", "51-200", "200+"].map((size) => (
                            <button
                              key={size}
                              type="button"
                              onClick={() => setFormData({ ...formData, teamSize: size })}
                              className={`p-3 rounded-xl text-sm font-medium transition-colors ${
                                formData.teamSize === size
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-muted/30 text-muted-foreground hover:bg-muted/50"
                              }`}
                            >
                              {size}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label className="text-foreground">What would you like to discuss?</Label>
                        <Textarea
                          placeholder="Tell us about your use case and what you're looking to achieve..."
                          value={formData.message}
                          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                          className="min-h-[120px] bg-muted/30 border-border focus:border-primary resize-none"
                        />
                      </div>

                      <Button type="submit" className="btn-primary w-full h-12 text-base">
                        Request Demo
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>

                      <p className="text-xs text-center text-muted-foreground">
                        By submitting, you agree to our{" "}
                        <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link>
                      </p>
                    </motion.form>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

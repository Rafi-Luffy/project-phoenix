import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, ArrowRight, CheckCircle2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function RequestIntegration() {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", integration: "", useCase: "" });

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-32 pb-24 px-4">
        <div className="container mx-auto max-w-2xl">
          <Link to="/docs/integrations" className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"><ArrowLeft className="w-4 h-4" />Back to Integrations</Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-4xl font-bold text-foreground mb-4">Request an Integration</h1>
            <p className="text-muted-foreground mb-8">Tell us which integration you need and we'll prioritize it on our roadmap.</p>
          </motion.div>
          {submitted ? (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-12">
              <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4"><CheckCircle2 className="w-8 h-8 text-green-500" /></div>
              <h2 className="text-2xl font-bold text-foreground mb-2">Request Submitted</h2>
              <p className="text-muted-foreground">We'll review your request and get back to you soon.</p>
            </motion.div>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }} className="space-y-6 p-6 rounded-2xl bg-muted/20 border border-border">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} required className="bg-muted/30" /></div>
                <div className="space-y-2"><Label>Email</Label><Input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required className="bg-muted/30" /></div>
              </div>
              <div className="space-y-2"><Label>Integration Name</Label><Input placeholder="e.g., Slack, MongoDB, Redis..." value={form.integration} onChange={(e) => setForm({...form, integration: e.target.value})} required className="bg-muted/30" /></div>
              <div className="space-y-2"><Label>Use Case</Label><Textarea placeholder="Describe how you would use this integration..." value={form.useCase} onChange={(e) => setForm({...form, useCase: e.target.value})} className="bg-muted/30 min-h-[100px]" /></div>
              <Button type="submit" className="btn-primary w-full"><Send className="w-4 h-4 mr-2" />Submit Request</Button>
            </form>
          )}
        </div>
      </section>
      <Footer />
    </div>
  );
}

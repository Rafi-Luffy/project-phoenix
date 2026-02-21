import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, 
  Mail, 
  MessageSquare, 
  Phone, 
  Clock, 
  Send,
  CheckCircle2,
  Headphones,
  FileText,
  ExternalLink,
  Zap
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const supportOptions = [
  {
    icon: MessageSquare,
    title: "Live Chat",
    description: "Chat with our support team in real-time",
    action: "Start Chat",
    available: true,
    responseTime: "< 5 min",
  },
  {
    icon: Mail,
    title: "Email Support",
    description: "Send us an email and we'll respond promptly",
    action: "support@phoenix.dev",
    available: true,
    responseTime: "< 4 hours",
  },
  {
    icon: Phone,
    title: "Priority Phone",
    description: "Direct phone support for Enterprise plans",
    action: "Schedule Call",
    available: false,
    responseTime: "Immediate",
  },
];

const helpResources = [
  { icon: FileText, title: "Documentation", desc: "Comprehensive guides and tutorials", href: "/docs" },
  { icon: MessageSquare, title: "Community Discord", desc: "Get help from the community", href: "#" },
  { icon: Zap, title: "API Status", desc: "Check system status and uptime", href: "#" },
];

export default function ContactSupport() {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    category: "",
    subject: "",
    message: "",
    priority: "normal"
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(249,115,22,0.08),transparent_60%)]" />
        
        <div className="container mx-auto max-w-5xl relative z-10">
          <Link 
            to="/docs"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Documentation
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-4">
              <Headphones className="w-4 h-4" />
              Support
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Contact Support
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl">
              Our support team is here to help. Choose the best way to reach us 
              or submit a support request below.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Support Options */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <div className="grid md:grid-cols-3 gap-4 mb-12">
            {supportOptions.map((option, i) => (
              <motion.div
                key={option.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`p-6 rounded-2xl border ${
                  option.available 
                    ? "bg-muted/20 border-border hover:border-primary/50" 
                    : "bg-muted/10 border-border/50 opacity-75"
                } transition-all`}
              >
                <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                  <option.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-1">{option.title}</h3>
                <p className="text-sm text-muted-foreground mb-4">{option.description}</p>
                <div className="flex items-center justify-between">
                  {option.available ? (
                    <Button variant="outline" size="sm" className="border-primary/30 text-primary hover:bg-primary/10">
                      {option.action}
                    </Button>
                  ) : (
                    <span className="text-xs text-muted-foreground">Enterprise Only</span>
                  )}
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {option.responseTime}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <div className="grid lg:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="lg:col-span-2"
            >
              <div className="p-6 rounded-2xl bg-muted/20 border border-border">
                <h2 className="text-xl font-bold text-foreground mb-6">Submit a Request</h2>
                
                {submitted ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-12"
                  >
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", duration: 0.5 }}
                      className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4"
                    >
                      <CheckCircle2 className="w-8 h-8 text-green-500" />
                    </motion.div>
                    <h3 className="text-2xl font-bold text-foreground mb-2">Request Submitted</h3>
                    <p className="text-muted-foreground mb-6">
                      We've received your message and will respond within 24 hours.
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Ticket ID: <span className="font-mono text-primary">PHX-{Date.now().toString().slice(-6)}</span>
                    </p>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Name</Label>
                        <Input 
                          value={form.name}
                          onChange={(e) => setForm({...form, name: e.target.value})}
                          required
                          className="bg-muted/30"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Email</Label>
                        <Input 
                          type="email"
                          value={form.email}
                          onChange={(e) => setForm({...form, email: e.target.value})}
                          required
                          className="bg-muted/30"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Category</Label>
                        <Select value={form.category} onValueChange={(v) => setForm({...form, category: v})}>
                          <SelectTrigger className="bg-muted/30">
                            <SelectValue placeholder="Select category" />
                          </SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            <SelectItem value="technical">Technical Issue</SelectItem>
                            <SelectItem value="billing">Billing & Account</SelectItem>
                            <SelectItem value="feature">Feature Request</SelectItem>
                            <SelectItem value="integration">Integration Help</SelectItem>
                            <SelectItem value="other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Priority</Label>
                        <Select value={form.priority} onValueChange={(v) => setForm({...form, priority: v})}>
                          <SelectTrigger className="bg-muted/30">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            <SelectItem value="low">Low</SelectItem>
                            <SelectItem value="normal">Normal</SelectItem>
                            <SelectItem value="high">High</SelectItem>
                            <SelectItem value="urgent">Urgent</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Subject</Label>
                      <Input 
                        value={form.subject}
                        onChange={(e) => setForm({...form, subject: e.target.value})}
                        placeholder="Brief description of your issue"
                        required
                        className="bg-muted/30"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Message</Label>
                      <Textarea 
                        value={form.message}
                        onChange={(e) => setForm({...form, message: e.target.value})}
                        placeholder="Please describe your issue in detail..."
                        required
                        className="bg-muted/30 min-h-[150px]"
                      />
                    </div>

                    <Button type="submit" className="btn-primary w-full">
                      <Send className="w-4 h-4 mr-2" />
                      Submit Request
                    </Button>
                  </form>
                )}
              </div>
            </motion.div>

            {/* Help Resources */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="space-y-4"
            >
              <h3 className="font-semibold text-foreground mb-4">Quick Resources</h3>
              {helpResources.map((resource) => (
                <Link
                  key={resource.title}
                  to={resource.href}
                  className="flex items-center gap-3 p-4 rounded-xl bg-muted/20 border border-border hover:border-primary/50 transition-all group"
                >
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <resource.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-foreground group-hover:text-primary transition-colors">
                      {resource.title}
                    </p>
                    <p className="text-xs text-muted-foreground">{resource.desc}</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </Link>
              ))}

              <div className="p-4 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20 mt-6">
                <h4 className="font-semibold text-foreground mb-2">Enterprise Support</h4>
                <p className="text-sm text-muted-foreground mb-4">
                  Get dedicated support with guaranteed SLAs, priority escalation, and direct phone access.
                </p>
                <Button variant="outline" size="sm" className="w-full border-primary/30 text-primary hover:bg-primary/10">
                  Learn More
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

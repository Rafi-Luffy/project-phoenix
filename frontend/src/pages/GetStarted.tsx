import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Eye, EyeOff, ArrowRight, Github, Chrome, Check, Zap, Shield, Cpu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PhoenixLogo } from "@/components/landing/PhoenixLogo";

const features = [
  { icon: Zap, text: "Deploy in seconds" },
  { icon: Shield, text: "Zero human intervention" },
  { icon: Cpu, text: "Autonomous self-healing" },
];

export default function GetStarted() {
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Panel - Visual */}
      <div className="hidden lg:flex flex-1 items-center justify-center bg-gradient-to-br from-dark via-charcoal to-dark relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(249,115,22,0.15),transparent_70%)]" />
        
        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `linear-gradient(rgba(249,115,22,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(249,115,22,0.3) 1px, transparent 1px)`,
            backgroundSize: '50px 50px'
          }} />
        </div>

        <div className="relative z-10 px-12 max-w-lg">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
          >
            <PhoenixLogo size="xl" animated={true} />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-8 text-4xl font-bold text-foreground leading-tight"
          >
            Start building
            <span className="text-primary"> self-healing </span>
            agents today
          </motion.h2>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-8 space-y-4"
          >
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + i * 0.1 }}
                className="flex items-center gap-3"
              >
                <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
                  <feature.icon className="w-5 h-5 text-primary" />
                </div>
                <span className="text-foreground font-medium">{feature.text}</span>
              </motion.div>
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-12 p-6 rounded-2xl glass border border-border/50"
          >
            <div className="flex items-center gap-3">
              <img
                src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=faces"
                alt="User"
                className="w-12 h-12 rounded-full border-2 border-primary/50"
              />
              <div>
                <p className="text-foreground font-medium">Alex Chen</p>
                <p className="text-sm text-muted-foreground">CTO at TechCorp</p>
              </div>
            </div>
            <p className="mt-4 text-muted-foreground italic">
              "Phoenix reduced our incident response time by 80%. The self-healing agents are incredible."
            </p>
          </motion.div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center px-4 py-12 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md space-y-8"
        >
          {/* Logo */}
          <div className="flex flex-col items-center gap-4">
            <Link to="/" className="flex items-center gap-3 group lg:hidden">
              <PhoenixLogo size="lg" animated={true} />
            </Link>
            <div className="text-center">
              <h1 className="text-3xl font-bold text-foreground">Create your account</h1>
              <p className="mt-2 text-muted-foreground">
                Start your 14-day free trial. No credit card required.
              </p>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-border bg-muted/30 hover:bg-muted/50 transition-colors text-sm font-medium text-foreground"
            >
              <Github className="w-4 h-4" />
              GitHub
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-border bg-muted/30 hover:bg-muted/50 transition-colors text-sm font-medium text-foreground"
            >
              <Chrome className="w-4 h-4" />
              Google
            </motion.button>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Or continue with email
              </span>
            </div>
          </div>

          {/* Form */}
          <form className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-foreground">Full name</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="h-12 bg-muted/30 border-border focus:border-primary focus:ring-primary/20"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-foreground">Work email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 bg-muted/30 border-border focus:border-primary focus:ring-primary/20"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-foreground">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a strong password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="h-12 bg-muted/30 border-border focus:border-primary focus:ring-primary/20 pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-xs text-muted-foreground">
                Must be at least 8 characters with one number
              </p>
            </div>

            <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}>
              <Button className="btn-primary w-full h-12 text-base group">
                Create account
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </motion.div>

            <p className="text-xs text-center text-muted-foreground">
              By signing up, you agree to our{" "}
              <Link to="/terms" className="text-primary hover:underline">Terms of Service</Link>
              {" "}and{" "}
              <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link>
            </p>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link to="/signin" className="text-primary hover:text-primary/80 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "react-router-dom";
import { Menu, X, Command } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SectionLink } from "@/components/ui/section-link";
import { PhoenixLogo } from "./PhoenixLogo";
import { SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";

const navLinks = [
  { label: "How it Works", href: "/#self-correction" },
  { label: "Capabilities", href: "/#agents" },
  { label: "Architecture", href: "/" },
  { label: "Docs", href: "/docs" },
  { label: "Pricing", href: "/pricing" },
];

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <motion.nav 
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled 
          ? "glass border-b border-border/30 shadow-lg shadow-black/20" 
          : "bg-transparent"
      }`}
    >
      <div className="container mx-auto px-4 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <a href="/" className="flex items-center gap-3 group">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative"
            >
              <div className="absolute inset-0 rounded-xl bg-primary/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <PhoenixLogo size="md" animated={true} />
            </motion.div>
            <span className="font-bold text-xl tracking-tight text-foreground">
              Phoenix
            </span>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-1">
            {navLinks.map((link, index) => (
              <motion.div
                key={link.label}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + index * 0.05, duration: 0.4 }}
                className="relative"
              >
                {link.href.startsWith("/#") || link.href === "/" ? (
                  <SectionLink
                    href={link.href}
                    className="block px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors rounded-lg group relative"
                  >
                    {link.label}
                    <span className="absolute inset-x-2 -bottom-px h-px bg-gradient-to-r from-transparent via-primary to-transparent scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
                  </SectionLink>
                ) : (
                  <Link
                    to={link.href}
                    className="relative block px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors rounded-lg group"
                  >
                    {link.label}
                    <span className="absolute inset-x-2 -bottom-px h-px bg-gradient-to-r from-transparent via-primary to-transparent scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
                  </Link>
                )}
              </motion.div>
            ))}
          </div>

          {/* Desktop CTA */}
          <div className="hidden lg:flex items-center gap-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <SignedOut>
                <Link
                  to="/signin"
                  className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  Sign in
                </Link>
              </SignedOut>
              <SignedIn>
                <Link
                  to="/console"
                  className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  Console
                </Link>
              </SignedIn>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 }}
            >
              <SignedOut>
                <Link to="/get-started">
                  <Button className="btn-primary text-sm px-5 py-2.5 h-auto group relative overflow-hidden">
                    <span className="relative z-10 flex items-center gap-2">
                      Get Started
                      <span className="flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-black/20 text-xs font-mono">
                        <Command className="w-3 h-3" />K
                      </span>
                    </span>
                    <motion.div 
                      className="absolute inset-0 bg-gradient-to-r from-accent via-primary to-accent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ backgroundSize: "200% 100%" }}
                      animate={{ backgroundPosition: ["0% 0%", "100% 0%", "0% 0%"] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    />
                  </Button>
                </Link>
              </SignedOut>
              <SignedIn>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </motion.div>
          </div>

          {/* Mobile Menu Button */}
          <motion.button
            onClick={() => setIsOpen(!isOpen)}
            whileTap={{ scale: 0.95 }}
            className="lg:hidden p-2 rounded-lg hover:bg-muted transition-colors text-foreground"
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </motion.button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="lg:hidden border-t border-border/30 glass"
          >
            <div className="container mx-auto px-4 py-4 space-y-1">
              {navLinks.map((link, index) => (
                <motion.div
                  key={link.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  {link.href.startsWith("/#") || link.href === "/" ? (
                    <SectionLink
                      href={link.href}
                      onClick={() => setIsOpen(false)}
                      className="block px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-primary/5 rounded-lg transition-colors"
                    >
                      {link.label}
                    </SectionLink>
                  ) : (
                    <Link
                      to={link.href}
                      onClick={() => setIsOpen(false)}
                      className="block px-4 py-3 text-sm font-medium text-muted-foreground hover:text-primary hover:bg-primary/5 rounded-lg transition-colors"
                    >
                      {link.label}
                    </Link>
                  )}
                </motion.div>
              ))}
              <div className="pt-4 border-t border-border/30 space-y-2">
                <a
                  href="#signin"
                  className="block px-4 py-3 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  Sign in
                </a>
                <Button className="btn-primary w-full text-sm">
                  Get Started
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

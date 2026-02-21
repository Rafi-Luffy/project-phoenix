import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Github, Twitter, MessageCircle } from "lucide-react";
import { SectionLink } from "@/components/ui/section-link";
import { PhoenixLogo } from "./PhoenixLogo";

const footerLinks = {
  Product: [
    { label: "Runtime Loop", href: "/#self-correction" },
    { label: "Capabilities", href: "/#agents" },
    { label: "Pricing", href: "/pricing" },
    { label: "Changelog", href: "/changelog" },
  ],
  Docs: [
    { label: "Getting Started", href: "/docs/getting-started" },
    { label: "API Reference", href: "/docs/api" },
    { label: "SDK Documentation", href: "/docs/sdk" },
    { label: "Examples", href: "/docs/examples" },
  ],
  Research: [
    { label: "Self-Refine", href: "/research/self-refine" },
    { label: "Tree of Thoughts", href: "/research/tree-of-thoughts" },
    { label: "Reflexion", href: "/research/reflexion" },
    { label: "CRITIC", href: "/research/critic" },
  ],
  Community: [
    { label: "Discord", href: "https://discord.gg/phoenix" },
    { label: "GitHub", href: "https://github.com/phoenix-agent" },
    { label: "Twitter", href: "https://twitter.com/phoenix_agent" },
    { label: "Blog", href: "/blog" },
  ],
};

export function Footer() {
  return (
    <footer className="bg-black border-t border-border/50">
      <div className="container mx-auto px-4 lg:px-8 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 lg:gap-12">
          {/* Brand */}
          <div className="col-span-2 md:col-span-4 lg:col-span-1 mb-8 lg:mb-0">
            <a href="/" className="flex items-center gap-3 mb-4">
              <PhoenixLogo size="sm" animated={false} />
              <span className="font-bold text-xl text-foreground">Phoenix</span>
            </a>
            <p className="text-sm text-muted-foreground mb-6 max-w-xs leading-relaxed">
              Autonomous, self-healing agent framework for runtime self-correction 
              with zero human intervention.
            </p>
            <div className="flex gap-3">
              {[Github, Twitter, MessageCircle].map((Icon, i) => (
                <motion.a
                  key={i}
                  href="#"
                  whileHover={{ scale: 1.1, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-10 h-10 rounded-xl bg-muted/50 hover:bg-primary/20 flex items-center justify-center transition-colors text-muted-foreground hover:text-primary"
                >
                  <Icon className="w-4 h-4" />
                </motion.a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="font-semibold text-sm mb-4 text-foreground">{category}</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    {link.href.startsWith("http") ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-muted-foreground hover:text-primary transition-colors"
                      >
                        {link.label}
                      </a>
                    ) : link.href.startsWith("/#") ? (
                      <SectionLink
                        href={link.href}
                        className="text-sm text-muted-foreground hover:text-primary transition-colors"
                      >
                        {link.label}
                      </SectionLink>
                    ) : (
                      <Link
                        to={link.href}
                        className="text-sm text-muted-foreground hover:text-primary transition-colors"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="mt-16 pt-8 border-t border-border/50 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Phoenix. All rights reserved.
          </p>
          <div className="flex gap-6">
            <Link to="/privacy" className="text-sm text-muted-foreground hover:text-primary transition-colors">
              Privacy Policy
            </Link>
            <Link to="/terms" className="text-sm text-muted-foreground hover:text-primary transition-colors">
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight, Clock, User, Tag } from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const featuredPost = {
  title: "Introducing Phoenix 2.4: Tree-of-Thoughts Planning for Smarter Agents",
  excerpt: "Today we're announcing Phoenix 2.4, our biggest release yet. With Tree-of-Thoughts planning, your agents can now reason through complex problems systematically, exploring multiple solution paths before committing to an action.",
  image: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&h=400&fit=crop",
  author: "Sarah Chen",
  date: "December 28, 2024",
  readTime: "8 min read",
  category: "Product",
};

const posts = [
  {
    title: "Building Production-Ready Self-Healing Systems",
    excerpt: "Learn best practices for deploying autonomous agents that can handle real-world failures gracefully.",
    image: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=250&fit=crop",
    author: "Michael Park",
    date: "December 20, 2024",
    readTime: "12 min read",
    category: "Engineering",
  },
  {
    title: "The Science Behind Self-Refine: How Agents Learn from Mistakes",
    excerpt: "A deep dive into the research papers and techniques that power Phoenix's self-correction engine.",
    image: "https://images.unsplash.com/photo-1507146153580-69a1fe6d8aa1?w=400&h=250&fit=crop",
    author: "Dr. Emily Zhang",
    date: "December 15, 2024",
    readTime: "15 min read",
    category: "Research",
  },
  {
    title: "Case Study: How TechCorp Reduced Incidents by 80%",
    excerpt: "An in-depth look at how one of our enterprise customers transformed their operations with Phoenix.",
    image: "https://images.unsplash.com/photo-1551434678-e076c223a692?w=400&h=250&fit=crop",
    author: "Alex Rivera",
    date: "December 10, 2024",
    readTime: "6 min read",
    category: "Case Study",
  },
  {
    title: "Multi-Agent Orchestration: Patterns and Pitfalls",
    excerpt: "Explore common patterns for coordinating multiple agents and how to avoid typical mistakes.",
    image: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=250&fit=crop",
    author: "Jordan Lee",
    date: "December 5, 2024",
    readTime: "10 min read",
    category: "Tutorial",
  },
  {
    title: "Memory Systems: Short-Term vs Long-Term for AI Agents",
    excerpt: "Understanding when and how to use different memory strategies for optimal agent performance.",
    image: "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=250&fit=crop",
    author: "Sarah Chen",
    date: "November 28, 2024",
    readTime: "9 min read",
    category: "Engineering",
  },
  {
    title: "Announcing Our Series A: $25M to Build the Future of Autonomous AI",
    excerpt: "We're thrilled to share that Phoenix has raised $25M to accelerate our mission of making AI truly autonomous.",
    image: "https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=400&h=250&fit=crop",
    author: "Team Phoenix",
    date: "November 20, 2024",
    readTime: "4 min read",
    category: "Company",
  },
];

const categoryColors: Record<string, string> = {
  Product: "bg-primary/20 text-primary",
  Engineering: "bg-blue-500/20 text-blue-400",
  Research: "bg-purple-500/20 text-purple-400",
  "Case Study": "bg-emerald-500/20 text-emerald-400",
  Tutorial: "bg-amber-500/20 text-amber-400",
  Company: "bg-pink-500/20 text-pink-400",
};

export default function Blog() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Phoenix Blog
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Insights on autonomous AI, self-healing systems, and the future of agent frameworks.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Featured Post */}
      <section className="pb-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.article
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="group"
          >
            <Link to="/blog/phoenix-2-4" className="grid md:grid-cols-2 gap-8 items-center">
              <div className="relative overflow-hidden rounded-2xl aspect-video">
                <img
                  src={featuredPost.image}
                  alt={featuredPost.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
              </div>
              <div>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium mb-4 ${categoryColors[featuredPost.category]}`}>
                  {featuredPost.category}
                </span>
                <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4 group-hover:text-primary transition-colors">
                  {featuredPost.title}
                </h2>
                <p className="text-muted-foreground mb-6 line-clamp-3">
                  {featuredPost.excerpt}
                </p>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1.5">
                    <User className="w-4 h-4" />
                    {featuredPost.author}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-4 h-4" />
                    {featuredPost.readTime}
                  </span>
                </div>
              </div>
            </Link>
          </motion.article>
        </div>
      </section>

      {/* All Posts */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-2xl font-bold text-foreground mb-8">All Posts</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map((post, i) => (
              <motion.article
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="group"
              >
                <Link to="#" className="block">
                  <div className="relative overflow-hidden rounded-xl aspect-video mb-4">
                    <img
                      src={post.image}
                      alt={post.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  </div>
                  <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium mb-2 ${categoryColors[post.category]}`}>
                    {post.category}
                  </span>
                  <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors line-clamp-2">
                    {post.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {post.excerpt}
                  </p>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{post.author}</span>
                    <span>•</span>
                    <span>{post.readTime}</span>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

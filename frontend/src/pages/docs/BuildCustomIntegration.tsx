import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Code2, Puzzle, Zap, BookOpen } from "lucide-react";
import { useState } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return <button onClick={copy} className="p-2 rounded-lg hover:bg-muted/50 transition-colors text-muted-foreground hover:text-foreground">{copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}</button>;
}

const customToolExample = `from phoenix import Tool, Agent

class CustomAPITool(Tool):
    name = "custom_api"
    description = "Interact with your custom API"
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
    
    async def execute(self, action: str, params: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/{action}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=params
            )
            return response.json()

# Use in agent
agent = Agent(
    name="custom-agent",
    tools=[CustomAPITool(api_url="https://api.example.com", api_key="key")],
    self_healing=True
)`;

export default function BuildCustomIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-5xl">
          <Link to="/docs/integrations" className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"><ArrowLeft className="w-4 h-4" />Back to Integrations</Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-primary text-sm font-medium mb-4"><Puzzle className="w-4 h-4" />Custom</div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Build Custom Integration</h1>
            <p className="text-lg text-muted-foreground max-w-2xl">Create your own Phoenix integrations using our extensible plugin system.</p>
          </motion.div>
        </div>
      </section>
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl grid md:grid-cols-3 gap-4">
          {[{icon: Code2, title: "Tool API", desc: "Extend agents with custom tools"}, {icon: Zap, title: "Middleware", desc: "Add processing pipelines"}, {icon: BookOpen, title: "Documentation", desc: "Full API reference available"}].map((f, i) => (
            <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }} className="p-4 rounded-xl bg-muted/20 border border-border">
              <f.icon className="w-8 h-8 text-primary mb-3" /><h3 className="font-semibold text-foreground mb-1">{f.title}</h3><p className="text-sm text-muted-foreground">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-6">Custom Tool Example</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border"><span className="text-xs text-muted-foreground">custom_tool.py</span><CopyButton text={customToolExample} /></div>
            <pre className="p-4 overflow-x-auto text-sm"><code className="text-green-400/90 font-mono whitespace-pre">{customToolExample}</code></pre>
          </div>
        </div>
      </section>
      <Footer />
    </div>
  );
}

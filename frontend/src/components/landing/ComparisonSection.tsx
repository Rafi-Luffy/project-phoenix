import { motion } from "framer-motion";

export function ComparisonSection() {
  return (
    <section className="py-20 lg:py-32">
      <div className="container mx-auto px-4 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="section-heading mb-4">
            Manual Ops vs <span className="gradient-text">Phoenix</span>
          </h2>
          <p className="section-subheading mx-auto">
            No human is required in the core loop - only optional governance rules 
            for high-stakes decisions.
          </p>
        </motion.div>

        {/* Comparison */}
        <div className="grid lg:grid-cols-2 gap-6 lg:gap-8">
          {/* Manual */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="mb-3">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-destructive/20 text-destructive text-sm font-semibold border border-destructive/30">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
                Traditional Manual Ops
              </span>
            </div>
            <div className="card-dark p-1">
              <pre className="code-block overflow-x-auto text-xs leading-relaxed">
                <code>
                  <span className="code-comment"># Traditional Manual Ops</span>{"\n"}
                  <span className="code-comment"># Humans in the loop at every step</span>{"\n\n"}
                  <span className="code-keyword">alerts</span>:{"\n"}
                  {"  "}- <span className="code-keyword">name</span>: <span className="code-string">"API Error Rate &gt; 5%"</span>{"\n"}
                  {"    "}<span className="code-keyword">action</span>: <span className="code-string">"page oncall engineer"</span>{"\n\n"}
                  <span className="code-keyword">runbook</span>:{"\n"}
                  {"  "}<span className="code-number">1.</span> SSH into production server{"\n"}
                  {"  "}<span className="code-number">2.</span> Check logs manually{"\n"}
                  {"  "}<span className="code-number">3.</span> Identify root cause{"\n"}
                  {"  "}<span className="code-number">4.</span> Write hotfix patch{"\n"}
                  {"  "}<span className="code-number">5.</span> Test in staging{"\n"}
                  {"  "}<span className="code-number">6.</span> Deploy manually{"\n"}
                  {"  "}<span className="code-number">7.</span> Monitor for 30 min{"\n"}
                  {"  "}<span className="code-number">8.</span> Close incident ticket{"\n\n"}
                  <span className="code-comment"># Average MTTR: 45 minutes</span>{"\n"}
                  <span className="code-comment"># Weekend incidents: painful</span>
                </code>
              </pre>
            </div>
          </motion.div>

          {/* Phoenix */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="relative"
          >
            <div className="mb-3">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/20 text-primary text-sm font-semibold border border-primary/30">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
                Phoenix
              </span>
            </div>
            <div className="card-dark p-1 ring-2 ring-primary/20">
              <pre className="code-block overflow-x-auto text-xs leading-relaxed">
                <code>
                  <span className="code-comment"># Phoenix Autonomous Loop</span>{"\n"}
                  <span className="code-comment"># Zero human intervention</span>{"\n\n"}
                  <span className="code-keyword">async def</span> <span className="code-function">self_heal</span>(incident):{"\n"}
                  {"    "}<span className="code-comment"># 1. Observe</span>{"\n"}
                  {"    "}telemetry = agent.<span className="code-function">observe</span>(){"\n\n"}
                  {"    "}<span className="code-comment"># 2. Reflect</span>{"\n"}
                  {"    "}analysis = critic.<span className="code-function">analyze</span>(telemetry){"\n\n"}
                  {"    "}<span className="code-comment"># 3. Correct</span>{"\n"}
                  {"    "}strategy = policy.<span className="code-function">select_correction</span>(analysis){"\n"}
                  {"    "}patch = runtime.<span className="code-function">generate_patch</span>(strategy){"\n"}
                  {"    "}runtime.<span className="code-function">apply_patch</span>(patch){"\n\n"}
                  {"    "}<span className="code-comment"># 4. Reinforce</span>{"\n"}
                  {"    "}<span className="code-keyword">if</span> runtime.<span className="code-function">validate</span>():{"\n"}
                  {"        "}memory.<span className="code-function">store_experience</span>(incident, patch){"\n"}
                  {"        "}policy.<span className="code-function">update</span>(reward=<span className="code-number">1.0</span>){"\n\n"}
                  <span className="code-comment"># Average MTTR: 47 seconds</span>{"\n"}
                  <span className="code-comment"># Weekend incidents: handled automatically</span>
                </code>
              </pre>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

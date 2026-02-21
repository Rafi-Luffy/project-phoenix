import { motion } from "framer-motion";
import { PhoenixLogo } from "./PhoenixLogo";

const nodes = [
  { id: "planner", label: "Planner", x: 50, y: 15, delay: 0 },
  { id: "critic", label: "Critic", x: 85, y: 40, delay: 0.15 },
  { id: "executor", label: "Executor", x: 70, y: 75, delay: 0.3 },
  { id: "monitor", label: "Monitor", x: 30, y: 75, delay: 0.45 },
  { id: "memory", label: "Memory", x: 15, y: 40, delay: 0.6 },
];

const edges = [
  { from: "planner", to: "critic" },
  { from: "critic", to: "executor" },
  { from: "executor", to: "monitor" },
  { from: "monitor", to: "memory" },
  { from: "memory", to: "planner" },
];

const getNodePosition = (id: string) => {
  const node = nodes.find((n) => n.id === id);
  return node ? { x: node.x, y: node.y } : { x: 0, y: 0 };
};

export function NetworkGraph() {
  return (
    <div className="relative w-full h-full min-h-[450px] lg:min-h-[550px]">
      {/* Outer glow ring */}
      <motion.div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] lg:w-[420px] lg:h-[420px] rounded-full"
        style={{
          background: "radial-gradient(circle, transparent 40%, hsl(25 95% 53% / 0.08) 60%, transparent 70%)",
        }}
        animate={{
          scale: [1, 1.05, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
      />

      {/* Inner rotating ring */}
      <motion.div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[280px] h-[280px] lg:w-[340px] lg:h-[340px] rounded-full border border-dashed border-primary/20"
        animate={{
          rotate: [0, -360],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "linear",
        }}
      />

      {/* SVG for connections */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="edgeGradientNew" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(25 95% 53%)" stopOpacity="0.6" />
            <stop offset="50%" stopColor="hsl(35 100% 50%)" stopOpacity="0.8" />
            <stop offset="100%" stopColor="hsl(43 96% 56%)" stopOpacity="0.6" />
          </linearGradient>
          
          <filter id="edgeGlow">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Animated dash pattern */}
          <pattern id="movingDash" width="8" height="1" patternUnits="userSpaceOnUse">
            <rect width="4" height="1" fill="hsl(25 95% 53%)" />
          </pattern>
        </defs>

        {/* Edge connections with animated flow */}
        {edges.map((edge, index) => {
          const from = getNodePosition(edge.from);
          const to = getNodePosition(edge.to);
          const midX = (from.x + to.x) / 2;
          const midY = (from.y + to.y) / 2;
          const offset = 8;
          const controlX = midX + (index % 2 === 0 ? offset : -offset);
          const controlY = midY + (index % 2 === 0 ? -offset : offset);

          return (
            <g key={`${edge.from}-${edge.to}`}>
              {/* Base glow line */}
              <motion.path
                d={`M ${from.x} ${from.y} Q ${controlX} ${controlY} ${to.x} ${to.y}`}
                stroke="url(#edgeGradientNew)"
                strokeWidth="0.8"
                fill="none"
                filter="url(#edgeGlow)"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 1.5,
                  delay: 0.5 + index * 0.2,
                  ease: "easeOut",
                }}
              />
              
              {/* Animated particle along path */}
              <motion.circle
                r="1.5"
                fill="hsl(43 96% 60%)"
                filter="url(#edgeGlow)"
                initial={{ opacity: 0 }}
                animate={{
                  opacity: [0, 1, 1, 0],
                  offsetDistance: ["0%", "100%"],
                }}
                transition={{
                  duration: 2,
                  delay: 1 + index * 0.4,
                  repeat: Infinity,
                  repeatDelay: 3,
                  ease: "easeInOut",
                }}
                style={{
                  offsetPath: `path("M ${from.x} ${from.y} Q ${controlX} ${controlY} ${to.x} ${to.y}")`,
                }}
              />
            </g>
          );
        })}
      </svg>

      {/* Nodes */}
      {nodes.map((node) => (
        <motion.div
          key={node.id}
          className="absolute transform -translate-x-1/2 -translate-y-1/2"
          style={{
            left: `${node.x}%`,
            top: `${node.y}%`,
          }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{
            duration: 0.6,
            delay: 0.8 + node.delay,
            type: "spring",
            stiffness: 200,
            damping: 15,
          }}
        >
          <motion.div
            className="relative"
            animate={{ y: [0, -4, 0] }}
            transition={{
              duration: 4 + node.delay,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            {/* Glow backdrop */}
            <motion.div 
              className="absolute inset-0 rounded-xl blur-xl bg-primary/30"
              animate={{ opacity: [0.3, 0.5, 0.3] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            
            {/* Node card */}
            <motion.div 
              className="relative px-4 py-2.5 rounded-xl bg-card/90 backdrop-blur-sm border border-primary/30 shadow-lg"
              whileHover={{ 
                scale: 1.08, 
                borderColor: "hsl(25 95% 53% / 0.6)",
                boxShadow: "0 0 30px hsl(25 95% 53% / 0.3)",
              }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center gap-2">
                <motion.div 
                  className="w-2 h-2 rounded-full bg-primary"
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
                <span className="text-sm font-semibold text-foreground whitespace-nowrap">
                  {node.label}
                </span>
              </div>
            </motion.div>
          </motion.div>
        </motion.div>
      ))}

      {/* Center Phoenix logo */}
      <motion.div
        className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 1.8, duration: 0.6, type: "spring" }}
      >
        <motion.div
          className="relative"
          animate={{ 
            y: [0, -5, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          {/* Multi-layer glow */}
          <motion.div
            className="absolute inset-0 -m-8 rounded-full bg-primary/20 blur-3xl"
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 3, repeat: Infinity }}
          />
          <motion.div
            className="absolute inset-0 -m-4 rounded-full bg-accent/30 blur-xl"
            animate={{ scale: [1.1, 1, 1.1], opacity: [0.4, 0.6, 0.4] }}
            transition={{ duration: 2.5, repeat: Infinity }}
          />
          
          {/* Logo container */}
          <div className="relative w-20 h-20 rounded-2xl bg-card/80 backdrop-blur-sm border border-primary/40 flex items-center justify-center shadow-2xl">
            <PhoenixLogo size="lg" animated={true} />
          </div>
        </motion.div>
      </motion.div>

      {/* Floating particles */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1.5 h-1.5 rounded-full"
          style={{
            background: i % 2 === 0 ? "hsl(25 95% 53%)" : "hsl(43 96% 56%)",
            left: `${20 + Math.random() * 60}%`,
            top: `${20 + Math.random() * 60}%`,
          }}
          animate={{
            y: [0, -20 - Math.random() * 20, 0],
            x: [0, (Math.random() - 0.5) * 15, 0],
            opacity: [0, 0.8, 0],
            scale: [0, 1.2, 0],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.4,
            ease: "easeOut",
          }}
        />
      ))}
    </div>
  );
}

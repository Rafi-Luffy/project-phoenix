import { motion } from "framer-motion";

export function FloatingOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Large primary orb - top right */}
      <motion.div
        className="absolute -top-20 -right-20 w-[500px] h-[500px]"
        animate={{
          y: [0, 30, 0],
          x: [0, -15, 0],
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <div 
          className="w-full h-full rounded-full opacity-30"
          style={{
            background: "radial-gradient(circle at 30% 30%, hsl(25 95% 53% / 0.6) 0%, hsl(25 95% 53% / 0.1) 50%, transparent 70%)",
          }}
        />
        {/* Halftone pattern overlay */}
        <div 
          className="absolute inset-0 rounded-full opacity-40"
          style={{
            backgroundImage: `radial-gradient(circle, hsl(25 95% 53% / 0.3) 1px, transparent 1px)`,
            backgroundSize: "8px 8px",
            maskImage: "radial-gradient(circle at 30% 30%, black 0%, transparent 60%)",
            WebkitMaskImage: "radial-gradient(circle at 30% 30%, black 0%, transparent 60%)",
          }}
        />
      </motion.div>

      {/* Medium secondary orb - bottom left */}
      <motion.div
        className="absolute -bottom-32 -left-32 w-[400px] h-[400px]"
        animate={{
          y: [0, -25, 0],
          x: [0, 20, 0],
          scale: [1, 1.08, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1,
        }}
      >
        <div 
          className="w-full h-full rounded-full opacity-25"
          style={{
            background: "radial-gradient(circle at 70% 70%, hsl(35 100% 50% / 0.5) 0%, hsl(35 100% 50% / 0.1) 50%, transparent 70%)",
          }}
        />
        <div 
          className="absolute inset-0 rounded-full opacity-30"
          style={{
            backgroundImage: `radial-gradient(circle, hsl(35 100% 50% / 0.4) 1px, transparent 1px)`,
            backgroundSize: "6px 6px",
            maskImage: "radial-gradient(circle at 70% 70%, black 0%, transparent 60%)",
            WebkitMaskImage: "radial-gradient(circle at 70% 70%, black 0%, transparent 60%)",
          }}
        />
      </motion.div>

      {/* Small accent orb - middle */}
      <motion.div
        className="absolute top-1/3 left-1/4 w-[200px] h-[200px]"
        animate={{
          y: [0, 20, 0],
          x: [0, -10, 0],
          opacity: [0.2, 0.35, 0.2],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2,
        }}
      >
        <div 
          className="w-full h-full rounded-full"
          style={{
            background: "radial-gradient(circle, hsl(43 96% 56% / 0.3) 0%, transparent 60%)",
          }}
        />
      </motion.div>

      {/* Floating ember particles */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-primary"
          style={{
            left: `${15 + Math.random() * 70}%`,
            top: `${20 + Math.random() * 60}%`,
          }}
          animate={{
            y: [0, -30 - Math.random() * 30, 0],
            x: [0, (Math.random() - 0.5) * 20, 0],
            opacity: [0, 0.8, 0],
            scale: [0, 1, 0],
          }}
          transition={{
            duration: 4 + Math.random() * 4,
            repeat: Infinity,
            delay: i * 0.5,
            ease: "easeOut",
          }}
        />
      ))}

      {/* Grid lines overlay */}
      <div 
        className="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage: `
            linear-gradient(hsl(var(--primary)) 1px, transparent 1px),
            linear-gradient(90deg, hsl(var(--primary)) 1px, transparent 1px)
          `,
          backgroundSize: "80px 80px",
        }}
      />
    </div>
  );
}

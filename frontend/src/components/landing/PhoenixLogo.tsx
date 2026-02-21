import { motion } from "framer-motion";

interface PhoenixLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  animated?: boolean;
  className?: string;
}

export function PhoenixLogo({ size = "md", animated = true, className = "" }: PhoenixLogoProps) {
  const sizes = {
    sm: { width: 32, height: 32, viewBox: "0 0 48 48" },
    md: { width: 40, height: 40, viewBox: "0 0 48 48" },
    lg: { width: 64, height: 64, viewBox: "0 0 48 48" },
    xl: { width: 96, height: 96, viewBox: "0 0 48 48" },
  };

  const config = sizes[size];

  return (
    <motion.svg
      width={config.width}
      height={config.height}
      viewBox={config.viewBox}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      initial={animated ? { opacity: 0, scale: 0.8 } : false}
      animate={animated ? { opacity: 1, scale: 1 } : false}
      transition={{ duration: 0.5 }}
    >
      <defs>
        {/* Main gradient for the phoenix body */}
        <linearGradient id="phoenixGradient" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="hsl(15, 90%, 45%)" />
          <stop offset="30%" stopColor="hsl(25, 95%, 53%)" />
          <stop offset="60%" stopColor="hsl(35, 100%, 50%)" />
          <stop offset="100%" stopColor="hsl(43, 96%, 56%)" />
        </linearGradient>

        {/* Inner flame gradient */}
        <linearGradient id="innerFlame" x1="50%" y1="100%" x2="50%" y2="0%">
          <stop offset="0%" stopColor="hsl(35, 100%, 55%)" />
          <stop offset="100%" stopColor="hsl(50, 100%, 70%)" />
        </linearGradient>

        {/* Glow filter */}
        <filter id="phoenixGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Drop shadow */}
        <filter id="phoenixShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="hsl(25, 95%, 53%)" floodOpacity="0.4" />
        </filter>
      </defs>

      {/* Background glow circle */}
      <motion.circle
        cx="24"
        cy="24"
        r="20"
        fill="url(#phoenixGradient)"
        opacity="0.15"
        animate={animated ? {
          scale: [1, 1.1, 1],
          opacity: [0.15, 0.25, 0.15],
        } : undefined}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Main Phoenix Bird */}
      <g filter="url(#phoenixShadow)">
        {/* Left wing - sweeping back */}
        <motion.path
          d="M8 28C10 24 14 20 18 18C15 22 13 26 12 30C10 28 8 27 8 28Z"
          fill="url(#phoenixGradient)"
          animate={animated ? {
            d: [
              "M8 28C10 24 14 20 18 18C15 22 13 26 12 30C10 28 8 27 8 28Z",
              "M6 26C8 22 14 18 18 17C15 21 12 26 11 31C9 28 6 25 6 26Z",
              "M8 28C10 24 14 20 18 18C15 22 13 26 12 30C10 28 8 27 8 28Z",
            ],
          } : undefined}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Right wing - sweeping back */}
        <motion.path
          d="M40 28C38 24 34 20 30 18C33 22 35 26 36 30C38 28 40 27 40 28Z"
          fill="url(#phoenixGradient)"
          animate={animated ? {
            d: [
              "M40 28C38 24 34 20 30 18C33 22 35 26 36 30C38 28 40 27 40 28Z",
              "M42 26C40 22 34 18 30 17C33 21 36 26 37 31C39 28 42 25 42 26Z",
              "M40 28C38 24 34 20 30 18C33 22 35 26 36 30C38 28 40 27 40 28Z",
            ],
          } : undefined}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Body - central flame shape */}
        <motion.path
          d="M24 8C26 12 28 16 28 20C28 24 26 28 24 32C22 28 20 24 20 20C20 16 22 12 24 8Z"
          fill="url(#phoenixGradient)"
          filter="url(#phoenixGlow)"
          animate={animated ? {
            scale: [1, 1.02, 1],
          } : undefined}
          style={{ transformOrigin: "center" }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Inner flame core */}
        <motion.path
          d="M24 12C25.5 15 26.5 18 26.5 21C26.5 24 25 27 24 29C23 27 21.5 24 21.5 21C21.5 18 22.5 15 24 12Z"
          fill="url(#innerFlame)"
          animate={animated ? {
            opacity: [0.9, 1, 0.9],
          } : undefined}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Head crest - top flames */}
        <motion.path
          d="M24 6C24.5 8 25 10 25 11C25 12 24.5 13 24 14C23.5 13 23 12 23 11C23 10 23.5 8 24 6Z"
          fill="url(#innerFlame)"
          animate={animated ? {
            scaleY: [1, 1.15, 1],
            y: [0, -1, 0],
          } : undefined}
          style={{ transformOrigin: "center bottom" }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Tail feathers - flowing down */}
        <motion.path
          d="M24 32C25 34 26 36 26 38C26 40 25 42 24 44C23 42 22 40 22 38C22 36 23 34 24 32Z"
          fill="url(#phoenixGradient)"
          opacity="0.8"
          animate={animated ? {
            scaleY: [1, 1.1, 1],
          } : undefined}
          style={{ transformOrigin: "center top" }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Left tail accent */}
        <motion.path
          d="M22 33C20 35 18 38 17 40C18 39 20 37 22 35C21 36 20 38 19 39C21 38 22 36 22 33Z"
          fill="url(#phoenixGradient)"
          opacity="0.6"
        />

        {/* Right tail accent */}
        <motion.path
          d="M26 33C28 35 30 38 31 40C30 39 28 37 26 35C27 36 28 38 29 39C27 38 26 36 26 33Z"
          fill="url(#phoenixGradient)"
          opacity="0.6"
        />
      </g>

      {/* Sparkle effects */}
      <motion.circle
        cx="18"
        cy="14"
        r="1"
        fill="hsl(43, 96%, 70%)"
        animate={animated ? {
          opacity: [0, 1, 0],
          scale: [0.5, 1, 0.5],
        } : undefined}
        transition={{
          duration: 2,
          repeat: Infinity,
          delay: 0.5,
        }}
      />
      <motion.circle
        cx="30"
        cy="14"
        r="1"
        fill="hsl(43, 96%, 70%)"
        animate={animated ? {
          opacity: [0, 1, 0],
          scale: [0.5, 1, 0.5],
        } : undefined}
        transition={{
          duration: 2,
          repeat: Infinity,
          delay: 1,
        }}
      />
      <motion.circle
        cx="24"
        cy="4"
        r="0.8"
        fill="hsl(50, 100%, 75%)"
        animate={animated ? {
          opacity: [0, 1, 0],
          y: [0, -2, 0],
        } : undefined}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          delay: 0.2,
        }}
      />
    </motion.svg>
  );
}

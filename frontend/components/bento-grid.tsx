"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useEffect, useState } from "react"
import { Activity, Video, BarChart3, Zap, Brain, Eye } from "lucide-react"

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.22, 1, 0.36, 1],
    },
  },
}

function SystemStatus() {
  const [dots, setDots] = useState([true, true, true, false, true])

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => prev.map(() => Math.random() > 0.2))
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2">
      {dots.map((active, i) => (
        <motion.div
          key={i}
          className={`w-2 h-2 rounded-full ${active ? "bg-emerald-500" : "bg-zinc-700"}`}
          animate={active ? { scale: [1, 1.2, 1] } : {}}
          transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, delay: i * 0.2 }}
        />
      ))}
    </div>
  )
}

function KeyboardCommand() {
  const [pressed, setPressed] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setPressed(true)
      setTimeout(() => setPressed(false), 200)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-1">
      <motion.kbd
        animate={pressed ? { scale: 0.95, y: 2 } : { scale: 1, y: 0 }}
        className="px-2 py-1 text-xs bg-zinc-800 border border-zinc-700 rounded text-zinc-300 font-mono"
      >
        ⌘
      </motion.kbd>
      <motion.kbd
        animate={pressed ? { scale: 0.95, y: 2 } : { scale: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="px-2 py-1 text-xs bg-zinc-800 border border-zinc-700 rounded text-zinc-300 font-mono"
      >
        K
      </motion.kbd>
    </div>
  )
}

function AnimatedChart() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  const points = [
    { x: 0, y: 60 },
    { x: 20, y: 45 },
    { x: 40, y: 55 },
    { x: 60, y: 30 },
    { x: 80, y: 40 },
    { x: 100, y: 15 },
  ]

  const pathD = points.reduce((acc, point, i) => {
    return i === 0 ? `M ${point.x} ${point.y}` : `${acc} L ${point.x} ${point.y}`
  }, "")

  return (
    <svg ref={ref} viewBox="0 0 100 70" className="w-full h-24">
      <defs>
        <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgb(255,255,255)" stopOpacity="0.2" />
          <stop offset="100%" stopColor="rgb(255,255,255)" stopOpacity="0" />
        </linearGradient>
      </defs>
      {isInView && (
        <>
          <path d={`${pathD} L 100 70 L 0 70 Z`} fill="url(#chartGradient)" className="opacity-50" />
          <path d={pathD} fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" className="draw-line" />
        </>
      )}
    </svg>
  )
}

export function BentoGrid() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section id="features" className="py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
            style={{ fontFamily: "var(--font-manrope)" }}
          >
            Multi-Agent Coaching Intelligence
          </h2>
          <p className="text-sm sm:text-base lg:text-lg text-zinc-400 max-w-2xl mx-auto">
            Five autonomous AI agents work in concert - scouting key moments, analyzing form, decoding strategy, and building your personalized coaching plan.
          </p>
        </motion.div>

        <motion.div
          ref={ref}
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4"
        >
          {/* Large card - Temporal Grounding */}
          <motion.div
            variants={itemVariants}
            className="md:col-span-2 group relative p-4 sm:p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-gray-600/50 hover:scale-[1.02] transition-all duration-300 overflow-hidden"
          >
            <div className="flex items-start justify-between mb-8">
              <div>
                <div className="p-2 rounded-lg bg-gradient-to-br from-white/20 to-gray-400/20 w-fit mb-4">
                  <Video className="w-5 h-5 text-white" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">The Scouter</h3>
                <p className="text-zinc-400 text-sm">
                  Pinpoints the exact frame of every critical action. Say "show me the turnover" and jump straight to it - no scrubbing required.
                </p>
              </div>
              <SystemStatus />
            </div>
            <div className="grid grid-cols-4 gap-4">
              {["00:32", "01:15", "03:47", "05:22"].map((time) => (
                <div key={time} className="text-center">
                  <div className="text-sm font-bold text-white mb-1">{time}</div>
                  <div className="text-xs text-zinc-500">Key moment</div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Kinematic Comparison */}
          <motion.div
            variants={itemVariants}
            className="group relative p-4 sm:p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-gray-600/50 hover:scale-[1.02] transition-all duration-300"
          >
            <div className="p-2 rounded-lg bg-gradient-to-br from-white/20 to-gray-400/20 w-fit mb-4">
              <Eye className="w-5 h-5 text-white" strokeWidth={1.5} />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">The Analyst</h3>
            <p className="text-zinc-400 text-sm mb-6">Overlay your mechanics against professional benchmarks and surface the subtle differences that matter most.</p>
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-400">Stance delta:</span>
              <span className="text-white font-mono">-2.3°</span>
            </div>
          </motion.div>

          {/* Tactical Analysis */}
          <motion.div
            variants={itemVariants}
            className="group relative p-4 sm:p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-gray-600/50 hover:scale-[1.02] transition-all duration-300"
          >
            <div className="p-2 rounded-lg bg-gradient-to-br from-white/20 to-gray-400/20 w-fit mb-4">
              <Brain className="w-5 h-5 text-white" strokeWidth={1.5} />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">The Strategist</h3>
            <p className="text-zinc-400 text-sm mb-4">Decode tactical patterns, expose opponent tendencies, and uncover the decision-making behind every play.</p>
          </motion.div>

          {/* Pedagogical Coaching */}
          <motion.div
            variants={itemVariants}
            className="group relative p-4 sm:p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-gray-600/50 hover:scale-[1.02] transition-all duration-300"
          >
            <div className="p-2 rounded-lg bg-gradient-to-br from-white/20 to-gray-400/20 w-fit mb-4">
              <Zap className="w-5 h-5 text-white" strokeWidth={1.5} />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">The Coach</h3>
            <p className="text-zinc-400 text-sm mb-4">
              Generates structured training programs and targeted drills calibrated to your unique strengths and weaknesses.
            </p>
            <div className="flex items-center gap-2 text-white text-sm">
              <span className="font-mono">5-week plan</span>
              <span className="text-zinc-500">Ready to start</span>
            </div>
          </motion.div>

          {/* Multi-Video Comparison */}
          <motion.div
            variants={itemVariants}
            className="group relative p-4 sm:p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-gray-600/50 hover:scale-[1.02] transition-all duration-300"
          >
            <div className="p-2 rounded-lg bg-gradient-to-br from-white/20 to-gray-400/20 w-fit mb-4">
              <Activity className="w-5 h-5 text-white" strokeWidth={1.5} />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Side-by-Side Comparison</h3>
            <p className="text-zinc-400 text-sm mb-4">Place any two performances next to each other — amateur vs. elite, week 1 vs. week 10, you vs. anyone.</p>
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 text-xs bg-white/10 rounded text-gray-200">Video 1</span>
              <span className="px-2 py-1 text-xs bg-gray-400/10 rounded text-gray-300">Video 2</span>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

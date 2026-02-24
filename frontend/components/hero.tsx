"use client"

import { motion } from "framer-motion"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

const avatars = [
  { initials: "AK", from: "from-blue-500", to: "to-cyan-400" },
  { initials: "MJ", from: "from-emerald-500", to: "to-green-400" },
  { initials: "SR", from: "from-violet-500", to: "to-purple-400" },
  { initials: "DT", from: "from-orange-500", to: "to-amber-400" },
  { initials: "LP", from: "from-pink-500", to: "to-rose-400" },
]

const textRevealVariants = {
  hidden: { y: "100%" },
  visible: (i: number) => ({
    y: 0,
    transition: {
      duration: 0.8,
      ease: [0.22, 1, 0.36, 1],
      delay: i * 0.1,
    },
  }),
}

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-4 pt-24 pb-16 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-zinc-950 via-zinc-950 to-zinc-900 pointer-events-none" />

      {/* Hero background image */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <img
          src="/hero-sports.png"
          alt=""
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[45%] w-full min-w-[100%] h-auto opacity-30 sm:w-[120%] md:w-[130%] lg:w-[140%]"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 via-transparent to-zinc-950/70" />
        <div className="absolute inset-0 bg-gradient-to-r from-zinc-950/50 via-transparent to-zinc-950/50" />
      </div>

      {/* Subtle radial glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[400px] h-[300px] sm:w-[600px] sm:h-[400px] md:w-[800px] md:h-[600px] bg-zinc-800/20 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900 border border-zinc-800 mb-8"
        >
          <span className="w-2 h-2 rounded-full bg-white pulse-glow" />
          <span className="text-sm text-zinc-400">Next-Gen Multi-Agent Sports Intelligence</span>
        </motion.div>

        {/* Headline with text mask animation */}
        <h1
          className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-white mb-6"
          style={{ fontFamily: "var(--font-manrope), sans-serif" }}
        >
          <span className="block overflow-hidden">
            <motion.span className="block" variants={textRevealVariants} initial="hidden" animate="visible" custom={0}>
              Decode every
            </motion.span>
          </span>
          <span className="block overflow-hidden">
            <motion.span
              className="block text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-300"
              variants={textRevealVariants}
              initial="hidden"
              animate="visible"
              custom={1}
            >
              move on the field.
            </motion.span>
          </span>
        </h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-lg sm:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Upload gameplay footage and let our multi-agent AI dissect biomechanics, tactics, and performance - delivering elite-level coaching insights in minutes, not weeks.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
        >
          <Link href="/analyze">
            <Button
              size="lg"
              className="shimmer-btn bg-white text-zinc-950 hover:bg-gray-200 rounded-full px-8 h-12 text-base font-medium shadow-lg shadow-white/20 font-semibold"
            >
              Start Analyzing
              <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
          <Button
            variant="outline"
            size="lg"
            className="rounded-full px-8 h-12 text-base font-medium border-gray-600 text-gray-300 hover:bg-zinc-800 hover:text-white hover:border-gray-500 bg-transparent"
          >
            Watch Demo
          </Button>
        </motion.div>

        {/* Social Proof */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="flex flex-col items-center gap-4"
        >
          <div className="flex items-center -space-x-3">
            {avatars.map((avatar, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.5, x: -20 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
                className="relative"
              >
                <div
                  className={`w-10 h-10 rounded-full border-2 border-zinc-950 bg-gradient-to-br ${avatar.from} ${avatar.to} flex items-center justify-center`}
                >
                  <span className="text-white text-xs font-bold">{avatar.initials}</span>
                </div>
              </motion.div>
            ))}
          </div>
          <p className="text-sm text-zinc-500">
            Empowering <span className="text-zinc-300 font-medium">2,000+</span> athletes & coaches worldwide
          </p>
        </motion.div>
      </div>
    </section>
  )
}

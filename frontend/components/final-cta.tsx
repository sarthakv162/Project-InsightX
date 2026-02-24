"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export function FinalCTA() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section className="py-24 px-4">
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 40 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className="max-w-4xl mx-auto text-center"
      >
        <h2
          className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-white mb-6 tracking-tight"
          style={{ fontFamily: "var(--font-manrope)" }}
        >
          Ready to elevate your game?
        </h2>
        <p className="text-sm sm:text-base lg:text-lg text-zinc-400 mb-10 max-w-2xl mx-auto">
          Drop your first video and experience what five AI agents can reveal about your performance. Start free - no credit card required.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/analyze">
            <Button
              size="lg"
              className="shimmer-btn bg-white text-zinc-950 hover:bg-gray-200 rounded-full px-8 h-14 text-base font-medium shadow-lg shadow-white/20 font-semibold"
            >
              Get Started Free
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
          <Button
            variant="outline"
            size="lg"
            className="rounded-full px-8 h-14 text-base font-medium border-gray-600 text-gray-300 hover:bg-zinc-800 hover:text-white hover:border-gray-500 bg-transparent"
          >
            Book a Demo
          </Button>
        </div>

        <p className="mt-8 text-sm text-zinc-500">5 free analyses every month on the Student plan. Upgrade to Coach for unlimited everything.</p>
      </motion.div>
    </section>
  )
}

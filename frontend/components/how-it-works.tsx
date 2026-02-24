"use client"

import { motion } from "framer-motion"
import { Check, Upload, Brain, Target } from "lucide-react"

const steps = [
    {
        icon: Upload,
        title: "Upload Your Footage",
        description: "Drop in your gameplay video - MP4, MOV, AVI, or paste a YouTube link. Our pipeline handles the rest automatically."
    },
    {
        icon: Brain,
        title: "Multi-Agent Breakdown",
        description: "Five specialized AI agents collaborate to analyze form, strategy, key moments, and performance gaps simultaneously."
    },
    {
        icon: Target,
        title: "Actionable Coaching",
        description: "Receive a structured game plan with drill recommendations, technique corrections, and measurable improvement targets."
    }
]

const features = [
    "Frame-level biomechanical analysis",
    "Tactical pattern & formation recognition",
    "Longitudinal performance tracking",
    "Ask anything in natural language",
    "Personalized training blueprints",
    "Player vs. pro comparison engine"
]

export function HowItWorks() {
    return (
        <section id="how-it-works" className="py-24 px-4 relative">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-zinc-900/50 to-transparent pointer-events-none" />

            <div className="relative z-10 max-w-6xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">How It Works</h2>
                    <p className="text-sm sm:text-base lg:text-lg text-zinc-400 max-w-2xl mx-auto">
                        From raw footage to a personalized coaching blueprint - three steps, zero guesswork.
                    </p>
                </motion.div>

                {/* Steps */}
                <div className="grid md:grid-cols-3 gap-4 md:gap-8 mb-16">
                    {steps.map((step, index) => {
                        const Icon = step.icon
                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: index * 0.1 }}
                                className="relative"
                            >
                                <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-4 sm:p-8 hover:border-zinc-700 transition-colors h-full">
                                    <div className="absolute -top-4 left-8 w-8 h-8 bg-white text-zinc-950 rounded-full flex items-center justify-center font-bold">
                                        {index + 1}
                                    </div>
                                    <Icon className="w-8 h-8 text-white mb-4 mt-4" />
                                    <h3 className="text-lg sm:text-xl font-semibold text-white mb-3">{step.title}</h3>
                                    <p className="text-zinc-400 text-sm">{step.description}</p>
                                </div>

                                {/* Connector line */}
                                {index < steps.length - 1 && (
                                    <div className="hidden md:block absolute top-16 -right-4 w-8 h-0.5 bg-gradient-to-r from-white/50 to-transparent" />
                                )}
                            </motion.div>
                        )
                    })}
                </div>

                {/* Features Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-4 sm:p-8 md:p-12"
                >
                    <h3 className="text-xl sm:text-2xl font-bold text-white mb-8">What Sets InsightX Apart</h3>
                    <div className="grid md:grid-cols-2 gap-6">
                        {features.map((feature, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -10 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.6, delay: index * 0.05 }}
                                className="flex items-center gap-3"
                            >
                                <Check className="w-5 h-5 text-white flex-shrink-0" />
                                <span className="text-zinc-300">{feature}</span>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </section>
    )
}

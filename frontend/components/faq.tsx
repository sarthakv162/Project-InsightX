"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"

const faqs = [
    {
        question: "What video formats are supported?",
        answer: "MP4, MOV, AVI, WebM, and all major formats are supported out of the box. You can also paste a YouTube link directly. Maximum file size is 2GB."
    },
    {
        question: "How long does analysis take?",
        answer: "Typically 2–5 minutes. Our multi-agent pipeline runs concurrently, so even longer clips are processed faster than traditional tools."
    },
    {
        question: "Which sports does InsightX support?",
        answer: "Basketball, soccer, football, tennis, cricket, baseball, rugby, and more. Our vision models are sport-agnostic and adapt to any gameplay footage."
    },
    {
        question: "Is my data secure?",
        answer: "Military-grade encryption at rest and in transit. Your footage is never shared, sold, or used for training without explicit consent."
    },
    {
        question: "Can I export or share my reports?",
        answer: "Absolutely. Export detailed reports in PDF, CSV, or JSON - perfect for sharing with coaching staff or integrating into your existing workflow."
    },
    {
        question: "Is there a free tier?",
        answer: "Yes - the Student plan gives you 5 free analyses per month with core features. Upgrade anytime to unlock unlimited uploads and all AI agents."
    }
]

export function FAQ() {
    return (
        <section id="faq" className="py-24 px-4 relative">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-zinc-900/50 to-transparent pointer-events-none" />

            <div className="relative z-10 max-w-6xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">Frequently Asked Questions</h2>
                    <p className="text-sm sm:text-base lg:text-lg text-zinc-400 max-w-2xl mx-auto">
                        Everything you need to know before getting started with InsightX.
                    </p>
                </motion.div>

                {/* FAQ Grid */}
                <div className="grid md:grid-cols-2 gap-4 md:gap-6 mb-12">
                    {faqs.map((faq, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: index * 0.05 }}
                            className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 sm:p-6 hover:border-zinc-700 transition-colors"
                        >
                            <h4 className="text-base sm:text-lg text-white font-semibold mb-3">{faq.question}</h4>
                            <p className="text-zinc-400 text-sm">{faq.answer}</p>
                        </motion.div>
                    ))}
                </div>

                {/* CTA */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center"
                >
                    <p className="text-zinc-400 mb-4">Can't find what you're looking for?</p>
                    <Button className="bg-white text-zinc-950 hover:bg-gray-200 rounded-full px-8">
                        Get in Touch
                    </Button>
                </motion.div>
            </div>
        </section>
    )
}

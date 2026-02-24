"use client"

import { motion } from "framer-motion"
import { BookOpen, Code, Lightbulb, Zap } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

const docSections = [
    {
        icon: BookOpen,
        title: "Getting Started",
        description: "Learn the basics and set up your first analysis",
        content: [
            "Account creation and setup",
            "Uploading your first video",
            "Understanding the dashboard",
            "Basic analysis tutorial"
        ]
    },
    {
        icon: Code,
        title: "API Documentation",
        description: "Integrate InsightX into your applications",
        content: [
            "REST API endpoints",
            "Authentication & API keys",
            "Request/response formats",
            "Code examples & SDKs"
        ]
    },
    {
        icon: Lightbulb,
        title: "Best Practices",
        description: "Tips for getting the most out of InsightX",
        content: [
            "Video quality recommendations",
            "Optimal footage angles",
            "Question formatting tips",
            "Performance optimization"
        ]
    },
    {
        icon: Zap,
        title: "Advanced Features",
        description: "Unlock powerful analysis capabilities",
        content: [
            "Custom training models",
            "Batch processing",
            "Team analytics",
            "Integration guides"
        ]
    }
]

const faqs = [
    {
        question: "What video formats are supported?",
        answer: "We support MP4, MOV, AVI, WebM, and most common video formats. Maximum file size is 2GB."
    },
    {
        question: "How long does analysis take?",
        answer: "Most analyses complete within 2-5 minutes depending on video length and complexity."
    },
    {
        question: "Can I use InsightX for multiple sports?",
        answer: "Yes! Our platform supports all sports including basketball, soccer, football, tennis, and more."
    },
    {
        question: "Is my data secure?",
        answer: "All your data is encrypted and stored securely. We never share your videos without permission."
    },
    {
        question: "Can I export my analysis?",
        answer: "Yes, you can export analysis reports in PDF, CSV, or JSON formats for further analysis."
    },
    {
        question: "What's the pricing model?",
        answer: "We offer flexible plans based on video duration analyzed. Check our pricing page for details."
    }
]

export function Docs() {
    return (
        <section id="docs" className="py-24 px-4 relative">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-zinc-900/50 to-transparent pointer-events-none" />

            <div className="relative z-10 max-w-6xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Documentation</h2>
                    <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
                        Everything you need to know about InsightX. From getting started to advanced integrations.
                    </p>
                </motion.div>

                {/* Doc Sections Grid */}
                <div className="grid md:grid-cols-2 gap-6 mb-16">
                    {docSections.map((section, index) => {
                        const Icon = section.icon
                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: index * 0.1 }}
                                className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 hover:border-zinc-700 transition-all group cursor-pointer"
                            >
                                <Icon className="w-10 h-10 text-amber-500 mb-4 group-hover:scale-110 transition-transform" />
                                <h3 className="text-xl font-semibold text-white mb-2">{section.title}</h3>
                                <p className="text-zinc-400 mb-6">{section.description}</p>
                                <ul className="space-y-2 mb-6">
                                    {section.content.map((item, idx) => (
                                        <li key={idx} className="text-sm text-zinc-300 flex items-center gap-2">
                                            <span className="w-1.5 h-1.5 bg-amber-500 rounded-full" />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="border-zinc-700 text-zinc-300 hover:text-white hover:bg-zinc-800 w-full"
                                >
                                    Learn More →
                                </Button>
                            </motion.div>
                        )
                    })}
                </div>

                {/* FAQ Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <h3 className="text-3xl font-bold text-white mb-8 text-center">Frequently Asked Questions</h3>

                    <div className="grid md:grid-cols-2 gap-6">
                        {faqs.map((faq, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: index * 0.05 }}
                                className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6"
                            >
                                <h4 className="text-white font-semibold mb-3">{faq.question}</h4>
                                <p className="text-zinc-400 text-sm">{faq.answer}</p>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>

                {/* CTA */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="mt-16 text-center"
                >
                    <p className="text-zinc-400 mb-4">Need more help?</p>
                    <Button className="bg-white text-zinc-950 hover:bg-gray-200 rounded-full px-8">
                        Contact Support
                    </Button>
                </motion.div>
            </div>
        </section>
    )
}

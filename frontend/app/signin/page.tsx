"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { ArrowRight, ArrowLeft, Eye, EyeOff, Mail, Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BackgroundPaths } from "@/components/ui/background-paths"
import Link from "next/link"

export default function SignIn() {
    const [showPassword, setShowPassword] = useState(false)
    const [formData, setFormData] = useState({
        email: "",
        password: "",
    })
    const [isLoading, setIsLoading] = useState(false)
    const router = useRouter()

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setFormData((prev) => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)
        // Prototype: skip real auth, navigate to analyze
        setTimeout(() => {
            setIsLoading(false)
            router.push("/analyze")
        }, 1000)
    }

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1, delayChildren: 0.2 },
        },
    }

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-950 to-zinc-900 flex items-center justify-center px-4 py-12 relative overflow-hidden">
            {/* Back Button */}
            <Link href="/" className="absolute top-4 left-4 sm:top-6 sm:left-6 z-50 inline-flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                <ArrowLeft size={18} className="sm:w-5 sm:h-5" />
                <span className="text-xs sm:text-sm font-medium">Back</span>
            </Link>

            {/* Animated Background Paths with Sports Elements */}
            <BackgroundPaths />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="relative z-10 w-full max-w-md"
            >

                {/* Header */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    className="text-center mb-8"
                >
                    <Link href="/" className="inline-flex items-center gap-2 mb-8">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-white to-gray-300 flex items-center justify-center">
                            <span className="text-zinc-950 font-bold text-base">IX</span>
                        </div>
                        <span className="font-semibold text-white text-lg">InsightX</span>
                    </Link>

                    <motion.h1
                        variants={itemVariants}
                        className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2"
                    >
                        Welcome Back
                    </motion.h1>
                    <motion.p
                        variants={itemVariants}
                        className="text-sm sm:text-base text-zinc-400"
                    >
                        Sign in to access your sports analysis dashboard
                    </motion.p>
                </motion.div>

                {/* Form Card */}
                <motion.div
                    variants={itemVariants}
                    className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 backdrop-blur-sm"
                >
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Email */}
                        <motion.div variants={itemVariants}>
                            <label className="block text-sm font-medium text-zinc-300 mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-3 w-5 h-5 text-zinc-500" />
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    placeholder="you@example.com"
                                    className="w-full pl-10 pr-4 py-2.5 bg-zinc-800/50 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-white focus:ring-1 focus:ring-white/20 transition-colors"
                                />
                            </div>
                        </motion.div>

                        {/* Password */}
                        <motion.div variants={itemVariants}>
                            <label className="block text-sm font-medium text-zinc-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-zinc-500" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    placeholder="••••••••"
                                    className="w-full pl-10 pr-10 py-2.5 bg-zinc-800/50 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-white focus:ring-1 focus:ring-white/20 transition-colors"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-3 text-zinc-500 hover:text-zinc-300"
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </motion.div>

                        {/* Sign In Button */}
                        <motion.button
                            variants={itemVariants}
                            type="submit"
                            disabled={isLoading}
                            className="w-full mt-6 shimmer-btn bg-white text-zinc-950 hover:bg-gray-100 disabled:bg-gray-400 rounded-full py-2.5 font-semibold transition-all flex items-center justify-center gap-2 shadow-lg shadow-white/20"
                        >
                            {isLoading ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-zinc-950 border-t-transparent rounded-full animate-spin" />
                                    Signing In...
                                </>
                            ) : (
                                <>
                                    Sign In
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </motion.button>
                    </form>

                    {/* Divider */}
                    <div className="relative my-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-zinc-700" />
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-zinc-900/50 text-zinc-500">or</span>
                        </div>
                    </div>

                    {/* Sign Up Link */}
                    <motion.div variants={itemVariants} className="text-center">
                        <p className="text-zinc-400 text-sm">
                            Don't have an account?{" "}
                            <Link href="/signup" className="text-white hover:text-gray-200 font-semibold transition-colors">
                                Sign up
                            </Link>
                        </p>
                    </motion.div>
                </motion.div>

                {/* Footer */}
                <motion.div
                    variants={itemVariants}
                    className="mt-6 text-center text-sm text-zinc-500"
                >
                    <p>
                        By signing in, you agree to our{" "}
                        <a href="#" className="text-zinc-400 hover:text-zinc-300">
                            Terms of Service
                        </a>
                        {" "}and{" "}
                        <a href="#" className="text-zinc-400 hover:text-zinc-300">
                            Privacy Policy
                        </a>
                    </p>
                </motion.div>
            </motion.div>
        </div>
    )
}

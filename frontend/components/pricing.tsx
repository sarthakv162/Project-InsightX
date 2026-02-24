"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useState } from "react"
import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"

const plans = [
  {
    name: "Student",
    description: "Perfect for solo athletes and learners getting started",
    price: { monthly: 0, yearly: 0 },
    features: ["5 video uploads/day", "Basic analysis", "Timestamp extraction", "Community support", "7-day analysis history"],
    cta: "Get Started Free",
    highlighted: false,
  },
  {
    name: "Coach",
    description: "For dedicated coaches and competitive athletes",
    price: { monthly: 1999, yearly: 1599 },
    features: [
      "Unlimited video uploads",
      "All AI agents (Scouter, Analyst, Strategist, Coach)",
      "Side-by-side video comparison",
      "Custom training regimens",
      "Priority support",
      "Unlimited analysis history",
      "API access",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Institution",
    description: "Enterprise-grade tools for academies and organizations",
    price: { monthly: 7999, yearly: 6399 },
    features: [
      "Everything in Coach",
      "Team management (50+ members)",
      "Dedicated support",
      "Custom integrations",
      "White-label analytics",
      "Advanced reporting",
      "SLA guarantee",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
]

function BorderBeam() {
  return (
    <div className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none">
      <div
        className="absolute w-24 h-24 bg-white/20 blur-xl border-beam"
        style={{
          offsetPath: "rect(0 100% 100% 0 round 16px)",
        }}
      />
    </div>
  )
}

export function Pricing() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly")

  return (
    <section id="pricing" className="py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
            style={{ fontFamily: "var(--font-manrope)" }}
          >
            Built for every ambition
          </h2>
          <p className="text-sm sm:text-base lg:text-lg text-zinc-400 max-w-2xl mx-auto mb-8">
            Whether you're training solo or managing an entire academy - there's a plan that fits.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center p-1 rounded-full bg-zinc-900 border border-zinc-800">
            <button
              onClick={() => setBillingCycle("monthly")}
              className={`relative px-4 py-2 text-sm font-medium rounded-full transition-colors ${billingCycle === "monthly" ? "text-white" : "text-zinc-400"
                }`}
            >
              {billingCycle === "monthly" && (
                <motion.div
                  layoutId="billing-toggle"
                  className="absolute inset-0 bg-zinc-800 rounded-full"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
              <span className="relative z-10">Monthly</span>
            </button>
            <button
              onClick={() => setBillingCycle("yearly")}
              className={`relative px-4 py-2 text-sm font-medium rounded-full transition-colors ${billingCycle === "yearly" ? "text-white" : "text-zinc-400"
                }`}
            >
              {billingCycle === "yearly" && (
                <motion.div
                  layoutId="billing-toggle"
                  className="absolute inset-0 bg-zinc-800 rounded-full"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
              <span className="relative z-10">Yearly</span>
              <span className="relative z-10 ml-2 px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-400 rounded-full">
                -20%
              </span>
            </button>
          </div>
        </motion.div>

        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              className={`relative p-4 sm:p-6 rounded-2xl border transition-all duration-300 hover:scale-[1.02] flex flex-col ${plan.highlighted
                ? "bg-zinc-900 border-zinc-700"
                : "bg-zinc-900/50 border-zinc-800 hover:border-zinc-600"
                }`}
            >
              {plan.highlighted && <BorderBeam />}

              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-white text-zinc-950 text-xs font-medium rounded-full">
                  Most Popular
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">{plan.name}</h3>
                <p className="text-zinc-400 text-sm">{plan.description}</p>
              </div>

              <div className="mb-6">
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl sm:text-4xl font-bold text-white">₹{plan.price[billingCycle]}</span>
                  {plan.price.monthly > 0 && <span className="text-zinc-400 text-sm">/month</span>}
                </div>
                {billingCycle === "yearly" && plan.price.yearly > 0 && (
                  <p className="text-xs text-zinc-500 mt-1">Billed annually (₹{plan.price.yearly * 12}/year)</p>
                )}
              </div>

              <ul className="space-y-3 mb-8 flex-grow">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-sm text-zinc-300">
                    <Check className="w-4 h-4 text-emerald-500 shrink-0" strokeWidth={1.5} />
                    {feature}
                  </li>
                ))}
              </ul>

              <Button
                className={`w-full rounded-full ${plan.highlighted
                  ? "shimmer-btn bg-white text-zinc-950 hover:bg-gray-200 shadow-lg shadow-white/20 font-semibold"
                  : "bg-zinc-800 text-white hover:bg-zinc-700 border border-zinc-700"
                  }`}
              >
                {plan.cta}
              </Button>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

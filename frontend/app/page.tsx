import { SmoothScroll } from "@/components/smooth-scroll"
import { Navbar } from "@/components/navbar"
import { Hero } from "@/components/hero"
import { LogoMarquee } from "@/components/logo-marquee"
import { BackgroundVideo } from "@/components/background-video"
import { BentoGrid } from "@/components/bento-grid"
import { HowItWorks } from "@/components/how-it-works"
import { Pricing } from "@/components/pricing"
import { FAQ } from "@/components/faq"
import { FinalCTA } from "@/components/final-cta"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <SmoothScroll>
      <main className="relative min-h-screen bg-zinc-950">
        <Navbar />
        <Hero />
        <LogoMarquee />
        <BackgroundVideo />
        <div className="relative z-[1]">
          <BentoGrid />
          <HowItWorks />
          <Pricing />
          <FAQ />
          <FinalCTA />
          <Footer />
        </div>
      </main>
    </SmoothScroll>
  )
}

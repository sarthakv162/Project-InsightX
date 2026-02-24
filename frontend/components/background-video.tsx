"use client"

import { useEffect, useRef, useState } from "react"

export function BackgroundVideo() {
    const containerRef = useRef<HTMLDivElement>(null)
    const videoRef = useRef<HTMLVideoElement>(null)
    const [opacity, setOpacity] = useState(0)

    useEffect(() => {
        const handleScroll = () => {
            if (!containerRef.current) return

            const rect = containerRef.current.getBoundingClientRect()
            const viewportHeight = window.innerHeight

            // Fade in: from when the container top reaches the bottom of viewport
            // to when the container top reaches the middle of viewport
            const fadeStart = viewportHeight // container top at viewport bottom
            const fadeEnd = viewportHeight * 0.3 // container top near viewport top-third

            if (rect.top >= fadeStart) {
                setOpacity(0)
            } else if (rect.top <= fadeEnd) {
                setOpacity(1)
            } else {
                const progress = 1 - (rect.top - fadeEnd) / (fadeStart - fadeEnd)
                setOpacity(Math.max(0, Math.min(1, progress)))
            }
        }

        window.addEventListener("scroll", handleScroll, { passive: true })
        handleScroll()

        return () => window.removeEventListener("scroll", handleScroll)
    }, [])

    useEffect(() => {
        // Auto-play the video when it becomes visible
        const video = videoRef.current
        if (!video) return

        if (opacity > 0) {
            video.play().catch(() => { })
        }
    }, [opacity])

    return (
        <>
            {/* Scroll anchor - place this where you want the video to start fading in */}
            <div ref={containerRef} className="relative h-0 w-full" aria-hidden="true" />

            {/* Fixed background video layer */}
            <div
                className="fixed inset-0 z-0 pointer-events-none transition-opacity duration-700"
                style={{ opacity: opacity * 0.15 }}
            >
                <video
                    ref={videoRef}
                    className="absolute inset-0 w-full h-full object-cover"
                    src="/bgclip.mp4"
                    muted
                    loop
                    playsInline
                    preload="auto"
                />
            </div>
        </>
    )
}

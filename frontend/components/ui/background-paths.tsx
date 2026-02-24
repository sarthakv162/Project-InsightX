"use client";

import { motion } from "framer-motion";

/**
 * Floating SVG paths animation with sports-themed silhouettes.
 * Renders animated curved paths + faint sport icon outlines
 * (basketball, soccer ball, tennis racket, running figure, etc.)
 */

/* ---------- curved flowing paths (from reference) ---------- */
function FloatingPaths({ position }: { position: number }) {
    const paths = Array.from({ length: 36 }, (_, i) => ({
        id: i,
        d: `M-${380 - i * 5 * position} -${189 + i * 6}C-${380 - i * 5 * position
            } -${189 + i * 6} -${312 - i * 5 * position} ${216 - i * 6} ${152 - i * 5 * position
            } ${343 - i * 6}C${616 - i * 5 * position} ${470 - i * 6} ${684 - i * 5 * position
            } ${875 - i * 6} ${684 - i * 5 * position} ${875 - i * 6}`,
        width: 0.5 + i * 0.03,
    }));

    return (
        <div className="absolute inset-0 pointer-events-none">
            <svg
                className="w-full h-full text-white"
                viewBox="0 0 696 316"
                fill="none"
            >
                <title>Background Paths</title>
                {paths.map((path) => (
                    <motion.path
                        key={path.id}
                        d={path.d}
                        stroke="currentColor"
                        strokeWidth={path.width}
                        strokeOpacity={0.04 + path.id * 0.015}
                        initial={{ pathLength: 0.3, opacity: 0.6 }}
                        animate={{
                            pathLength: 1,
                            opacity: [0.3, 0.6, 0.3],
                            pathOffset: [0, 1, 0],
                        }}
                        transition={{
                            duration: 20 + Math.random() * 10,
                            repeat: Number.POSITIVE_INFINITY,
                            ease: "linear",
                        }}
                    />
                ))}
            </svg>
        </div>
    );
}

/* ---------- sport icon silhouettes ---------- */

const sportIcons = [
    {
        // Basketball
        id: "basketball",
        x: "12%",
        y: "18%",
        size: 64,
        path: "M32 2a30 30 0 1 0 0 60 30 30 0 0 0 0-60Zm0 4a26 26 0 0 1 18.4 7.6A37 37 0 0 1 32 18a37 37 0 0 1-18.4-4.4A26 26 0 0 1 32 6ZM6 32a26 26 0 0 1 5.6-16.1A33 33 0 0 0 32 22a33 33 0 0 0 20.4-6.1A26 26 0 0 1 58 32H34V6.1A26 26 0 0 0 6 32Zm28 26a26 26 0 0 1-25.8-22H30v22a26 26 0 0 1-0 0Zm4 0V36h22a26 26 0 0 1-22 22Z",
        delay: 0,
    },
    {
        // Soccer ball
        id: "soccer",
        x: "82%",
        y: "72%",
        size: 56,
        path: "M28 2a26 26 0 1 0 0 52 26 26 0 0 0 0-52Zm0 4 8 6-3 9H23l-3-9Zm-14 10 4-3 3 8-6 7H9Zm0 22h6l6 7-3 8-4-2a22 22 0 0 1-5-13Zm24 12-3-8 6-7h7a22 22 0 0 1-5 13Zm5-17h-7l-3-9 8-6 4 3a22 22 0 0 1 1 9Z",
        delay: 2,
    },
    {
        // Running person
        id: "runner",
        x: "88%",
        y: "22%",
        size: 52,
        path: "M26 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm-6 12 6 4 8-4 2 6-6 8v10h-4V30l-4-4-6 8v10h-4V28Z",
        delay: 4,
    },
    {
        // Tennis racket
        id: "tennis",
        x: "15%",
        y: "75%",
        size: 48,
        path: "M30 4a14 14 0 0 0-14 14c0 4 2 8 4 10l-12 12 3 3 12-12c2 2 6 4 10 4a14 14 0 0 0 0-28Zm0 4a10 10 0 1 1 0 20 10 10 0 0 1 0-20Z",
        delay: 6,
    },
    {
        // Trophy
        id: "trophy",
        x: "50%",
        y: "85%",
        size: 44,
        path: "M14 4v2H6v8a8 8 0 0 0 7 8v2a6 6 0 0 1-5 6v2h20v-2a6 6 0 0 1-5-6v-2a8 8 0 0 0 7-8V6h-8V4Zm-4 4h4v8a4 4 0 0 1-4-4Zm16 0h4v4a4 4 0 0 1-4 4Z",
        delay: 3,
    },
    {
        // Whistle
        id: "whistle",
        x: "72%",
        y: "14%",
        size: 40,
        path: "M8 12h12l8 6v8a8 8 0 0 1-16 0v-4H8Zm4 4a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z",
        delay: 5,
    },
];

function SportIcons() {
    return (
        <div className="absolute inset-0 pointer-events-none">
            {sportIcons.map((icon) => (
                <motion.div
                    key={icon.id}
                    className="absolute"
                    style={{
                        left: icon.x,
                        top: icon.y,
                        transform: "translate(-50%, -50%)",
                    }}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{
                        opacity: [0.04, 0.1, 0.04],
                        scale: [0.9, 1.05, 0.9],
                        y: [0, -8, 0],
                    }}
                    transition={{
                        duration: 12 + icon.delay,
                        repeat: Number.POSITIVE_INFINITY,
                        ease: "easeInOut",
                        delay: icon.delay,
                    }}
                >
                    <svg
                        width={icon.size}
                        height={icon.size}
                        viewBox="0 0 64 64"
                        fill="none"
                        className="text-white"
                    >
                        <path
                            d={icon.path}
                            fill="currentColor"
                            fillOpacity={0.15}
                            stroke="currentColor"
                            strokeWidth={0.5}
                            strokeOpacity={0.2}
                        />
                    </svg>
                </motion.div>
            ))}
        </div>
    );
}

/* ---------- main export ---------- */

export function BackgroundPaths() {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <FloatingPaths position={1} />
            <FloatingPaths position={-1} />
            <SportIcons />
        </div>
    );
}

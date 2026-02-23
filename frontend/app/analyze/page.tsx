"use client"

import { useState, useRef, useCallback, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { ParticleField } from "@/components/particle-field"
import {
    ArrowUpIcon,
    Upload,
    Link2,
    ArrowLeft,
    Loader2,
    Video,
    Sparkles,
    Search,
    Target,
    Brain,
    Trophy,
    Dumbbell,
} from "lucide-react"

const API = "http://localhost:8000"

/* ── Types ──────────────────────────────────────────────── */
interface Message {
    role: "user" | "assistant"
    content: string
}

interface SessionInfo {
    session_id: string
    sport: string
    source_type: string
    youtube_url?: string
    filename?: string
}

/* ── Auto-resize Textarea Hook ──────────────────────────── */
function useAutoResizeTextarea({ minHeight, maxHeight }: { minHeight: number; maxHeight?: number }) {
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const adjustHeight = useCallback(
        (reset?: boolean) => {
            const ta = textareaRef.current
            if (!ta) return
            if (reset) { ta.style.height = `${minHeight}px`; return }
            ta.style.height = `${minHeight}px`
            const h = Math.max(minHeight, Math.min(ta.scrollHeight, maxHeight ?? Infinity))
            ta.style.height = `${h}px`
        },
        [minHeight, maxHeight],
    )
    useEffect(() => {
        if (textareaRef.current) textareaRef.current.style.height = `${minHeight}px`
    }, [minHeight])
    return { textareaRef, adjustHeight }
}

/* ── YouTube ID Extractor ───────────────────────────────── */
function extractYouTubeId(url: string) {
    const m = url.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([\w-]+)/)
    return m ? m[1] : null
}

/* ── Basic Markdown → HTML ──────────────────────────────── */
function renderMarkdown(text: string) {
    return text
        .replace(/^#### (.+)$/gm, "<h4 class='text-sm font-semibold text-white mt-4 mb-1'>$1</h4>")
        .replace(/^### (.+)$/gm, "<h3 class='text-base font-bold text-white mt-5 mb-2'>$1</h3>")
        .replace(/^## (.+)$/gm, "<h2 class='text-lg font-bold text-white mt-6 mb-2'>$2</h2>")
        .replace(/\*\*(.+?)\*\*/g, "<strong class='text-white'>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/`([^`]+)`/g, "<code class='bg-zinc-800 px-1.5 py-0.5 rounded text-xs text-zinc-300'>$1</code>")
        .replace(/^- (.+)$/gm, "<li class='ml-4 list-disc text-zinc-300'>$1</li>")
        .replace(/^\d+\.\s+(.+)$/gm, "<li class='ml-4 list-decimal text-zinc-300'>$1</li>")
        .replace(/\n\n/g, "</p><p class='mb-3'>")
        .replace(/\n/g, "<br/>")
}

/* ── Suggestion Pills ───────────────────────────────────── */
const suggestions = [
    { icon: <Search className="w-3.5 h-3.5" />, text: "What mistakes happened in the video?" },
    { icon: <Target className="w-3.5 h-3.5" />, text: "Take me to the instance where the issue happened" },
    { icon: <Brain className="w-3.5 h-3.5" />, text: "Compare the players' techniques" },
    { icon: <Trophy className="w-3.5 h-3.5" />, text: "How could the opponent have won?" },
    { icon: <Dumbbell className="w-3.5 h-3.5" />, text: "Create a training plan to improve" },
]

/* ═══════════════════════════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════════════════════════ */
export default function AnalyzePage() {
    // Stage: "input" | "chat"
    const [stage, setStage] = useState<"input" | "chat">("input")

    // Input state
    const [inputMode, setInputMode] = useState<"upload" | "youtube">("youtube")
    const [youtubeUrl, setYoutubeUrl] = useState("")
    const [sport, setSport] = useState("unknown")
    const [dragOver, setDragOver] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [uploadedFileName, setUploadedFileName] = useState("")
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Chat state
    const [session, setSession] = useState<SessionInfo | null>(null)
    const [messages, setMessages] = useState<Message[]>([])
    const [query, setQuery] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")
    const chatEndRef = useRef<HTMLDivElement>(null)
    const { textareaRef, adjustHeight } = useAutoResizeTextarea({ minHeight: 52, maxHeight: 180 })

    // Auto-scroll chat
    useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages, loading])

    /* ── Submit Video ───────────────────────────────────────── */
    const submitYouTube = async () => {
        if (!youtubeUrl.trim()) return
        setUploading(true)
        setError("")
        try {
            const res = await fetch(`${API}/api/video/youtube`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: youtubeUrl.trim(), sport }),
            })
            if (!res.ok) throw new Error(await res.text())
            const data = await res.json()
            setSession(data)
            setStage("chat")
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : "Failed to submit URL")
        } finally {
            setUploading(false)
        }
    }

    const uploadFile = useCallback(async (file: File) => {
        setUploading(true)
        setUploadedFileName(file.name)
        setError("")
        const form = new FormData()
        form.append("file", file)
        form.append("sport", sport)
        try {
            const res = await fetch(`${API}/api/video/upload`, { method: "POST", body: form })
            if (!res.ok) throw new Error(await res.text())
            const data = await res.json()
            setSession(data)
            setStage("chat")
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : "Upload failed")
        } finally {
            setUploading(false)
        }
    }, [sport])

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setDragOver(false)
        const file = e.dataTransfer.files[0]
        if (file) uploadFile(file)
    }, [uploadFile])

    /* ── Send Chat Query ────────────────────────────────────── */
    const sendQuery = async (q?: string) => {
        const text = (q || query).trim()
        if (!text || loading || !session) return
        setQuery("")
        adjustHeight(true)
        setMessages(prev => [...prev, { role: "user", content: text }])
        setLoading(true)
        setError("")
        try {
            const res = await fetch(`${API}/api/analysis/query`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: session.session_id, query: text, sport }),
            })
            if (!res.ok) throw new Error(await res.text())
            const data = await res.json()
            setMessages(prev => [...prev, { role: "assistant", content: data.response }])
        } catch (e: unknown) {
            const msg = e instanceof Error ? e.message : "Analysis failed"
            setError(msg)
            setMessages(prev => [...prev, { role: "assistant", content: `⚠ Error: ${msg}` }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            sendQuery()
        }
    }

    /* ── Video Embed ────────────────────────────────────────── */
    const renderVideo = () => {
        if (!session) return null
        if (session.source_type === "youtube" && session.youtube_url) {
            const vid = extractYouTubeId(session.youtube_url)
            if (vid) {
                return (
                    <iframe
                        src={`https://www.youtube.com/embed/${vid}`}
                        title="Video"
                        className="w-full h-full rounded-xl"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                    />
                )
            }
        }
        if (session.source_type === "upload" && session.filename) {
            return (
                <video controls className="w-full h-full rounded-xl object-contain bg-black">
                    <source src={`${API}/api/video/file/${session.filename}`} type="video/mp4" />
                </video>
            )
        }
        return null
    }

    /* ═════════════════════════════════════════════════════════
       RENDER: INPUT STAGE
       ═════════════════════════════════════════════════════════ */
    if (stage === "input") {
        return (
            <main className="min-h-screen bg-zinc-950 flex flex-col relative overflow-hidden">
                {/* Animated particle background */}
                <ParticleField />

                {/* Minimal nav */}
                <nav className="relative z-10 flex items-center justify-between px-6 py-4">
                    <Link href="/" className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-4 h-4" />
                        <span className="text-sm">Back</span>
                    </Link>
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-white to-gray-300 flex items-center justify-center">
                            <span className="text-zinc-950 font-bold text-xs">IX</span>
                        </div>
                        <span className="font-semibold text-white text-sm">InsightX</span>
                    </div>
                    <div className="w-16" />
                </nav>

                {/* Main content */}
                <div className="flex-1 flex flex-col items-center justify-center px-4 pb-20 relative z-10">
                    {/* Background glow */}
                    <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-zinc-800/15 rounded-full blur-3xl pointer-events-none" />

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="relative z-10 w-full max-w-2xl"
                    >
                        {/* Header */}
                        <div className="text-center mb-10">
                            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 mb-6">
                                <Sparkles className="w-3.5 h-3.5 text-zinc-400" />
                                <span className="text-xs text-zinc-400">5-Agent AI Pipeline</span>
                            </div>
                            <h1
                                className="text-3xl sm:text-4xl font-bold text-white mb-3"
                                style={{ fontFamily: "var(--font-manrope), sans-serif" }}
                            >
                                Upload your video
                            </h1>
                            <p className="text-zinc-500 text-sm sm:text-base">
                                Drop a video file or paste a YouTube link to begin AI coaching analysis
                            </p>
                        </div>

                        {/* Toggle: Upload / YouTube */}
                        <div className="flex items-center justify-center gap-1 p-1 bg-zinc-900 rounded-full border border-zinc-800 mb-8 max-w-xs mx-auto">
                            <button
                                onClick={() => setInputMode("youtube")}
                                className={cn(
                                    "flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-full text-sm transition-all",
                                    inputMode === "youtube"
                                        ? "bg-white text-zinc-950 font-medium"
                                        : "text-zinc-400 hover:text-white"
                                )}
                            >
                                <Link2 className="w-3.5 h-3.5" />
                                YouTube URL
                            </button>
                            <button
                                onClick={() => setInputMode("upload")}
                                className={cn(
                                    "flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-full text-sm transition-all",
                                    inputMode === "upload"
                                        ? "bg-white text-zinc-950 font-medium"
                                        : "text-zinc-400 hover:text-white"
                                )}
                            >
                                <Upload className="w-3.5 h-3.5" />
                                Upload
                            </button>
                        </div>

                        {/* Sport Selector */}
                        <div className="mb-6">
                            <label className="block text-xs text-zinc-500 mb-2 font-medium">Sport</label>
                            <select
                                value={sport}
                                onChange={e => setSport(e.target.value)}
                                className="w-full px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white outline-none focus:border-zinc-600 transition-colors appearance-none cursor-pointer"
                            >
                                <option value="unknown">Auto-detect</option>
                                <option value="cricket">🏏 Cricket</option>
                                <option value="tennis">🎾 Tennis</option>
                                <option value="basketball">🏀 Basketball</option>
                                <option value="football">⚽ Football</option>
                                <option value="badminton">🏸 Badminton</option>
                            </select>
                        </div>

                        {/* Error */}
                        <AnimatePresence>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="mb-4 px-4 py-3 bg-red-950/50 border border-red-800/50 rounded-xl text-red-400 text-sm"
                                >
                                    ⚠ {error}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* YouTube Input */}
                        {inputMode === "youtube" && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                                <div className="relative bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
                                    <input
                                        type="url"
                                        placeholder="https://youtube.com/watch?v=… or youtube.com/shorts/…"
                                        value={youtubeUrl}
                                        onChange={e => setYoutubeUrl(e.target.value)}
                                        onKeyDown={e => e.key === "Enter" && submitYouTube()}
                                        className="w-full px-4 py-4 bg-transparent text-white text-sm outline-none placeholder:text-zinc-600"
                                    />
                                    <div className="flex items-center justify-end px-3 pb-3">
                                        <Button
                                            onClick={submitYouTube}
                                            disabled={uploading || !youtubeUrl.trim()}
                                            className="shimmer-btn bg-white text-zinc-950 hover:bg-zinc-200 rounded-full px-6 h-9 text-sm font-medium disabled:opacity-40"
                                        >
                                            {uploading ? (
                                                <><Loader2 className="w-4 h-4 animate-spin mr-2" />Processing…</>
                                            ) : (
                                                <>Analyze <Sparkles className="w-3.5 h-3.5 ml-1.5" /></>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* File Upload */}
                        {inputMode === "upload" && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                                <div
                                    className={cn(
                                        "relative rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition-all",
                                        dragOver
                                            ? "border-white/30 bg-zinc-800/30"
                                            : "border-zinc-800 bg-zinc-900/50 hover:border-zinc-700 hover:bg-zinc-900"
                                    )}
                                    onClick={() => fileInputRef.current?.click()}
                                    onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                                    onDragLeave={() => setDragOver(false)}
                                    onDrop={onDrop}
                                >
                                    <input ref={fileInputRef} type="file" accept="video/*" className="hidden"
                                        onChange={e => { const f = e.target.files?.[0]; if (f) uploadFile(f) }}
                                    />
                                    {uploading ? (
                                        <div className="flex flex-col items-center gap-3">
                                            <Loader2 className="w-8 h-8 text-white animate-spin" />
                                            <p className="text-sm text-zinc-300">Uploading {uploadedFileName}…</p>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center gap-3">
                                            <div className="w-12 h-12 rounded-xl bg-zinc-800 flex items-center justify-center">
                                                <Video className="w-6 h-6 text-zinc-400" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-white font-medium">Drag & drop a video file</p>
                                                <p className="text-xs text-zinc-500 mt-1">or click to browse · MP4, AVI, MOV, MKV</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </motion.div>
                </div>
            </main>
        )
    }

    /* ═════════════════════════════════════════════════════════
       RENDER: CHAT STAGE
       ═════════════════════════════════════════════════════════ */
    return (
        <main className="min-h-screen bg-zinc-950 flex flex-col">
            {/* Top bar */}
            <nav className="flex items-center justify-between px-6 py-3 border-b border-zinc-900">
                <button
                    onClick={() => { setStage("input"); setMessages([]); setSession(null) }}
                    className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors text-sm"
                >
                    <ArrowLeft className="w-4 h-4" />
                    New Video
                </button>
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-md bg-gradient-to-br from-white to-gray-300 flex items-center justify-center">
                        <span className="text-zinc-950 font-bold text-[10px]">IX</span>
                    </div>
                    <span className="font-semibold text-white text-sm">InsightX</span>
                </div>
                <div className="flex items-center gap-2">
                    <select
                        value={sport}
                        onChange={e => setSport(e.target.value)}
                        className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-300 outline-none cursor-pointer appearance-none"
                    >
                        <option value="unknown">Auto-detect</option>
                        <option value="cricket">🏏 Cricket</option>
                        <option value="tennis">🎾 Tennis</option>
                        <option value="basketball">🏀 Basketball</option>
                        <option value="football">⚽ Football</option>
                        <option value="badminton">🏸 Badminton</option>
                    </select>
                </div>
            </nav>

            {/* Two-panel layout */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left: Video */}
                <div className="w-1/2 p-4 flex flex-col gap-3 border-r border-zinc-900">
                    <div className="flex-1 bg-zinc-900 rounded-xl overflow-hidden flex items-center justify-center">
                        {renderVideo()}
                    </div>
                    <div className="flex items-center justify-between px-1">
                        <div className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 pulse-glow" />
                            <span className="text-xs text-zinc-500">Session {session?.session_id.slice(0, 8)}…</span>
                        </div>
                        <span className="text-xs text-zinc-600">
                            {session?.source_type === "youtube" ? "YouTube" : "Uploaded"}
                        </span>
                    </div>
                </div>

                {/* Right: Chat */}
                <div className="w-1/2 flex flex-col">
                    {/* Messages area */}
                    <div className="flex-1 overflow-y-auto px-6 py-6">
                        {messages.length === 0 && !loading && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex flex-col items-center justify-center h-full text-center"
                            >
                                <div className="w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-5">
                                    <Sparkles className="w-6 h-6 text-zinc-500" />
                                </div>
                                <h2
                                    className="text-xl font-bold text-white mb-2"
                                    style={{ fontFamily: "var(--font-manrope), sans-serif" }}
                                >
                                    Ask anything about your video
                                </h2>
                                <p className="text-sm text-zinc-500 max-w-sm mb-8">
                                    Our 5-agent coaching staff analyzes biomechanics, tactics, timestamps, and creates training plans — just ask.
                                </p>

                                {/* Suggestion pills */}
                                <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                                    {suggestions.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => { setQuery(s.text); sendQuery(s.text) }}
                                            className="flex items-center gap-2 px-3.5 py-2 bg-zinc-900 hover:bg-zinc-800 rounded-full border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-white transition-all text-xs"
                                        >
                                            {s.icon}
                                            <span>{s.text}</span>
                                        </button>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {messages.map((msg, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3 }}
                                className={cn("mb-4", msg.role === "user" ? "flex justify-end" : "")}
                            >
                                {msg.role === "user" ? (
                                    <div className="max-w-[80%] px-4 py-3 bg-white text-zinc-950 rounded-2xl rounded-br-sm text-sm">
                                        {msg.content}
                                    </div>
                                ) : (
                                    <div className="max-w-[95%]">
                                        <div className="flex items-center gap-2 mb-2">
                                            <div className="w-5 h-5 rounded-md bg-gradient-to-br from-white to-gray-300 flex items-center justify-center">
                                                <span className="text-zinc-950 font-bold text-[8px]">IX</span>
                                            </div>
                                            <span className="text-xs text-zinc-500 font-medium">InsightX</span>
                                        </div>
                                        <div
                                            className="text-sm text-zinc-300 leading-relaxed [&_h3]:text-white [&_h3]:font-bold [&_h3]:mt-4 [&_h3]:mb-1 [&_strong]:text-white [&_li]:my-0.5 [&_code]:bg-zinc-800 [&_code]:px-1 [&_code]:rounded"
                                            dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                                        />
                                    </div>
                                )}
                            </motion.div>
                        ))}

                        {/* Loading */}
                        {loading && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex items-center gap-3 py-3"
                            >
                                <div className="w-5 h-5 rounded-md bg-gradient-to-br from-white to-gray-300 flex items-center justify-center">
                                    <span className="text-zinc-950 font-bold text-[8px]">IX</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: "0ms" }} />
                                    <span className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: "150ms" }} />
                                    <span className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: "300ms" }} />
                                </div>
                                <span className="text-xs text-zinc-600">Analyzing with 5-agent pipeline…</span>
                            </motion.div>
                        )}

                        <div ref={chatEndRef} />
                    </div>

                    {/* Input bar (v0-style) */}
                    <div className="p-4 border-t border-zinc-900">
                        <AnimatePresence>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="mb-3 px-3 py-2 bg-red-950/50 border border-red-800/50 rounded-lg text-red-400 text-xs"
                                >
                                    ⚠ {error}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="relative bg-zinc-900 rounded-xl border border-zinc-800 focus-within:border-zinc-700 transition-colors">
                            <Textarea
                                ref={textareaRef}
                                value={query}
                                onChange={e => { setQuery(e.target.value); adjustHeight() }}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask about technique, tactics, training, timestamps…"
                                disabled={loading}
                                className={cn(
                                    "w-full px-4 py-3.5",
                                    "resize-none bg-transparent border-none",
                                    "text-white text-sm",
                                    "focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0",
                                    "placeholder:text-zinc-600 placeholder:text-sm",
                                    "min-h-[52px] disabled:opacity-50"
                                )}
                                style={{ overflow: "hidden" }}
                            />
                            <div className="flex items-center justify-between px-3 pb-3">
                                <div className="flex items-center gap-1.5">
                                    <button
                                        onClick={() => { setStage("input"); setMessages([]); setSession(null) }}
                                        className="px-2.5 py-1.5 rounded-lg text-xs text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors border border-dashed border-zinc-800 hover:border-zinc-700 flex items-center gap-1.5"
                                    >
                                        <Video className="w-3.5 h-3.5" />
                                        New Video
                                    </button>
                                </div>
                                <button
                                    onClick={() => sendQuery()}
                                    disabled={loading || !query.trim()}
                                    className={cn(
                                        "p-2 rounded-lg transition-all",
                                        query.trim() && !loading
                                            ? "bg-white text-zinc-950 hover:bg-zinc-200"
                                            : "text-zinc-600 border border-zinc-800"
                                    )}
                                >
                                    {loading
                                        ? <Loader2 className="w-4 h-4 animate-spin" />
                                        : <ArrowUpIcon className="w-4 h-4" />
                                    }
                                    <span className="sr-only">Send</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    )
}

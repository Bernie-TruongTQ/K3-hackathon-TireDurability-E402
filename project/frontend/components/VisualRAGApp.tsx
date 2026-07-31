"use client"

import { FormEvent, useMemo, useState } from "react"
import { BookOpen, FileText, Image as ImageIcon, Loader2, Send, ShieldCheck, Upload } from "lucide-react"

// Use the Next.js same-origin proxy by default. This avoids browser CORS,
// mixed-content and "localhost points to the client device" failures.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "/backend"

type Source = {
  source_id?: string
  page: number
  filename: string
  content_preview: string
  region_type?: string
  image_path?: string
  score?: number
}

type Message = {
  role: "user" | "assistant"
  content: string
  route?: string
  isMock?: boolean
  traceId?: string
  sources?: Source[]
}

export default function VisualRAGApp() {
  const [file, setFile] = useState<File | null>(null)
  const [documentId, setDocumentId] = useState("")
  const [documentName, setDocumentName] = useState("")
  const [provider, setProvider] = useState("openai")
  const [query, setQuery] = useState("")
  const [selectedSourceId, setSelectedSourceId] = useState("")
  const [selectedPage, setSelectedPage] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [uploading, setUploading] = useState(false)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState("")

  const ready = useMemo(() => Boolean(documentId), [documentId])

  async function uploadDocument() {
    if (!file) return
    setError("")
    setUploading(true)
    try {
      const form = new FormData()
      form.append("file", file)
      const response = await fetch(`${API_BASE}/api/v1/index/upload`, {
        method: "POST",
        body: form,
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || "Không thể index tài liệu")
      setDocumentId(payload.document_id)
      setDocumentName(file.name)
      setMessages([])
      setSelectedSourceId("")
      setSelectedPage(null)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Upload thất bại")
    } finally {
      setUploading(false)
    }
  }

  async function ask(event: FormEvent) {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed || !ready || asking) return
    setError("")
    setMessages((items) => [...items, { role: "user", content: trimmed }])
    setQuery("")
    setAsking(true)
    try {
      const response = await fetch(`${API_BASE}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: trimmed,
          document_id: documentId,
          llm_provider: provider,
          selected_page: selectedPage,
          selected_image_id: selectedSourceId || null,
        }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || "Không thể trả lời")
      setMessages((items) => [
        ...items,
        {
          role: "assistant",
          content: payload.answer,
          route: payload.route,
          isMock: payload.is_mock,
          traceId: payload.trace_id,
          sources: payload.sources,
        },
      ])
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Truy vấn thất bại")
    } finally {
      setAsking(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#f6f4ee] text-slate-950">
      <header className="border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-indigo-600 p-2 text-white"><BookOpen size={22} /></div>
            <div>
              <h1 className="text-lg font-semibold">VLearn VisualRAG</h1>
              <p className="text-xs text-slate-500">Hiểu cả chữ, bảng, công thức và hình trong slide PDF</p>
            </div>
          </div>
          <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-800">
            <ShieldCheck size={14} /> Chỉ trả lời từ nguồn đã nạp
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-6xl gap-5 px-5 py-6 lg:grid-cols-[320px_1fr]">
        <aside className="h-fit rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="font-semibold">1. Nạp tài liệu</h2>
          <p className="mt-1 text-sm text-slate-500">PDF/ảnh dùng DeepSeek-OCR. Markdown dùng cho demo nhanh.</p>
          <label className="mt-4 flex cursor-pointer flex-col items-center rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-7 text-center hover:border-indigo-400">
            <Upload className="mb-2 text-indigo-600" />
            <span className="text-sm font-medium">{file ? file.name : "Chọn PDF, ảnh hoặc Markdown"}</span>
            <input
              className="hidden"
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.webp,.md,.json"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
          </label>
          <button
            onClick={uploadDocument}
            disabled={!file || uploading}
            className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
          >
            {uploading ? <Loader2 className="animate-spin" size={17} /> : <FileText size={17} />}
            {uploading ? "Đang xử lý…" : "Trích xuất & index"}
          </button>

          <div className="mt-6 border-t border-slate-100 pt-5">
            <label className="text-sm font-semibold">2. Provider</label>
            <select
              value={provider}
              onChange={(event) => setProvider(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
            >
              <option value="demo">Demo extractive — mock có nhãn</option>
              <option value="openai">OpenAI GPT-4o mini — AI/VLM thật</option>
              <option value="gemini">Gemini — AI/VLM thật</option>
              <option value="qwen">Qwen local — AI text thật</option>
            </select>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              CP6 phải chọn provider thật và giữ trace ID. Demo provider chỉ dùng để kiểm tra UI.
            </p>
          </div>

          {ready && (
            <div className="mt-5 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-900">
              <div className="font-semibold">Đã sẵn sàng</div>
              <div className="mt-1 truncate">{documentName}</div>
              <div className="mt-1 font-mono text-[10px] text-emerald-700">{documentId}</div>
            </div>
          )}
        </aside>

        <section className="flex min-h-[72vh] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 px-5 py-4">
            <h2 className="font-semibold">Hỏi tài liệu</h2>
            <p className="text-sm text-slate-500">
              Câu trả lời cho biết route text/visual và hiển thị nguồn để kiểm chứng.
            </p>
            {selectedSourceId && (
              <button
                type="button"
                onClick={() => {
                  setSelectedSourceId("")
                  setSelectedPage(null)
                }}
                className="mt-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700"
              >
                Đang khóa một nguồn ở trang {selectedPage} · bấm để bỏ chọn
              </button>
            )}
          </div>

          <div className="flex-1 space-y-5 overflow-y-auto p-5">
            {messages.length === 0 && (
              <div className="mx-auto mt-20 max-w-md text-center text-slate-500">
                <ImageIcon className="mx-auto mb-3 text-indigo-500" size={34} />
                <p className="font-medium text-slate-700">
                  {ready ? "Hãy hỏi về một đoạn chữ, hình, bảng hoặc công thức." : "Nạp một tài liệu để bắt đầu."}
                </p>
                <p className="mt-2 text-sm">Thử: “Giải thích biểu đồ này và cho tôi xem nguồn.”</p>
              </div>
            )}
            {messages.map((message, index) => (
              <article key={index} className={message.role === "user" ? "ml-auto max-w-xl" : "max-w-2xl"}>
                <div
                  className={
                    message.role === "user"
                      ? "rounded-2xl rounded-br-md bg-slate-900 px-4 py-3 text-sm text-white"
                      : "rounded-2xl rounded-bl-md bg-slate-100 px-4 py-3 text-sm leading-6"
                  }
                >
                  {message.isMock && (
                    <div className="mb-2 font-semibold text-amber-700">MOCK — chưa tính là lời gọi AI thật</div>
                  )}
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  {message.route && (
                    <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                      <span className="rounded-full bg-indigo-100 px-2 py-0.5 font-medium text-indigo-800">
                        route: {message.route}
                      </span>
                      {message.traceId && <span className="font-mono text-slate-500">trace: {message.traceId}</span>}
                    </div>
                  )}
                </div>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 grid gap-2 sm:grid-cols-2">
                    {message.sources.map((source) => (
                      <button
                        type="button"
                        key={source.source_id}
                        onClick={() => {
                          setSelectedSourceId(source.source_id || "")
                          setSelectedPage(source.page)
                        }}
                        className={
                          selectedSourceId === source.source_id
                            ? "rounded-xl border-2 border-indigo-500 bg-indigo-50 p-3 text-left text-xs"
                            : "rounded-xl border border-slate-200 p-3 text-left text-xs hover:border-indigo-300"
                        }
                      >
                        <div className="font-semibold">{source.filename} · trang {source.page}</div>
                        <div className="mt-1 text-slate-500">{source.region_type || "text"}</div>
                        <p className="mt-2 line-clamp-3 text-slate-600">{source.content_preview}</p>
                        {source.image_path && (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={`${API_BASE}${source.image_path}`}
                            alt={`Nguồn trực quan trang ${source.page}`}
                            className="mt-2 max-h-36 w-full rounded-lg object-contain bg-slate-50"
                          />
                        )}
                        <div className="mt-2 font-medium text-indigo-700">
                          {selectedSourceId === source.source_id ? "Nguồn đang được khóa" : "Chọn nguồn này để hỏi lại"}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </article>
            ))}
            {asking && <Loader2 className="animate-spin text-indigo-600" />}
          </div>

          <form onSubmit={ask} className="border-t border-slate-100 p-4">
            {error && <div className="mb-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}
            <div className="flex gap-2">
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                disabled={!ready || asking}
                placeholder={ready ? "Hỏi về tài liệu…" : "Nạp tài liệu trước"}
                className="min-w-0 flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-indigo-500"
              />
              <button
                disabled={!ready || !query.trim() || asking}
                className="rounded-xl bg-indigo-600 px-4 text-white disabled:opacity-40"
                aria-label="Gửi câu hỏi"
              >
                <Send size={19} />
              </button>
            </div>
          </form>
        </section>
      </div>
    </main>
  )
}

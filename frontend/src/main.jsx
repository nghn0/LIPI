import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowUpRight,
  ArrowRight,
  ArrowClockwise,
  ArrowLeft,
  PencilSimpleLine,
  Notebook,
  ChartBar,
  Cpu,
  ArrowDown,
  DownloadSimple,
  Copy,
  Check,
  Plus,
  Trash,
  FileText,
  X,
  Translate,
  Sparkle,
  ShieldCheck,
  CaretDown,
  Command,
  Info,
  CircleNotch,
  WarningCircle,
  BookOpen,
  SlidersHorizontal,
  GithubLogo,
  CheckCircle,
} from "@phosphor-icons/react";
import "@fontsource-variable/manrope";
import "@fontsource/noto-sans-devanagari/400.css";
import "@fontsource/noto-sans-devanagari/500.css";
import "./styles.css";

async function api(path, body) {
  const response = await fetch("/api/" + path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    let data;
    try {
      data = await response.json();
    } catch {}
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : `Request failed (${response.status}). Please try again.`,
    );
  }
  return response.json();
}
function readStorage(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
}
function download(name, text, type = "text/plain") {
  const u = URL.createObjectURL(
    new Blob([text], { type: type + ";charset=utf-8" }),
  );
  const a = document.createElement("a");
  a.href = u;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(u), 1000);
}
const SAMPLE =
  "Namaste! Mujhe kal ki meeting ke liye apne project ki report taiyaar karni hai.";
const NAV = [
  ["write", PencilSimpleLine, "Writing studio"],
  ["drafts", Notebook, "My drafts"],
  ["evaluation", ChartBar, "Evaluation lab"],
  ["models", Cpu, "Models & project"],
];

function App() {
  const [page, setPage] = useState("write");
  const [input, setInput] = useState(() => readStorage("lipi-input", SAMPLE));
  const [preserve, setPreserve] = useState(true);
  const [result, setResult] = useState(null);
  const [selection, setSelection] = useState(null);
  const [generation, setGeneration] = useState(null);
  const [tone, setTone] = useState("natural");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [health, setHealth] = useState(null);
  const [examples, setExamples] = useState([]);
  const [drafts, setDrafts] = useState(() => readStorage("lipi-drafts", []));
  const [report, setReport] = useState(null);
  const [toast, setToast] = useState("");
  const [deleteId, setDeleteId] = useState(null);
  const [outputMode, setOutputMode] = useState("tokens");
  const [edited, setEdited] = useState("");
  const inputRef = useRef(null);
  const tokenRefs = useRef({});
  const fileRef = useRef(null);
  const output =
    outputMode === "edit"
      ? edited
      : result?.tokens.map((t) => t.text).join("") || "";
  const words = input.trim() ? input.trim().split(/\s+/).length : 0;
  const current =
    result?.input === input && result?.preserve_english === preserve;
  useEffect(() => {
    api("health")
      .then(setHealth)
      .catch(() =>
        setError(
          "The local backend is not connected. Run ./start.sh, then refresh.",
        ),
      );
    api("examples")
      .then(setExamples)
      .catch(() => {});
    api("evaluation")
      .then(setReport)
      .catch(() => {});
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem("lipi-input", JSON.stringify(input));
    } catch {}
  }, [input]);
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(""), 2800);
      return () => clearTimeout(t);
    }
  }, [toast]);
  useEffect(() => {
    if (selection === null) return;
    const close = (e) => {
      if (e.key === "Escape") closeSelection(selection);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [selection]);
  function closeSelection(index) {
    setSelection(null);
    requestAnimationFrame(() => tokenRefs.current[index]?.focus());
  }
  function notify(message) {
    setToast(message);
  }
  function changeInput(value) {
    setInput(value);
    setSelection(null);
    setGeneration(null);
    setError("");
  }
  async function convert() {
    if (!input.trim() || busy) return;
    setBusy("convert");
    setError("");
    setSelection(null);
    setGeneration(null);
    try {
      const data = await api("transliterate", {
        text: input,
        preserve_english: preserve,
      });
      setResult(data);
      setOutputMode("tokens");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }
  useEffect(() => {
    const key = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && page === "write") {
        e.preventDefault();
        convert();
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [input, preserve, busy, page]);
  async function generate(task) {
    if (!output || busy || !current) return;
    setBusy(task);
    setSelection(null);
    setError("");
    try {
      setGeneration(await api("generate", { text: output, task, tone }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }
  function save() {
    if (!output || !current) return;
    const draft = {
      id: Date.now().toString(),
      input,
      output,
      generation,
      preserve,
      date: new Date().toISOString(),
    };
    const next = [draft, ...drafts].slice(0, 100);
    try {
      localStorage.setItem("lipi-drafts", JSON.stringify(next));
      setDrafts(next);
      notify("Draft saved on this device");
    } catch {
      setError("Your browser storage is full. Export this draft instead.");
    }
  }
  function removeDraft(id) {
    const next = drafts.filter((d) => d.id !== id);
    try {
      localStorage.setItem("lipi-drafts", JSON.stringify(next));
      setDrafts(next);
      setDeleteId(null);
    } catch {
      setError("Could not update browser storage.");
    }
  }
  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text);
      notify("Copied to clipboard");
    } catch {
      setError("Clipboard is unavailable. Select the text and copy manually.");
    }
  }
  async function runEvaluation() {
    setBusy("evaluation");
    setError("");
    try {
      setReport(await api("evaluation/run", {}));
      notify("Evaluation complete — results saved");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }
  async function importFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 30000) {
      setError("Choose a text file smaller than 30 KB.");
      return;
    }
    const text = await file.text();
    if (text.length > 3000) {
      setError(
        "Your text is longer than 3,000 characters. Import a shorter passage.",
      );
    } else {
      changeInput(text);
      setPage("write");
      inputRef.current?.focus();
    }
    e.target.value = "";
  }
  const title = NAV.find((n) => n[0] === page)?.[2];
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          href="#"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            setPage("write");
          }}
          aria-label="Lipi home"
        >
          <span className="brand-symbol" lang="hi">
            लि
          </span>
          <span>
            lipi<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="workspace-label">YOUR WRITING SPACE</div>
        <nav aria-label="Main navigation">
          {NAV.map(([id, Icon, label]) => (
            <button
              key={id}
              disabled={!!busy}
              aria-label={label}
              title={label}
              className={"nav-link " + (page === id ? "active" : "")}
              aria-current={page === id ? "page" : undefined}
              onClick={() => {
                setPage(id);
                setError("");
                setSelection(null);
              }}
            >
              <Icon size={19} weight={page === id ? "fill" : "regular"} />
              <span>{label}</span>
              {id === "drafts" && drafts.length > 0 && (
                <span className="count">{drafts.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <div className="note-mark" lang="hi">
            अ
          </div>
          <p>
            Think in Hinglish.
            <br />
            Make it your own.
          </p>
          <span>Small words. Wider possibilities.</span>
        </div>
        <div className="sidebar-bottom">
          <div className="local-status">
            <span
              className={
                "status-dot " + (health?.transliteration.ready ? "" : "offline")
              }
            />
            {health?.transliteration.ready
              ? "Running on your device"
              : "Connecting to models"}
          </div>
          <div className="course-block">
            <span className="course-icon">
              <BookOpen size={19} />
            </span>
            <div>
              <strong>CS3235 Mini Project</strong>
              <span>AI4Bharat × BharatGen</span>
            </div>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{title}</strong>
          </div>
          <div className="topbar-right">
            <span className="privacy">
              <ShieldCheck size={16} />
              Private by design
            </span>
            <span className="avatar" title="Local workspace">
              L
            </span>
          </div>
        </header>
        <main>
          {page === "write" && (
            <>
              <section className="intro">
                <div>
                  <h1>
                    Your words.
                    <br />
                    <span>In your script.</span>
                  </h1>
                  <p>
                    A little Hinglish, a little help.
                    <br className="mobile-break" /> Write naturally. Let Lipi
                    bring it to Hindi.
                  </p>
                </div>
                <div className="type-art" aria-hidden="true">
                  <span className="roman-art">a</span>
                  <span className="art-line" />
                  <span className="hindi-art" lang="hi">
                    अ
                  </span>
                  <small>THOUGHTS, WITHOUT TRANSLATION.</small>
                </div>
              </section>
              <section className="studio" aria-label="Hinglish writing editor">
                <div className="studio-toolbar">
                  <div className="language-path">
                    <span className="language-dot">Aa</span>
                    <strong>Hinglish</strong>
                    <ArrowRight size={17} />
                    <span className="language-dot hindi" lang="hi">
                      अ
                    </span>
                    <strong>Hindi</strong>
                    <span className="script-label">देवनागरी</span>
                  </div>
                  <label className="toggle-label">
                    <span>Keep English words</span>
                    <input
                      type="checkbox"
                      checked={preserve}
                      onChange={(e) => {
                        setPreserve(e.target.checked);
                        setGeneration(null);
                        setSelection(null);
                      }}
                      disabled={!!busy}
                    />
                    <span className="toggle-track" />
                  </label>
                </div>
                <div className="editor-grid">
                  <div className="input-panel">
                    <div className="panel-heading">
                      <span>YOUR HINGLISH</span>
                      <button
                        className="icon-button"
                        title="Clear input"
                        aria-label="Clear input"
                        onClick={() => {
                          changeInput("");
                          setResult(null);
                          inputRef.current?.focus();
                        }}
                        disabled={!input || !!busy}
                      >
                        <Trash size={17} />
                      </button>
                    </div>
                    <label className="sr-only" htmlFor="hinglish-input">
                      Write your Hinglish message
                    </label>
                    <textarea
                      id="hinglish-input"
                      ref={inputRef}
                      className="source-editor"
                      value={input}
                      maxLength={3000}
                      onChange={(e) => changeInput(e.target.value)}
                      placeholder="Jaise aap bolte hain, waise hi likhiye…"
                      spellCheck="false"
                      disabled={!!busy}
                    />
                    <div className="panel-footer">
                      <span>
                        {words} {words === 1 ? "word" : "words"}
                        <span className="separator">·</span>
                        {input.length.toLocaleString()} / 3,000
                      </span>
                      <button
                        className="text-button"
                        onClick={() => fileRef.current.click()}
                        disabled={!!busy}
                      >
                        <FileText size={15} />
                        Import .txt
                      </button>
                      <input
                        ref={fileRef}
                        type="file"
                        accept=".txt,text/plain"
                        hidden
                        onChange={importFile}
                      />
                    </div>
                  </div>
                  <div
                    className={
                      "output-panel " + (!current ? "not-current" : "")
                    }
                  >
                    <div className="panel-heading">
                      <span>YOUR HINDI</span>
                      <div className="panel-tools">
                        {current && (
                          <button
                            className="text-button"
                            onClick={() => {
                              if (outputMode === "tokens") {
                                setEdited(output);
                                setOutputMode("edit");
                              } else {
                                setResult({
                                  ...result,
                                  tokens: [
                                    {
                                      source: edited,
                                      text: edited,
                                      alternatives: [edited],
                                      kind: "literal",
                                    },
                                  ],
                                });
                                setOutputMode("tokens");
                              }
                            }}
                            disabled={!!busy}
                          >
                            {outputMode === "edit"
                              ? "Done editing"
                              : "Edit text"}
                          </button>
                        )}
                        <span className="small-badge">देवनागरी</span>
                      </div>
                    </div>
                    {busy === "convert" ? (
                      <div className="output-loading" aria-live="polite">
                        <div className="skeleton-line" />
                        <div className="skeleton-line" />
                        <div className="skeleton-line short" />
                        <p>Finding the right words…</p>
                      </div>
                    ) : current ? (
                      outputMode === "edit" ? (
                        <textarea
                          aria-label="Edit Hindi output"
                          lang="hi"
                          className="hindi-editor"
                          disabled={!!busy}
                          value={edited}
                          onChange={(e) => {
                            setEdited(e.target.value);
                            setGeneration(null);
                          }}
                          maxLength={6000}
                        />
                      ) : (
                        <div className="token-output" lang="hi">
                          {result.tokens.map((token, i) =>
                            token.kind === "converted" ? (
                              <span className="token-wrap" key={i}>
                                <button
                                  ref={(node) => {
                                    tokenRefs.current[i] = node;
                                  }}
                                  disabled={!!busy}
                                  className={
                                    "word-token " +
                                    (selection === i ? "selected" : "")
                                  }
                                  onClick={() =>
                                    setSelection(selection === i ? null : i)
                                  }
                                  aria-label={`Alternatives for ${token.text}`}
                                  aria-expanded={selection === i}
                                >
                                  {token.text}
                                </button>
                                {selection === i && (
                                  <div
                                    className="alternatives"
                                    role="group"
                                    aria-label={"Spellings for " + token.source}
                                  >
                                    <div className="alternative-title">
                                      <span>{token.source}</span>
                                      <button
                                        className="icon-button"
                                        aria-label="Close spellings"
                                        onClick={() => closeSelection(i)}
                                      >
                                        <X size={13} />
                                      </button>
                                    </div>
                                    {token.alternatives.map((a) => (
                                      <button
                                        key={a}
                                        className={
                                          token.text === a ? "chosen" : ""
                                        }
                                        onClick={() => {
                                          const tokens = result.tokens.map(
                                            (t, n) =>
                                              n === i ? { ...t, text: a } : t,
                                          );
                                          setResult({ ...result, tokens });
                                          closeSelection(i);
                                          setGeneration(null);
                                        }}
                                      >
                                        {a}
                                        {token.text === a && (
                                          <Check size={15} />
                                        )}
                                      </button>
                                    ))}
                                  </div>
                                )}
                              </span>
                            ) : (
                              <span
                                key={i}
                                className={
                                  token.kind === "english"
                                    ? "preserved-word"
                                    : ""
                                }
                              >
                                {token.text}
                              </span>
                            ),
                          )}
                        </div>
                      )
                    ) : (
                      <div className="output-empty">
                        <span className="empty-script" lang="hi">
                          क ख ग
                        </span>
                        <p>
                          {result
                            ? "Your message has changed."
                            : "A new script. The same you."}
                        </p>
                        <span>
                          {result
                            ? "Convert again to update your Hindi."
                            : "Your Hindi will appear here when you convert."}
                        </span>
                      </div>
                    )}
                    <div className="panel-footer">
                      <span>
                        {current ? (
                          <>
                            <span className="status-dot" />
                            {result.converted_words} words converted
                          </>
                        ) : (
                          "Made for the way you write"
                        )}
                      </span>
                      <div>
                        <button
                          className="icon-button"
                          aria-label="Copy Hindi output"
                          title="Copy Hindi"
                          disabled={!current || !output}
                          onClick={() => copy(output)}
                        >
                          <Copy size={17} />
                        </button>
                        <button
                          className="icon-button"
                          aria-label="Download Hindi output"
                          title="Download Hindi"
                          disabled={!current || !output}
                          onClick={() => download("lipi-hindi.txt", output)}
                        >
                          <DownloadSimple size={17} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="action-bar">
                  <div className="model-caption">
                    <span className="model-orbit">
                      <Cpu size={18} />
                    </span>
                    <span>
                      Powered by <strong>IndicXlit</strong>
                      <small>
                        {current
                          ? `${result.latency_ms} ms · processed locally`
                          : "AI4Bharat’s multilingual transliteration model"}
                      </small>
                    </span>
                  </div>
                  <button
                    className="primary-button"
                    onClick={convert}
                    disabled={!input.trim() || !!busy}
                  >
                    {busy === "convert" ? "Converting…" : "Convert to Hindi"}
                    {busy === "convert" ? (
                      <CircleNotch className="spin" size={18} />
                    ) : (
                      <ArrowRight size={18} />
                    )}
                    <kbd>⌘ ↵</kbd>
                  </button>
                </div>
              </section>
              <div className="example-strip">
                <span>Need a starting point?</span>
                {examples.map((example) => (
                  <button
                    key={example.id}
                    onClick={() => {
                      changeInput(example.text);
                      inputRef.current?.focus();
                    }}
                    disabled={!!busy}
                  >
                    {example.title}
                    <ArrowUpRight size={14} />
                  </button>
                ))}
              </div>
              {error && (
                <div className="error-banner" role="alert">
                  <WarningCircle size={20} />
                  <span>{error}</span>
                  <button
                    className="icon-button"
                    aria-label="Dismiss error"
                    onClick={() => setError("")}
                  >
                    <X size={17} />
                  </button>
                </div>
              )}
              <section className="refine-section">
                <div className="refine-heading">
                  <div>
                    <h2>A finishing touch.</h2>
                    <p>Keep your meaning. Find just the right words.</p>
                  </div>
                  <span
                    className={
                      "model-pill " + (!health?.generation.ready ? "muted" : "")
                    }
                  >
                    <span className="status-dot" />
                    {health?.generation.ready
                      ? "BharatGen Param ready"
                      : "BharatGen Param · checking availability"}
                  </span>
                </div>
                <div className="refine-tools">
                  <div className="tone-control">
                    <label htmlFor="tone">Writing tone</label>
                    <select
                      id="tone"
                      value={tone}
                      onChange={(e) => setTone(e.target.value)}
                      disabled={!!busy}
                    >
                      <option value="natural">Natural</option>
                      <option value="formal">Formal</option>
                      <option value="friendly">Friendly</option>
                    </select>
                  </div>
                  <button
                    className="secondary-button"
                    onClick={() => generate("polish")}
                    disabled={
                      !current || !output || !!busy || !health?.generation.ready
                    }
                  >
                    <Sparkle size={18} />
                    {busy === "polish"
                      ? "Refining your words…"
                      : "Polish Hindi"}
                  </button>
                  <button
                    className="secondary-button"
                    onClick={() => generate("translate")}
                    disabled={
                      !current || !output || !!busy || !health?.generation.ready
                    }
                  >
                    <Translate size={18} />
                    {busy === "translate"
                      ? "Translating…"
                      : "Translate to English"}
                  </button>
                  <button
                    className="save-button"
                    onClick={save}
                    disabled={!current || !output || !!busy}
                  >
                    <Notebook size={18} />
                    Save draft
                  </button>
                </div>
                {busy && busy !== "convert" && busy !== "evaluation" && (
                  <div className="generation-loading" role="status">
                    <div className="skeleton-line" />
                    <div className="skeleton-line short" />
                    <p>
                      Param is working locally. The first request may take a
                      moment.
                    </p>
                  </div>
                )}
                {generation && (
                  <div className="generated-result">
                    <div className="generated-header">
                      <span>
                        <Sparkle size={16} />
                        {generation.task === "polish"
                          ? "Refined Hindi"
                          : "English translation"}
                      </span>
                      <div>
                        <button
                          className="icon-button"
                          aria-label="Copy generated text"
                          onClick={() => copy(generation.output)}
                        >
                          <Copy size={17} />
                        </button>
                        <button
                          className="icon-button"
                          aria-label="Download generated text"
                          onClick={() =>
                            download(
                              `lipi-${generation.task}.txt`,
                              generation.output,
                            )
                          }
                        >
                          <DownloadSimple size={17} />
                        </button>
                      </div>
                    </div>
                    <p lang={generation.task === "polish" ? "hi" : "en"}>
                      {generation.output}
                    </p>
                    <div className="generation-note">
                      <Info size={14} />
                      {generation.review_note}
                      <span>{(generation.latency_ms / 1000).toFixed(1)}s</span>
                    </div>
                  </div>
                )}
                {!health?.generation.ready && (
                  <p className="setup-hint">
                    The writing model is not connected yet.{" "}
                    <button onClick={() => setPage("models")}>
                      View model setup <ArrowUpRight size={12} />
                    </button>
                  </p>
                )}
              </section>
              <footer className="studio-footer">
                <span>
                  <ShieldCheck size={15} />
                  Your writing stays on this device.
                </span>
                <span>
                  Built with Indian-language AI. Built for your voice.
                </span>
              </footer>
            </>
          )}
          {page === "drafts" && (
            <>
              <div className="page-heading">
                <div>
                  <h1>
                    A space for
                    <br />
                    <span>your words.</span>
                  </h1>
                  <p>Your saved writing, right where you left it.</p>
                </div>
                <button
                  className="primary-button"
                  onClick={() => {
                    changeInput("");
                    setResult(null);
                    setPage("write");
                  }}
                >
                  <Plus size={18} />
                  New draft
                </button>
              </div>
              <p className="section-meta">
                {drafts.length} saved {drafts.length === 1 ? "draft" : "drafts"}{" "}
                · Stored in this browser
              </p>
              {drafts.length === 0 ? (
                <div className="large-empty">
                  <Notebook size={42} weight="thin" />
                  <h2>Your next thought belongs here.</h2>
                  <p>
                    Convert a message in the studio, then save it as a draft.
                  </p>
                  <button
                    className="secondary-button"
                    onClick={() => setPage("write")}
                  >
                    Open writing studio
                    <ArrowRight size={17} />
                  </button>
                </div>
              ) : (
                <div className="draft-list">
                  {drafts.map((d) => (
                    <article className="draft" key={d.id}>
                      <div className="draft-top">
                        <span>
                          {new Date(d.date).toLocaleDateString("en-IN", {
                            day: "numeric",
                            month: "short",
                            year: "numeric",
                          })}
                        </span>
                        <div>
                          <button
                            className="icon-button"
                            aria-label="Download draft"
                            onClick={() =>
                              download(
                                "lipi-draft.txt",
                                d.input +
                                  "\n\n" +
                                  d.output +
                                  (d.generation
                                    ? "\n\n" + d.generation.output
                                    : ""),
                              )
                            }
                          >
                            <DownloadSimple size={18} />
                          </button>
                          <button
                            className="icon-button"
                            aria-label="Delete draft"
                            onClick={() => setDeleteId(d.id)}
                          >
                            <Trash size={18} />
                          </button>
                        </div>
                      </div>
                      <p lang="hi" className="draft-hindi">
                        {d.output}
                      </p>
                      <p className="draft-source">{d.input}</p>
                      <div className="draft-bottom">
                        <button
                          className="text-button"
                          onClick={() => {
                            setInput(d.input);
                            setPreserve(d.preserve);
                            setResult({
                              input: d.input,
                              preserve_english: d.preserve,
                              tokens: [
                                {
                                  source: d.output,
                                  text: d.output,
                                  alternatives: [d.output],
                                  kind: "literal",
                                },
                              ],
                              converted_words: d.output.split(/\s+/).length,
                              latency_ms: 0,
                            });
                            setEdited(d.output);
                            setOutputMode("edit");
                            setGeneration(d.generation);
                            setPage("write");
                          }}
                        >
                          Continue writing
                          <ArrowUpRight size={16} />
                        </button>
                        {deleteId === d.id && (
                          <div className="confirm-delete">
                            <span>Delete this draft?</span>
                            <button onClick={() => removeDraft(d.id)}>
                              Delete
                            </button>
                            <button onClick={() => setDeleteId(null)}>
                              Keep
                            </button>
                          </div>
                        )}
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </>
          )}
          {page === "evaluation" && (
            <>
              <div className="page-heading">
                <div>
                  <h1>
                    Good AI.
                    <br />
                    <span>Measured honestly.</span>
                  </h1>
                  <p>
                    40 real-world test cases. Every result, including the
                    misses.
                  </p>
                </div>
                <button
                  className="primary-button"
                  onClick={runEvaluation}
                  disabled={!!busy}
                >
                  <ArrowClockwise
                    size={18}
                    className={busy === "evaluation" ? "spin" : ""}
                  />
                  {busy === "evaluation"
                    ? "Running 40 cases…"
                    : "Run evaluation"}
                </button>
              </div>
              {error && (
                <div className="error-banner" role="alert">
                  {error}
                </div>
              )}
              {report && !report.not_run ? (
                <>
                  <div className="metrics">
                    <div>
                      <span>Character error rate</span>
                      <strong>
                        {(report.cer * 100).toFixed(1)}
                        <small>%</small>
                      </strong>
                      <p>Lower is better</p>
                    </div>
                    <div>
                      <span>Word accuracy</span>
                      <strong>
                        {(report.word_accuracy * 100).toFixed(1)}
                        <small>%</small>
                      </strong>
                      <p>1 − word error rate, floored at zero</p>
                    </div>
                    <div>
                      <span>Exact sentence match</span>
                      <strong>
                        {report.exact_matches}
                        <small> / {report.test_count}</small>
                      </strong>
                      <p>After NFC + whitespace normalization</p>
                    </div>
                    <div>
                      <span>Evaluation time</span>
                      <strong>
                        {report.duration_s}
                        <small>s</small>
                      </strong>
                      <p>Cache state affects timing</p>
                    </div>
                  </div>
                  <div className="report-head">
                    <div>
                      <h2>Test bench</h2>
                      <p>{report.model}</p>
                    </div>
                    <button
                      className="secondary-button"
                      onClick={() =>
                        download(
                          "lipi-evaluation.json",
                          JSON.stringify(report, null, 2),
                          "application/json",
                        )
                      }
                    >
                      <DownloadSimple size={16} />
                      Export results
                    </button>
                  </div>
                  <div className="category-strip">
                    {report.categories.map((c) => (
                      <div key={c.name}>
                        <span>{c.name}</span>
                        <strong>
                          {c.passed}/{c.count}
                        </strong>
                      </div>
                    ))}
                  </div>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>CASE</th>
                          <th>INPUT / EXPECTED</th>
                          <th>MODEL OUTPUT</th>
                          <th>CER</th>
                          <th>RESULT</th>
                        </tr>
                      </thead>
                      <tbody>
                        {report.results.map((r) => (
                          <tr key={r.id}>
                            <td>
                              {r.id}
                              <small>{r.category}</small>
                            </td>
                            <td>
                              <span>{r.input}</span>
                              <small lang="hi">{r.expected}</small>
                            </td>
                            <td lang="hi">{r.actual}</td>
                            <td>{(r.cer * 100).toFixed(1)}%</td>
                            <td>
                              <span
                                className={
                                  "result-badge " +
                                  (r.exact ? "passed" : "review")
                                }
                              >
                                {r.exact ? "Match" : "Review"}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <section className="analysis">
                    <h2>What the misses teach us</h2>
                    {report.failure_analysis.map((f) => (
                      <article key={f.type}>
                        <h3>{f.type}</h3>
                        <p>{f.cause}</p>
                        <p>
                          <strong>What we do:</strong> {f.mitigation}
                        </p>
                        <p>
                          <strong>Next experiment:</strong> {f.next_step}
                        </p>
                      </article>
                    ))}
                    <h3>Reading these numbers</h3>
                    <ul>
                      {report.limitations.map((l) => (
                        <li key={l}>{l}</li>
                      ))}
                    </ul>
                    <p className="section-meta">
                      Last run:{" "}
                      {new Date(report.created_at).toLocaleString("en-IN")}
                    </p>
                  </section>
                </>
              ) : (
                <div className="large-empty">
                  <ChartBar size={42} />
                  <h2>Let the results speak.</h2>
                  <p>
                    Run the task-specific suite to measure this model on 40
                    examples.
                  </p>
                </div>
              )}
            </>
          )}
          {page === "models" && (
            <>
              <div className="page-heading">
                <div>
                  <h1>
                    Indian models.
                    <br />
                    <span>Local intelligence.</span>
                  </h1>
                  <p>
                    A look inside Lipi, from a Roman keystroke to your final
                    draft.
                  </p>
                </div>
                <button
                  className="secondary-button"
                  onClick={() =>
                    api("health")
                      .then(setHealth)
                      .then(() => notify("Model status refreshed"))
                      .catch(() => setError("Backend unavailable"))
                  }
                >
                  <ArrowClockwise size={17} />
                  Refresh status
                </button>
              </div>
              {error && (
                <div className="error-banner" role="alert">
                  {error}
                </div>
              )}
              <div className="pipeline-visual">
                <span>Hinglish input</span>
                <ArrowRight />
                <span>Token protection</span>
                <ArrowRight />
                <strong>IndicXlit</strong>
                <ArrowRight />
                <span>Hindi + alternatives</span>
                <ArrowRight />
                <strong>Param</strong>
              </div>
              <div className="model-details">
                <article>
                  <div className="model-detail-top">
                    <div className="model-icon">
                      <Translate size={26} />
                    </div>
                    <span
                      className={
                        "result-badge " +
                        (health?.transliteration.ready ? "passed" : "review")
                      }
                    >
                      {health?.transliteration.ready
                        ? "Ready"
                        : "Not connected"}
                    </span>
                  </div>
                  <h2>IndicXlit</h2>
                  <p className="model-author">AI4Bharat · IIT Madras</p>
                  <p>
                    A character-level encoder–decoder Transformer trained on
                    Aksharantar. Converts Roman spellings into native script,
                    with beam-search alternatives.
                  </p>
                  <dl>
                    <div>
                      <dt>Parameters</dt>
                      <dd>~11 million</dd>
                    </div>
                    <div>
                      <dt>Runtime</dt>
                      <dd>PyTorch · CPU</dd>
                    </div>
                    <div>
                      <dt>App language</dt>
                      <dd>Hindi / Devanagari</dd>
                    </div>
                    <div>
                      <dt>Weights license</dt>
                      <dd>MIT</dd>
                    </div>
                  </dl>
                  <a
                    href="https://github.com/AI4Bharat/IndicXlit"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Official model & paper
                    <ArrowUpRight size={16} />
                  </a>
                </article>
                <article>
                  <div className="model-detail-top">
                    <div className="model-icon">
                      <Sparkle size={26} />
                    </div>
                    <span
                      className={
                        "result-badge " +
                        (health?.generation.ready ? "passed" : "review")
                      }
                    >
                      {health?.generation.ready ? "Ready" : "Setup required"}
                    </span>
                  </div>
                  <h2>Param-1</h2>
                  <p className="model-author">BharatGen · 2.9B Instruct</p>
                  <p>
                    A Hindi–English instruction-tuned language model. Used to
                    improve phrasing and translate your final Hindi message into
                    English, entirely on this device.
                  </p>
                  <dl>
                    <div>
                      <dt>Quantization</dt>
                      <dd>Q4_K_M · community GGUF</dd>
                    </div>
                    <div>
                      <dt>Runtime</dt>
                      <dd>Ollama · Metal / CPU</dd>
                    </div>
                    <div>
                      <dt>Generation</dt>
                      <dd>Temperature 0 · 2,048 context</dd>
                    </div>
                    <div>
                      <dt>Model card license</dt>
                      <dd>Apache 2.0</dd>
                    </div>
                  </dl>
                  <a
                    href="https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Official model card
                    <ArrowUpRight size={16} />
                  </a>
                </article>
              </div>
              <section className="project-notes">
                <h2>Made for CS3235.</h2>
                <p>
                  This is project 4: Hinglish Smart Writing Assistant. The
                  working system combines pretrained neural transliteration, an
                  explicit code-switch policy, instruction prompting, and
                  task-specific evaluation.
                </p>
                <div className="project-note-grid">
                  <div>
                    <h3>Designed to be inspected</h3>
                    <p>
                      40 manually authored test cases cover everyday Hindi,
                      spelling variants, code-switching, named entities, and
                      protected content. The evaluation lab shows each input,
                      reference, prediction and error.
                    </p>
                  </div>
                  <div>
                    <h3>Your text, your device</h3>
                    <p>
                      Messages are processed by local models. Drafts use this
                      browser’s local storage. There is no account, analytics
                      service or external text API.
                    </p>
                  </div>
                </div>
                <h3>A deliberate model choice</h3>
                <p>
                  IndicTrans2’s official checkpoint requires Hugging Face access
                  acceptance. Lipi uses the available BharatGen Param checkpoint
                  for optional English translation, and labels its provenance.
                  IndicTrans2 is not claimed to be running.
                </p>
                <h3>One-command launch</h3>
                <pre>./start.sh</pre>
                <p>
                  If the writing model is missing, run{" "}
                  <code>python3 scripts/setup_param.py</code>. See the
                  repository README for model downloads, evaluation commands,
                  architecture, known limitations and the demo walkthrough.
                </p>
                <p className="setup-status">
                  <Info size={17} />
                  {health?.generation.message || "Checking local model server…"}
                </p>
              </section>
            </>
          )}
        </main>
      </div>
      {toast && (
        <div className="toast" role="status">
          <CheckCircle size={18} weight="fill" />
          {toast}
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);

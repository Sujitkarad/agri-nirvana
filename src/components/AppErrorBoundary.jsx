import React from "react";

export default class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Keep production telemetry privacy-safe: do not send user crop images or form data.
    if (import.meta.env.DEV) {
      console.error("Agri Nirvana UI error:", error, info);
    }
  }

  handleReload = () => window.location.reload();

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <main className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
        <div className="mx-auto max-w-xl rounded-3xl border border-emerald-500/20 bg-slate-900/90 p-8 text-center shadow-2xl">
          <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10 text-2xl" aria-hidden="true">
            🌱
          </div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-emerald-400">Agri Nirvana</p>
          <h1 className="text-2xl font-extrabold tracking-tight">The workspace needs a quick restart</h1>
          <p className="mt-3 text-sm leading-6 text-slate-400">
            Something unexpected happened in the interface. Your uploaded crop image is not included in this error screen.
          </p>
          <button
            type="button"
            onClick={this.handleReload}
            className="mt-6 min-h-11 rounded-xl bg-emerald-500 px-5 py-3 text-sm font-bold text-slate-950 shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          >
            Reload Agri Nirvana
          </button>
          {import.meta.env.DEV && this.state.error?.message ? (
            <details className="mt-5 text-left text-xs text-slate-500">
              <summary className="cursor-pointer">Developer error</summary>
              <pre className="mt-2 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3">{this.state.error.message}</pre>
            </details>
          ) : null}
        </div>
      </main>
    );
  }
}

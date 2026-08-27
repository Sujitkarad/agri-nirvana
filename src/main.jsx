import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Analytics } from "@vercel/analytics/react";
import "./index.css";
import App from "./App";
import AppErrorBoundary from "./components/AppErrorBoundary";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Agri Nirvana root element was not found.");
}

createRoot(rootElement).render(
  <StrictMode>
    <AppErrorBoundary>
      <App />
    </AppErrorBoundary>
    <Analytics />
  </StrictMode>,
);

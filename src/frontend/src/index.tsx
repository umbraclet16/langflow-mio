// Polyfills for Chrome 108 compatibility
// Promise.withResolvers - Chrome 119+
if (typeof Promise.withResolvers !== "function") {
  Promise.withResolvers = function () {
    let resolve!: (value: unknown) => void;
    let reject!: (reason?: unknown) => void;
    const promise = new Promise((res, rej) => {
      resolve = res as (value: unknown) => void;
      reject = rej;
    });
    return { promise, resolve, reject };
  };
}

// Array.prototype.toReversed - Chrome 110+
if (typeof Array.prototype.toReversed !== "function") {
  Array.prototype.toReversed = function () {
    return [...this].reverse();
  };
}

import "./i18n";
import i18n from "./i18n";
import { loadLanguage } from "./i18n";
import ReactDOM from "react-dom/client";
import reportWebVitals from "./reportWebVitals";

import "./style/classes.css";
// @ts-ignore
import "./style/index.css";
// @ts-ignore
import "./App.css";
import "./style/applies.css";

// @ts-ignore
import App from "./customization/custom-App";

// Map browser language codes to our supported codes.
// navigator.language returns BCP 47 tags (e.g. "zh-CN", "zh-Hans", "zh-TW").
// We support simplified Chinese under "zh-Hans".
function mapBrowserLang(lang: string): string | null {
  // Exact match
  if (["en", "fr", "es", "de", "pt", "ja", "zh-Hans"].includes(lang)) {
    return lang;
  }
  const base = lang.split("-")[0];
  if (base === "zh") return "zh-Hans";
  // Other languages we don't have translations for
  return null;
}

const detectedLang =
  localStorage.getItem("languagePreference") ||
  mapBrowserLang(navigator.language) ||
  "en";

loadLanguage(detectedLang).then(() => {
  // Apply the detected language — i18n.init() hardcodes lng:"en",
  // so loadLanguage alone only loads the bundle but doesn't switch.
  i18n.changeLanguage(detectedLang);

  const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement,
  );
  root.render(<App />);
  reportWebVitals();
});

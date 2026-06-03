CSS = """\
/* ========== CSS Variables ========== */
:root {
  --bg-page: #f5f2f0;
  --bg-card: #ffffff;
  --bg-code: #1e1e2e;
  --bg-table-alt: #f8f7f6;
  --bg-blockquote: #faf8f6;
  --bg-hover: #f0eeec;

  --text-primary: #2c2c2c;
  --text-secondary: #5a5a5a;
  --text-muted: #8a8a8a;
  --text-code: #cdd6f4;

  --accent: #4f6ef7;
  --accent-hover: #3b55d9;
  --border: #e6e2de;
  --border-light: #f0ece8;

  --radius: 10px;
  --radius-sm: 6px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 16px rgba(0,0,0,0.06), 0 2px 6px rgba(0,0,0,0.04);

  --font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --font-mono: "SF Mono", "Fira Code", "Cascadia Code", "JetBrains Mono", "Menlo", Consolas, monospace;
  --font-size: 16px;
  --line-height: 1.75;
  --content-width: 820px;
}

/* ========== Reset & Base ========== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
  font-size: var(--font-size);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-sans);
  color: var(--text-primary);
  background: var(--bg-page);
  line-height: var(--line-height);
  padding: 40px 20px 80px;
  min-height: 100vh;
}

/* ========== Main Container ========== */
.markdown-body {
  max-width: var(--content-width);
  margin: 0 auto;
  background: var(--bg-card);
  padding: 48px 56px;
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
}

/* ========== Typography ========== */
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  font-weight: 600;
  line-height: 1.35;
  color: var(--text-primary);
  margin-top: 1.8em;
  margin-bottom: 0.4em;
  scroll-margin-top: 20px;
}

.markdown-body h1 {
  font-size: 2em;
  margin-top: 0;
  margin-bottom: 0.6em;
  padding-bottom: 0.3em;
  border-bottom: 2px solid var(--border-light);
  letter-spacing: -0.02em;
}

.markdown-body h2 {
  font-size: 1.55em;
  padding-bottom: 0.25em;
  border-bottom: 1px solid var(--border-light);
}

.markdown-body h3 { font-size: 1.25em; }
.markdown-body h4 { font-size: 1.1em; }
.markdown-body h5 { font-size: 1em; }
.markdown-body h6 { font-size: 0.9em; color: var(--text-secondary); }

.markdown-body p {
  margin: 0.8em 0;
}

.markdown-body a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.15s;
}

.markdown-body a:hover {
  border-bottom-color: var(--accent);
}

.markdown-body strong {
  font-weight: 600;
}

.markdown-body em {
  font-style: italic;
}

/* ========== Lists ========== */
.markdown-body ul,
.markdown-body ol {
  margin: 0.6em 0;
  padding-left: 1.6em;
}

.markdown-body li {
  margin: 0.3em 0;
}

.markdown-body li > ul,
.markdown-body li > ol {
  margin: 0.2em 0;
}

/* ========== Task List ========== */
.markdown-body input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border: 2px solid var(--border);
  border-radius: 3px;
  margin-right: 8px;
  vertical-align: middle;
  cursor: default;
  position: relative;
  top: -1px;
  transition: background 0.15s, border-color 0.15s;
}

.markdown-body input[type="checkbox"]:checked {
  background: var(--accent);
  border-color: var(--accent);
}

.markdown-body input[type="checkbox"]:checked::after {
  content: "";
  position: absolute;
  left: 3px;
  top: 0px;
  width: 6px;
  height: 10px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.markdown-body li:has(input[type="checkbox"]) {
  list-style: none;
  margin-left: -1.6em;
}

/* ========== Blockquotes ========== */
.markdown-body blockquote {
  margin: 1em 0;
  padding: 12px 20px;
  background: var(--bg-blockquote);
  border-left: 4px solid var(--accent);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
}

.markdown-body blockquote p {
  margin: 0.4em 0;
}

.markdown-body blockquote p:first-child { margin-top: 0; }
.markdown-body blockquote p:last-child { margin-bottom: 0; }

/* ========== Code ========== */
.markdown-body code {
  font-family: var(--font-mono);
  font-size: 0.88em;
  background: var(--bg-page);
  padding: 2px 6px;
  border-radius: 4px;
  color: #e06c75;
}

.markdown-body pre {
  margin: 1em 0;
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.markdown-body pre code {
  font-size: 0.85em;
  background: none;
  color: var(--text-code);
  padding: 0;
}

/* Pygments highlighing overrides for Catppuccin Mocha-like theme */
.markdown-body pre {
  background: var(--bg-code) !important;
  padding: 18px 20px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.markdown-body pre code {
  background: transparent !important;
  padding: 0 !important;
}

/* Code scrollbar */
.markdown-body pre::-webkit-scrollbar {
  height: 6px;
}
.markdown-body pre::-webkit-scrollbar-track {
  background: transparent;
}
.markdown-body pre::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.15);
  border-radius: 3px;
}

/* ========== Tables ========== */
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 0.95em;
  overflow: hidden;
  border-radius: var(--radius-sm);
}

.markdown-body thead {
  background: var(--bg-page);
}

.markdown-body th {
  font-weight: 600;
  text-align: left;
  padding: 10px 14px;
  border-bottom: 2px solid var(--border);
  color: var(--text-secondary);
}

.markdown-body td {
  padding: 9px 14px;
  border-bottom: 1px solid var(--border-light);
}

.markdown-body tbody tr:last-child td {
  border-bottom: none;
}

.markdown-body tbody tr:hover {
  background: var(--bg-hover);
}

/* ========== Horizontal Rule ========== */
.markdown-body hr {
  border: none;
  height: 1px;
  background: var(--border-light);
  margin: 2em 0;
}

/* ========== Images ========== */
.markdown-body img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-sm);
  margin: 1em 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* ========== Table of Contents ========== */
.markdown-body .toc {
  background: var(--bg-page);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin: 0 0 2em;
  border: 1px solid var(--border-light);
}

.markdown-body .toc h2 {
  font-size: 1.1em;
  margin: 0 0 12px;
  padding: 0;
  border: none;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.markdown-body .toc ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.markdown-body .toc li {
  margin: 4px 0;
  padding: 0;
}

.markdown-body .toc a {
  color: var(--text-secondary);
  text-decoration: none;
  border: none;
  display: block;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}

.markdown-body .toc a:hover {
  background: var(--bg-hover);
  color: var(--accent);
}

/* ========== Footnotes ========== */
.markdown-body .footnote-ref {
  font-size: 0.8em;
  vertical-align: super;
  line-height: 1;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  body { padding: 16px 12px 60px; }
  .markdown-body { padding: 24px 20px; }
  .markdown-body h1 { font-size: 1.65em; }
  .markdown-body h2 { font-size: 1.3em; }
}
"""

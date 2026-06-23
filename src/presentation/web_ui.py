"""Local web UI for configuring and running the ontology pipeline."""

from __future__ import annotations

import html
import json
import multiprocessing as mp
import queue
import threading
import webbrowser
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import count
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

from host.llm_planner import PIPELINE_ACTIONS

PIPELINE_GOALS = list(PIPELINE_ACTIONS.keys())
REPO_ROOT = str(Path(__file__).resolve().parents[2]) + "/"


def _escape_attr(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _json_ready(value: Any) -> Any:
  if isinstance(value, Path):
    return str(value)
  if isinstance(value, dict):
    return {key: _json_ready(item) for key, item in value.items()}
  if isinstance(value, list):
    return [_json_ready(item) for item in value]
  return value


def _html_template(defaults: Dict[str, Any]) -> str:
    goal_options = "\n".join(
        (
            "<label class=\"goal-option\">"
            f"<input type=\"checkbox\" name=\"goals\" value=\"{_escape_attr(goal)}\""
            f" {'checked' if goal in defaults['goals'] else ''}>"
            f"<span>{html.escape(goal)}</span>"
            "</label>"
        )
        for goal in PIPELINE_GOALS
    )
    existing_ontologies = html.escape("\n".join(defaults["existing_ontologies"]))
    default_goal_count = len(defaults["goals"])
    existing_ontology_count = len(defaults["existing_ontologies"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Memory-Assisted Ontology Engineering</title>
  <link rel="icon" href="data:image/svg+xml,&lt;svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'&gt;&lt;rect width='64' height='64' rx='16' fill='%230f766e'/&gt;&lt;path d='M20 20h24v6H35v18h-6V26h-9z' fill='white'/&gt;&lt;/svg&gt;">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f4ede3;
      --panel: rgba(252, 248, 241, 0.88);
      --panel-strong: rgba(255, 252, 247, 0.98);
      --panel-soft: rgba(255, 255, 255, 0.68);
      --text: #1f2937;
      --muted: #5f6c76;
      --accent: #0f766e;
      --accent-strong: #134e4a;
      --accent-soft: #d8f0ea;
      --ember: #c56a1b;
      --ember-soft: #f4d6b8;
      --border: rgba(15, 118, 110, 0.16);
      --border-strong: rgba(19, 78, 74, 0.22);
      --shadow: 0 28px 80px rgba(59, 43, 24, 0.14);
      --danger: #b91c1c;
      --code: #163441;
      --mono: "IBM Plex Mono", Menlo, Monaco, Consolas, monospace;
      --sans: "Manrope", "Avenir Next", sans-serif;
      --serif: "Fraunces", Georgia, serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--sans);
      color: var(--text);
      background:
        radial-gradient(circle at 0% 0%, rgba(15, 118, 110, 0.18), transparent 24%),
        radial-gradient(circle at 100% 12%, rgba(197, 106, 27, 0.18), transparent 20%),
        radial-gradient(circle at 72% 100%, rgba(20, 184, 166, 0.12), transparent 22%),
        linear-gradient(145deg, #f7f0e6, #edf5f3 55%, #f5ebdd);
      min-height: 100vh;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
      background-size: 22px 22px;
      mask-image: linear-gradient(180deg, rgba(0,0,0,0.35), transparent 85%);
      opacity: 0.45;
    }}
    .shell {{
      width: min(1280px, calc(100vw - 32px));
      margin: 22px auto 28px;
      display: grid;
      grid-template-columns: minmax(340px, 500px) minmax(460px, 1fr);
      gap: 22px;
      align-items: start;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 28px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
      overflow: hidden;
      position: relative;
    }}
    .panel::after {{
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      border: 1px solid rgba(255, 255, 255, 0.45);
      pointer-events: none;
    }}
    .panel-inner {{ padding: 28px; }}
    .hero {{
      padding: 28px 28px 20px;
      border-bottom: 1px solid var(--border);
      background:
        radial-gradient(circle at top right, rgba(197, 106, 27, 0.16), transparent 28%),
        linear-gradient(180deg, rgba(15,118,110,0.13), rgba(255,255,255,0));
    }}
    h1, h2, h3 {{ margin: 0; }}
    h1 {{
      font-family: var(--serif);
      font-size: clamp(2.4rem, 5vw, 4.25rem);
      line-height: 0.95;
      letter-spacing: -0.05em;
      max-width: 10ch;
    }}
    h2 {{ font-size: 1.12rem; margin-bottom: 14px; font-weight: 800; letter-spacing: -0.03em; }}
    h3 {{ font-size: 0.98rem; font-weight: 800; letter-spacing: -0.02em; }}
    p {{ margin: 0; color: var(--muted); line-height: 1.55; }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      margin-bottom: 16px;
      border-radius: 999px;
      background: rgba(255,255,255,0.64);
      border: 1px solid rgba(19, 78, 74, 0.12);
      color: var(--accent-strong);
      font-size: 0.82rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .hero-copy {{ max-width: 58ch; display: grid; gap: 12px; }}
    .hero-grid {{ display: grid; gap: 18px; }}
    .hero-metrics {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 6px;
    }}
    .hero-metric {{
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.6);
      border: 1px solid rgba(19, 78, 74, 0.11);
    }}
    .hero-metric strong {{
      display: block;
      margin-bottom: 4px;
      font-size: 1.15rem;
      font-weight: 800;
      color: var(--code);
    }}
    .hero-metric span {{ font-size: 0.84rem; color: var(--muted); }}
    form {{ display: grid; gap: 18px; }}
    .section {{ display: grid; gap: 12px; }}
    .section-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }}
    .section-head span {{ color: var(--muted); font-size: 0.9rem; max-width: 30ch; text-align: right; }}
    .goals {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }}
    .goal-option {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 15px;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,252,251,0.92));
      border: 1px solid rgba(15, 118, 110, 0.14);
      cursor: pointer;
      transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease, background 140ms ease;
    }}
    .goal-option:hover {{ transform: translateY(-1px); border-color: rgba(15, 118, 110, 0.32); box-shadow: 0 16px 28px rgba(15, 118, 110, 0.08); }}
    .goal-option:has(input:checked) {{
      background: linear-gradient(180deg, rgba(216, 240, 234, 0.96), rgba(255,255,255,0.94));
      border-color: rgba(15, 118, 110, 0.34);
      box-shadow: inset 0 0 0 1px rgba(15, 118, 110, 0.08);
    }}
    .goal-option input {{ accent-color: var(--accent); width: 18px; height: 18px; }}
    .goal-option span {{ font-size: 0.95rem; line-height: 1.35; font-weight: 700; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .field {{ display: grid; gap: 8px; }}
    .field.full {{ grid-column: 1 / -1; }}
    .field-hint {{ color: var(--muted); font-size: 0.84rem; }}
    label.title {{ font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); font-weight: 800; }}
    input[type="text"], input[type="number"], textarea {{
      width: 100%;
      border: 1px solid rgba(21, 50, 67, 0.12);
      background: rgba(255,255,255,0.92);
      border-radius: 16px;
      padding: 13px 14px;
      color: var(--code);
      font-size: 0.96rem;
      font-family: var(--mono);
      outline: none;
      transition: border-color 140ms ease, box-shadow 140ms ease;
    }}
    input:focus, textarea:focus {{ border-color: var(--accent); box-shadow: 0 0 0 4px rgba(45, 212, 191, 0.15); }}
    textarea {{ min-height: 132px; resize: vertical; }}
    .field textarea, .field input {{ box-shadow: inset 0 1px 0 rgba(255,255,255,0.45); }}
    .settings-band {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 4px;
    }}
    .band-card {{
      padding: 14px 15px;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,0.78), rgba(255,255,255,0.58));
      border: 1px solid rgba(21, 50, 67, 0.08);
    }}
    .band-card strong {{ display: block; margin-bottom: 5px; font-size: 0.95rem; }}
    .band-card span {{ color: var(--muted); font-size: 0.84rem; line-height: 1.45; }}
    .actions {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
    button {{
      border: none;
      border-radius: 999px;
      padding: 13px 20px;
      font-size: 0.95rem;
      font-weight: 800;
      font-family: var(--sans);
      cursor: pointer;
      transition: transform 140ms ease, opacity 140ms ease, box-shadow 140ms ease;
    }}
    button:hover {{ transform: translateY(-1px); }}
    button:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}
    .primary {{ background: linear-gradient(135deg, var(--accent), var(--accent-strong)); color: #fff; box-shadow: 0 18px 30px rgba(15, 118, 110, 0.24); }}
    .secondary {{ background: rgba(21, 50, 67, 0.08); color: var(--text); }}
    .primary:focus-visible, .secondary:focus-visible {{ outline: 2px solid rgba(15, 118, 110, 0.45); outline-offset: 2px; }}
    .status-card {{ display: grid; gap: 18px; }}
    .status-row {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; }}
    .badge {{ background: rgba(15, 118, 110, 0.12); color: var(--accent-strong); padding: 8px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }}
    .progress-track {{ height: 14px; background: rgba(21,50,67,0.08); border-radius: 999px; overflow: hidden; position: relative; }}
    .progress-bar {{ height: 100%; width: 0%; border-radius: inherit; background: linear-gradient(90deg, #0f766e, #14b8a6, #f59e0b); transition: width 220ms ease; }}
    .progress-note {{ color: var(--muted); font-size: 0.86rem; display: flex; justify-content: space-between; gap: 12px; }}
    .meta {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .meta-card {{ background: rgba(255,255,255,0.86); border: 1px solid rgba(21,50,67,0.08); border-radius: 18px; padding: 15px; }}
    .meta-card strong {{ display: block; font-size: 1.22rem; margin-bottom: 4px; font-weight: 800; }}
    .meta-card span {{ color: var(--muted); font-size: 0.88rem; }}
    .insight-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .insight-card {{
      min-height: 124px;
      padding: 16px;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(216, 240, 234, 0.46), rgba(255,255,255,0.92));
      border: 1px solid rgba(15, 118, 110, 0.14);
      display: grid;
      gap: 8px;
      align-content: start;
    }}
    .insight-card.alt {{
      background: linear-gradient(180deg, rgba(244, 214, 184, 0.52), rgba(255,255,255,0.94));
      border-color: rgba(197, 106, 27, 0.18);
    }}
    .insight-card strong {{ font-size: 0.98rem; font-weight: 800; }}
    .insight-card p {{ font-size: 0.9rem; }}
    .log {{
      min-height: 300px;
      max-height: 420px;
      overflow: auto;
      border-radius: 18px;
      background: #12212a;
      color: #d5e4ea;
      padding: 16px;
      font-family: var(--mono);
      font-size: 0.9rem;
      line-height: 1.45;
      white-space: pre-wrap;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}
    .report {{
      margin-top: 14px;
      border-radius: 18px;
      background: rgba(255,255,255,0.9);
      border: 1px solid rgba(21,50,67,0.08);
      padding: 16px;
      max-height: 320px;
      overflow: auto;
      font-family: var(--mono);
      font-size: 0.86rem;
      white-space: pre-wrap;
      color: var(--code);
    }}
    .error {{ color: var(--danger); min-height: 1.2em; }}
    .quiet {{ color: var(--muted); font-size: 0.9rem; }}
    .status-layout {{ display: grid; gap: 18px; }}
    .support-note {{
      padding: 14px 15px;
      border-radius: 18px;
      background: rgba(255,255,255,0.62);
      border: 1px solid rgba(21,50,67,0.08);
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.5;
    }}
    @media (max-width: 980px) {{
      .shell {{ grid-template-columns: 1fr; }}
      .grid, .meta, .hero-metrics, .settings-band, .insight-grid {{ grid-template-columns: 1fr; }}
      .section-head {{ flex-direction: column; align-items: start; }}
      .section-head span {{ text-align: left; max-width: none; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="panel">
      <div class="hero">
        <div class="hero-grid">
          <div class="hero-copy">
            <div class="eyebrow">Memory-Assisted Ontology Engineering</div>
            <h1>Shape the pipeline before you commit a run.</h1>
            <p>Choose the execution goals, confirm the ontology sources, and launch a monitored run from one place. The UI is tuned for long-running ontology generation work, not just a thin wrapper around the CLI.</p>
          </div>
          <div class="hero-metrics">
            <div class="hero-metric">
              <strong>{len(PIPELINE_GOALS)} stages</strong>
              <span>Available pipeline goals</span>
            </div>
            <div class="hero-metric">
              <strong id="selected-goal-count">{default_goal_count} selected</strong>
              <span>Default run configuration</span>
            </div>
            <div class="hero-metric">
              <strong id="existing-ontology-count">{existing_ontology_count} ontologies</strong>
              <span>Preloaded reuse sources</span>
            </div>
          </div>
        </div>
      </div>
      <div class="panel-inner">
        <form id="pipeline-form">
          <div class="section">
            <div class="section-head">
              <h2>What should this run do?</h2>
              <span>Select one or more steps to include in this run</span>
            </div>
            <div class="goals">{goal_options}</div>
          </div>
          <div class="section">
            <div class="section-head">
              <h2>Files and settings</h2>
              <span>Use repository-relative paths unless you need an absolute path</span>
            </div>
            <div class="settings-band">
              <div class="band-card">
                <strong>Input discipline</strong>
                <span>Relative paths keep runs portable across machines and branches.</span>
              </div>
              <div class="band-card">
                <strong>Ontology reuse</strong>
                <span>Keep one ontology path per line to preserve mapping order and intent.</span>
              </div>
              <div class="band-card">
                <strong>Generation scope</strong>
                <span>Use the numeric limits to trade depth for faster feedback while iterating.</span>
              </div>
            </div>
            <div class="grid">
              <div class="field full">
                <label class="title" for="declarative">Declarative Ontology</label>
                <input id="declarative" name="declarative" type="text" value="{_escape_attr(defaults['declarative'])}">
                <div class="field-hint">Primary ontology memory source used to ground the run.</div>
              </div>
              <div class="field full">
                <label class="title" for="procedural">Procedural Source</label>
                <input id="procedural" name="procedural" type="text" value="{_escape_attr(defaults['procedural'])}">
                <div class="field-hint">EU AI Act JSON source consumed by the procedural memory pipeline.</div>
              </div>
              <div class="field full">
                <label class="title" for="competency_questions">Competency Questions Output</label>
                <input id="competency_questions" name="competency_questions" type="text" value="{_escape_attr(defaults['competency_questions'])}">
              </div>
              <div class="field full">
                <label class="title" for="concept_extraction_output">Concept Extraction Output</label>
                <input id="concept_extraction_output" name="concept_extraction_output" type="text" value="{_escape_attr(defaults['concept_extraction_output'])}">
              </div>
              <div class="field full">
                <label class="title" for="mapping_output">Mapping Output</label>
                <input id="mapping_output" name="mapping_output" type="text" value="{_escape_attr(defaults['mapping_output'])}">
              </div>
              <div class="field full">
                <label class="title" for="ontology_output">Ontology Output</label>
                <input id="ontology_output" name="ontology_output" type="text" value="{_escape_attr(defaults['ontology_output'])}">
              </div>
              <div class="field full">
                <label class="title" for="config">API Config</label>
                <input id="config" name="config" type="text" value="{_escape_attr(defaults['config'])}">
                <div class="field-hint">Make sure the config file contains real API credentials before launching LLM-backed steps.</div>
              </div>
              <div class="field">
                <label class="title" for="concept_limit">Concept Limit</label>
                <input id="concept_limit" name="concept_limit" type="number" min="1" value="{defaults['concept_limit']}">
              </div>
              <div class="field">
                <label class="title" for="chapter_limit">Chapter Limit</label>
                <input id="chapter_limit" name="chapter_limit" type="number" min="1" value="{defaults['chapter_limit']}">
              </div>
              <div class="field full">
                <label class="title" for="existing_ontologies">Existing Ontologies</label>
                <textarea id="existing_ontologies" name="existing_ontologies">{existing_ontologies}</textarea>
              </div>
            </div>
          </div>
          <div class="actions">
            <button class="primary" id="run-button" type="submit">Start Run</button>
            <button class="secondary" id="stop-button" type="button">Stop After Current Step</button>
            <button class="secondary" id="reset-button" type="button">Restore Default Values</button>
            <span class="quiet">The UI stays available until you stop the Python process.</span>
          </div>
          <div class="error" id="error"></div>
        </form>
      </div>
    </section>

    <section class="panel">
      <div class="hero">
        <div class="eyebrow">Run monitor</div>
        <h2 style="font-family: var(--serif); font-size:2rem; line-height:1; margin-top:2px; letter-spacing:-0.04em;">Live progress, operational context, and final report.</h2>
      </div>
      <div class="panel-inner status-layout">
        <div class="status-card">
          <div class="status-row">
            <strong id="status-text">Ready to start</strong>
            <div class="badge" id="status-badge">Idle</div>
          </div>
          <div class="progress-track"><div class="progress-bar" id="progress-bar"></div></div>
          <div class="progress-note">
            <span id="progress-caption">No active run</span>
            <span id="run-identifier">Run ID: --</span>
          </div>
          <div class="meta">
            <div class="meta-card"><strong id="current-goal">0 / 0</strong><span>Selected steps completed</span></div>
            <div class="meta-card"><strong id="current-action">Waiting</strong><span>Current activity</span></div>
          </div>
        </div>
        <div class="insight-grid">
          <div class="insight-card">
            <strong>Operator view</strong>
            <p>The log records stage transitions as the worker process reports them, so you can see where long-running steps stall or finish.</p>
          </div>
          <div class="insight-card alt">
            <strong>Stop behavior</strong>
            <p>The stop control ends the background process and preserves the latest emitted state so you can inspect what happened.</p>
          </div>
        </div>
        <div>
          <h3 style="margin-bottom:10px;">Activity log</h3>
          <div class="log" id="log">No run has started yet.</div>
        </div>
        <div>
          <h3 style="margin-bottom:10px;">Structured result</h3>
          <div class="report" id="report">Results will appear here after the run finishes.</div>
        </div>
        <div class="support-note">
          The UI remains active until you stop the Python process that launched it. Keep that terminal open while you monitor or rerun the pipeline.
        </div>
      </div>
    </section>
  </div>

  <script>
    const defaults = {json.dumps(_json_ready(defaults))};
    const form = document.getElementById('pipeline-form');
    const runButton = document.getElementById('run-button');
    const stopButton = document.getElementById('stop-button');
    const resetButton = document.getElementById('reset-button');
    const errorBox = document.getElementById('error');
    const logBox = document.getElementById('log');
    const reportBox = document.getElementById('report');
    const selectedGoalCount = document.getElementById('selected-goal-count');
    const existingOntologyCount = document.getElementById('existing-ontology-count');
    const statusText = document.getElementById('status-text');
    const statusBadge = document.getElementById('status-badge');
    const progressBar = document.getElementById('progress-bar');
    const progressCaption = document.getElementById('progress-caption');
    const runIdentifier = document.getElementById('run-identifier');
    const currentGoal = document.getElementById('current-goal');
    const currentAction = document.getElementById('current-action');

    function updateConfigurationSummary() {{
      const selectedGoals = form.querySelectorAll('input[name="goals"]:checked').length;
      const ontologyCount = form.existing_ontologies.value
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean)
        .length;
      selectedGoalCount.textContent = `${{selectedGoals}} selected`;
      existingOntologyCount.textContent = `${{ontologyCount}} ontologies`;
    }}

    function resetForm() {{
      for (const [key, value] of Object.entries(defaults)) {{
        if (key === 'goals') continue;
        const field = form.elements.namedItem(key);
        if (!field) continue;
        field.value = Array.isArray(value) ? value.join('\\n') : value;
      }}
      const checkboxes = form.querySelectorAll('input[name="goals"]');
      checkboxes.forEach((checkbox) => {{
        checkbox.checked = defaults.goals.includes(checkbox.value);
      }});
      updateConfigurationSummary();
      errorBox.textContent = '';
    }}

    function appendLog(message) {{
      if (!message) return;
      if (logBox.textContent === 'No run has started yet.') {{
        logBox.textContent = '';
      }}
      for (const line of message.split('\\n')) {{
        logBox.textContent += `${{new Date().toLocaleTimeString()}}  ${{line}}\\n`;
      }}
      logBox.scrollTop = logBox.scrollHeight;
    }}

    function applyState(state) {{
      const total = state.total || 0;
      const current = state.current || 0;
      const percent = total > 0 ? Math.min(100, Math.round((current / total) * 100)) : 0;
      progressBar.style.width = `${{percent}}%`;
      progressCaption.textContent = total > 0 ? `${{percent}}% complete across selected goals` : 'No active run';
      runIdentifier.textContent = state.run_id ? `Run ID: ${{state.run_id}}` : 'Run ID: --';
      currentGoal.textContent = `${{current}} / ${{total}}`;
      currentAction.textContent = state.action || 'Waiting';
      statusText.textContent = state.status_text || 'Ready to start';
      statusBadge.textContent = state.status_badge || 'Idle';
      appendLog(state.last_event);
      if (state.report) reportBox.textContent = JSON.stringify(state.report, null, 2);
      if (state.error) errorBox.textContent = state.error;
      stopButton.disabled = !state.running;
      runButton.textContent = state.running ? 'Run In Progress' : 'Start Run';
    }}

    async function pollStatus() {{
      const response = await fetch('/api/status');
      const state = await response.json();
      applyState(state);
      runButton.disabled = state.running;
      return state;
    }}

    function collectPayload() {{
      const goals = [...form.querySelectorAll('input[name="goals"]:checked')].map((node) => node.value);
      return {{
        goals,
        declarative: form.declarative.value.trim(),
        procedural: form.procedural.value.trim(),
        competency_questions: form.competency_questions.value.trim(),
        concept_extraction_output: form.concept_extraction_output.value.trim(),
        existing_ontologies: form.existing_ontologies.value.split('\\n').map((item) => item.trim()).filter(Boolean),
        mapping_output: form.mapping_output.value.trim(),
        ontology_output: form.ontology_output.value.trim(),
        config: form.config.value.trim(),
        concept_limit: Number(form.concept_limit.value),
        chapter_limit: Number(form.chapter_limit.value),
      }};
    }}

    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      errorBox.textContent = '';
      logBox.textContent = '';
      reportBox.textContent = 'Run in progress. Results will appear here when finished.';
      const payload = collectPayload();
      const response = await fetch('/api/run', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(payload),
      }});
      const result = await response.json();
      if (!response.ok) {{
        errorBox.textContent = result.error || 'The run could not be started.';
        return;
      }}
      appendLog(`Run ${{result.run_id}} started.`);
      await pollStatus();
    }});

    stopButton.addEventListener('click', async () => {{
      errorBox.textContent = '';
      const response = await fetch('/api/stop', {{ method: 'POST' }});
      const result = await response.json();
      if (!response.ok) {{
        errorBox.textContent = result.error || 'The run could not be stopped.';
        return;
      }}
      appendLog(result.message || 'Stop requested. The current step will finish first.');
      await pollStatus();
    }});

    form.querySelectorAll('input[name="goals"]').forEach((checkbox) => {{
      checkbox.addEventListener('change', updateConfigurationSummary);
    }});
    form.existing_ontologies.addEventListener('input', updateConfigurationSummary);
    resetButton.addEventListener('click', resetForm);
    resetForm();
    stopButton.disabled = true;
    pollStatus();
    setInterval(() => {{
      pollStatus().catch((error) => {{
        errorBox.textContent = error.message;
      }});
    }}, 1200);
  </script>
</body>
</html>
"""


def _coerce_payload(defaults: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    params = dict(defaults)
    params.update(payload)
    params["goals"] = [goal for goal in payload.get("goals", []) if goal in PIPELINE_GOALS]
    if not params["goals"]:
        raise ValueError("Select at least one pipeline goal.")

    params["existing_ontologies"] = [
        str(item).strip() for item in payload.get("existing_ontologies", []) if str(item).strip()
    ]
    if not params["existing_ontologies"]:
        raise ValueError("Provide at least one existing ontology path.")

    params["concept_limit"] = int(payload.get("concept_limit", defaults["concept_limit"]))
    params["chapter_limit"] = int(payload.get("chapter_limit", defaults["chapter_limit"]))
    if params["concept_limit"] < 1 or params["chapter_limit"] < 1:
        raise ValueError("Concept limit and chapter limit must be positive integers.")
    return params


def _resolve_path(value: Optional[Any]) -> Optional[str]:
  if value is None:
    return None

  path_str = str(value).strip()
  if not path_str:
    return None
  if Path(path_str).is_absolute():
    return path_str

  path = Path(path_str)
  repo_root = Path(REPO_ROOT)
  if path.parts and path.parts[0] == repo_root.name:
    path = Path(*path.parts[1:])
  return str(repo_root / path)


@dataclass
class RunState:
  defaults: Dict[str, Any]
  running: bool = False
  stop_requested: bool = False
  current: int = 0
  total: int = 0
  action: str = "None"
  status_text: str = "Idle"
  status_badge: str = "Waiting"
  error: str = ""
  report: Optional[List[Dict[str, Any]]] = None
  events: List[str] = field(default_factory=list)
  event_offset: int = 0
  run_id: Optional[int] = None
  _lock: threading.Lock = field(default_factory=threading.Lock)
  _worker_process: Optional[Any] = field(default=None, repr=False)

  def snapshot(self) -> Dict[str, Any]:
    with self._lock:
      last_event = None
      if self.event_offset < len(self.events):
        last_event = "\n".join(self.events[self.event_offset:])
        self.event_offset = len(self.events)
      return {
        "running": self.running,
        "stop_requested": self.stop_requested,
        "current": self.current,
        "total": self.total,
        "action": self.action,
        "status_text": self.status_text,
        "status_badge": self.status_badge,
        "error": self.error,
        "report": self.report,
        "last_event": last_event,
        "run_id": self.run_id,
      }

  def reset_for_run(self, run_id: int, total: int) -> None:
    with self._lock:
      self.running = True
      self.stop_requested = False
      self.current = 0
      self.total = total
      self.action = "None"
      self.status_text = "Preparing run"
      self.status_badge = "Running"
      self.error = ""
      self.report = None
      self.events = []
      self.event_offset = 0
      self.run_id = run_id
      self._worker_process = None

  def attach_worker(self, worker_process: Any) -> None:
    with self._lock:
      self._worker_process = worker_process

  def request_stop(self) -> bool:
    with self._lock:
      if not self.running:
        return False
      worker_process = self._worker_process
      self.stop_requested = True

    if worker_process is not None and worker_process.is_alive():
      worker_process.terminate()
      worker_process.join(timeout=1)
      if worker_process.is_alive():
        worker_process.kill()
        worker_process.join(timeout=1)

    self.finish_error("Pipeline run stopped by user.")
    return True

  def is_active_run(self, run_id: int) -> bool:
    with self._lock:
      return self.running and self.run_id == run_id

  def update_from_progress(self, event: Dict[str, Any]) -> None:
    stage = event["stage"]
    goal = event.get("goal")
    action = event.get("action")
    current = event.get("current")
    total = event.get("total")
    with self._lock:
      if current is not None:
        self.current = current
      if total is not None:
        self.total = total
      if action:
        self.action = action

      if stage == "goal_started":
        self.status_text = f"Starting {goal}"
        self.events.append(f"Goal {self.current}/{self.total} started: {goal}")
      elif stage == "plan_created":
        self.status_text = f"Planned {action}"
        self.events.append(f"Plan created for {goal}: {action}")
      elif stage == "action_started":
        self.status_text = f"Executing {action}"
        self.events.append(f"Action started: {action}")
      elif stage == "action_completed":
        self.status_text = f"Completed {action}"
        self.events.append(f"Action completed: {action}")
      elif stage == "goal_completed":
        self.status_text = f"Finished {goal}"
        self.events.append(f"Goal {self.current}/{self.total} finished: {goal}")

  def finish_success(self, report: List[Dict[str, Any]]) -> None:
    with self._lock:
      self.running = False
      self.stop_requested = False
      self.current = self.total
      self.status_text = "Run completed"
      self.status_badge = "Done"
      self.report = report
      self._worker_process = None
      self.events.append("Pipeline run completed successfully.")

  def finish_error(self, message: str) -> None:
    with self._lock:
      self.running = False
      self.stop_requested = False
      if message == "Pipeline run stopped by user.":
        self.status_text = "Run stopped"
        self.status_badge = "Stopped"
      else:
        self.status_text = "Run failed"
        self.status_badge = "Error"
      self.error = message
      self._worker_process = None
      self.events.append(f"Pipeline run failed: {message}")


def _pipeline_worker(params: Dict[str, Any], event_queue: Any) -> None:
  try:
    from client.client_access import PrototypeClient

    prototype_client = PrototypeClient(
      declarative_ontology_path=_resolve_path(params["declarative"]),
      procedural_pdf_path=_resolve_path(params["procedural"]),
      config={
        "competency_questions_path": _resolve_path(params["competency_questions"]),
        "concept_extraction_output_path": _resolve_path(params["concept_extraction_output"]),
        "existing_ontologies": [_resolve_path(item) for item in params["existing_ontologies"]],
        "mapping_output_path": _resolve_path(params["mapping_output"]),
        "run_config_path": _resolve_path(params["config"]),
      },
      run_config_path=_resolve_path(params["config"]),
      ontology_output_path=_resolve_path(params["ontology_output"]),
      concept_limit=params["concept_limit"],
      chapter_limit=params["chapter_limit"],
    )
    report = prototype_client.run_pipeline(
      params["goals"],
      progress_callback=lambda event: event_queue.put({"type": "progress", "event": event}),
    )
  except Exception as exc:
    event_queue.put({"type": "error", "message": str(exc)})
    return
  event_queue.put({"type": "success", "report": report})


def _monitor_worker_process(run_id: int, worker_process: Any, event_queue: Any, state: RunState) -> None:
  while True:
    if not state.is_active_run(run_id):
      return
    try:
      message = event_queue.get(timeout=0.2)
    except queue.Empty:
      if not worker_process.is_alive():
        if state.is_active_run(run_id):
          state.finish_error("Pipeline run exited unexpectedly.")
        return
      continue

    if not state.is_active_run(run_id):
      return

    message_type = message.get("type")
    if message_type == "progress":
      state.update_from_progress(message["event"])
    elif message_type == "success":
      state.finish_success(message["report"])
      return
    elif message_type == "error":
      state.finish_error(message["message"])
      return


def launch_web_ui(defaults: Dict[str, Any]) -> None:
  state = RunState(defaults=_json_ready(dict(defaults)))
  run_counter = count(1)
  mp_context = mp.get_context("spawn")

  class RequestHandler(BaseHTTPRequestHandler):
    def _send_bytes(
      self,
      body: bytes,
      content_type: str,
      status: int = HTTPStatus.OK,
    ) -> None:
      self.send_response(status)
      self.send_header("Content-Type", content_type)
      self.send_header("Content-Length", str(len(body)))
      self.end_headers()
      if body:
        self.wfile.write(body)

    def _send_json(self, payload: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
      body = json.dumps(payload).encode("utf-8")
      self._send_bytes(body, "application/json; charset=utf-8", status=status)

    def _read_payload(self) -> Dict[str, Any]:
      content_length = int(self.headers.get("Content-Length", "0"))
      raw_body = self.rfile.read(content_length)
      return json.loads(raw_body.decode("utf-8")) if raw_body else {}

    def do_GET(self) -> None:
      request_path = urlsplit(self.path).path
      if request_path in {"/", "/index.html"}:
        body = _html_template(state.defaults).encode("utf-8")
        self._send_bytes(body, "text/html; charset=utf-8")
        return
      if request_path == "/favicon.ico":
        self._send_bytes(b"", "image/x-icon", status=HTTPStatus.NO_CONTENT)
        return
      if request_path == "/api/status":
        self._send_json(state.snapshot())
        return
      self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
      request_path = urlsplit(self.path).path
      if request_path == "/api/stop":
        if not state.request_stop():
          self._send_json(
            {"error": "No pipeline run is currently in progress."},
            status=HTTPStatus.CONFLICT,
          )
          return
        self._send_json({"status": "stopping", "message": "Stop requested."})
        return

      if request_path != "/api/run":
        self.send_error(HTTPStatus.NOT_FOUND)
        return
      if state.running:
        self._send_json(
          {"error": "A pipeline run is already in progress."},
          status=HTTPStatus.CONFLICT,
        )
        return
      try:
        payload = self._read_payload()
        params = _coerce_payload(state.defaults, payload)
      except (ValueError, json.JSONDecodeError) as exc:
        self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        return

      run_id = next(run_counter)
      state.reset_for_run(run_id=run_id, total=len(params["goals"]))
      event_queue = mp_context.Queue()
      worker_process = mp_context.Process(
        target=_pipeline_worker,
        args=(params, event_queue),
        daemon=True,
      )
      worker_process.start()
      state.attach_worker(worker_process)
      monitor = threading.Thread(
        target=_monitor_worker_process,
        args=(run_id, worker_process, event_queue, state),
        daemon=True,
      )
      monitor.start()
      self._send_json({"run_id": run_id, "status": "started"}, status=HTTPStatus.ACCEPTED)

    def log_message(self, format: str, *args: Any) -> None:
      return

  server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
  url = f"http://127.0.0.1:{server.server_port}"
  print(f"Launching web UI at {url}")
  webbrowser.open(url)
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    pass
  finally:
    server.server_close()
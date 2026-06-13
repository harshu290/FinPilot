import streamlit as st
from groq import Groq
import plotly.graph_objects as go
from dotenv import load_dotenv
import re
import json

load_dotenv()

st.set_page_config(
    page_title="FinPilot — Financial Intelligence",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── DESIGN SYSTEM ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F8FAFC;
    color: #1E293B;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, header, footer { visibility: hidden; height: 0; }
.stDeployButton { display: none; }
[data-testid="stSidebar"] { display: none; }
.block-container {
    padding: 0 0 4rem 0 !important;
    max-width: 1280px;
    margin: 0 auto;
}
section[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── Top navigation bar ── */
.fp-navbar {
    position: sticky;
    top: 0;
    z-index: 200;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 56px;
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    backdrop-filter: blur(8px);
}
.fp-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.02em;
}
.fp-logo-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #10B981;
    display: inline-block;
}
.fp-nav-links {
    display: flex;
    align-items: center;
    gap: 28px;
    list-style: none;
    margin: 0; padding: 0;
}
.fp-nav-links li a {
    font-size: 13px;
    font-weight: 500;
    color: #64748B;
    text-decoration: none;
    letter-spacing: 0.01em;
    transition: color 0.15s;
}
.fp-nav-links li a:hover { color: #0F172A; }
.fp-nav-badge {
    background: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* ── Page wrapper ── */
.fp-page { padding: 0 40px; }

/* ── Hero / Header ── */
.fp-hero {
    padding: 48px 0 40px;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 40px;
}
.fp-hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #059669;
    margin-bottom: 14px;
}
.fp-hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #10B981;
}
.fp-hero-title {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 38px;
    font-weight: 400;
    color: #0F172A;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 10px;
}
.fp-hero-title em {
    font-style: italic;
    color: #10B981;
}
.fp-hero-sub {
    font-size: 15px;
    color: #64748B;
    font-weight: 400;
    line-height: 1.6;
    max-width: 500px;
}

/* ── KPI cards row ── */
.fp-kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px 28px;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s;
}
.fp-kpi-card:hover { box-shadow: 0 4px 20px rgba(15,23,42,0.07); }
.fp-kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 10px;
}
.fp-kpi-value {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 32px;
    font-weight: 400;
    color: #0F172A;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 8px;
}
.fp-kpi-status {
    font-size: 12px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 20px;
}
.status-excellent { background: #ECFDF5; color: #047857; }
.status-good      { background: #FEF9C3; color: #854D0E; }
.status-fair      { background: #FFF7ED; color: #9A3412; }
.status-poor      { background: #FEF2F2; color: #991B1B; }
.fp-kpi-accent {
    position: absolute;
    right: 0; bottom: 0;
    width: 56px; height: 56px;
    background: linear-gradient(135deg, transparent 60%, #ECFDF5 100%);
    border-top-left-radius: 100%;
}

/* ── Section layout ── */
.fp-section { margin-bottom: 48px; }
.fp-section-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #F1F5F9;
}
.fp-section-title {
    font-size: 16px;
    font-weight: 600;
    color: #0F172A;
    letter-spacing: -0.01em;
}
.fp-section-meta {
    font-size: 12px;
    color: #94A3B8;
    font-weight: 400;
}

/* ── Score ring card ── */
.fp-score-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    height: 100%;
}
.fp-score-ring-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 4px;
}
.fp-score-big {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 64px;
    font-weight: 400;
    color: #0F172A;
    letter-spacing: -0.04em;
    line-height: 1;
}
.fp-score-denom { font-size: 20px; color: #CBD5E1; }
.fp-score-grade {
    font-size: 13px;
    font-weight: 600;
    margin-top: 8px;
    padding: 4px 14px;
    border-radius: 20px;
}

/* ── Breakdown table ── */
.fp-breakdown-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #F8FAFC;
    font-size: 13px;
    color: #334155;
}
.fp-breakdown-row:last-child { border-bottom: none; }
.fp-breakdown-label { color: #64748B; font-weight: 400; }
.fp-breakdown-score {
    font-size: 12px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 4px;
    background: #F8FAFC;
    color: #334155;
    font-variant-numeric: tabular-nums;
}

/* ── Ratio bar ── */
.fp-ratio-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #F8FAFC;
    font-size: 13px;
}
.fp-ratio-row:last-child { border-bottom: none; }
.fp-ratio-label { width: 140px; color: #64748B; flex-shrink: 0; }
.fp-ratio-track {
    flex: 1;
    height: 5px;
    background: #F1F5F9;
    border-radius: 3px;
    overflow: hidden;
}
.fp-ratio-fill { height: 100%; border-radius: 3px; }
.fill-green  { background: #10B981; }
.fill-yellow { background: #F59E0B; }
.fill-red    { background: #EF4444; }
.fp-ratio-value { width: 52px; text-align: right; font-weight: 500; color: #0F172A; font-variant-numeric: tabular-nums; }
.fp-ratio-tag {
    width: 64px;
    text-align: right;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.tag-green  { color: #059669; }
.tag-yellow { color: #D97706; }
.tag-red    { color: #DC2626; }

/* ── Insight / recommendation cards ── */
.fp-insight-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 12px;
    display: flex;
    gap: 20px;
    align-items: flex-start;
    transition: box-shadow 0.2s;
}
.fp-insight-card:hover { box-shadow: 0 4px 16px rgba(15,23,42,0.06); }
.fp-insight-icon {
    width: 40px; height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}
.icon-blue   { background: #EFF6FF; }
.icon-green  { background: #ECFDF5; }
.icon-orange { background: #FFF7ED; }
.icon-purple { background: #F5F3FF; }
.fp-insight-content { flex: 1; }
.fp-insight-title {
    font-size: 14px;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 4px;
}
.fp-insight-desc { font-size: 13px; color: #64748B; line-height: 1.55; }
.fp-insight-impact {
    margin-top: 8px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    font-weight: 500;
    color: #059669;
}
.fp-insight-alert { color: #DC2626 !important; }

/* ── Alert banner ── */
.fp-alert-banner {
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    border-left: 3px solid #F97316;
    border-radius: 8px;
    padding: 14px 20px;
    font-size: 13px;
    color: #9A3412;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ── Form cards ── */
.fp-form-block {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 20px;
}
.fp-form-block-title {
    font-size: 14px;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 4px;
}
.fp-form-block-sub {
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 20px;
}
.fp-step-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #10B981;
    margin-bottom: 6px;
}

/* ── CTA button ── */
div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s !important;
    border: 1px solid #E2E8F0 !important;
    padding: 10px 20px !important;
    color: #334155 !important;
    background: #FFFFFF !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 1px 2px rgba(15,23,42,0.2) !important;
    padding: 12px 28px !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #1E293B !important;
    box-shadow: 0 4px 12px rgba(15,23,42,0.25) !important;
}

/* ── Streamlit inputs ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 7px !important;
    border-color: #E2E8F0 !important;
    background: #FFFFFF !important;
    font-size: 13px !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.1) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #64748B !important;
    margin-bottom: 4px !important;
    text-transform: none !important;
}
div[data-testid="stSlider"] { padding-top: 4px !important; }
div[data-testid="stCheckbox"] label { font-size: 13px !important; color: #334155 !important; }

/* ── Insurance cards ── */
.fp-ins-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 10px;
    transition: box-shadow 0.15s;
}
.fp-ins-card:hover { box-shadow: 0 3px 14px rgba(15,23,42,0.06); }
.fp-ins-name { font-size: 14px; font-weight: 600; color: #0F172A; margin-bottom: 3px; }
.fp-ins-detail { font-size: 12px; color: #64748B; line-height: 1.5; }
.fp-ins-cover {
    display: inline-block;
    margin-top: 8px;
    font-size: 11px;
    font-weight: 600;
    color: #059669;
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 4px;
    padding: 2px 8px;
    letter-spacing: 0.02em;
}

/* ── Divider ── */
.fp-divider { border: none; border-top: 1px solid #E2E8F0; margin: 40px 0; }

/* ── Footer ── */
.fp-footer {
    border-top: 1px solid #E2E8F0;
    padding: 28px 40px;
    text-align: center;
    font-size: 12px;
    color: #94A3B8;
    margin-top: 60px;
}

/* plan cards */
.plan-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 16px;
    transition: box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.plan-card:hover { box-shadow: 0 4px 20px rgba(15,23,42,0.07); }
.plan-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
}
.plan-card.card-blue::before   { background: #3B82F6; }
.plan-card.card-green::before  { background: #10B981; }
.plan-card.card-orange::before { background: #F59E0B; }
.plan-card.card-purple::before { background: #8B5CF6; }
.plan-card.card-rose::before   { background: #F43F5E; }
.plan-card.card-teal::before   { background: #14B8A6; }
.plan-card.card-indigo::before { background: #6366F1; }

.plan-card-header {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 20px;
}
.plan-card-icon {
    width: 38px; height: 38px;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    flex-shrink: 0;
    margin-top: 1px;
}
.icon-bg-blue   { background: #EFF6FF; }
.icon-bg-green  { background: #ECFDF5; }
.icon-bg-orange { background: #FFF7ED; }
.icon-bg-purple { background: #F5F3FF; }
.icon-bg-rose   { background: #FFF1F2; }
.icon-bg-teal   { background: #F0FDFA; }
.icon-bg-indigo { background: #EEF2FF; }

.plan-card-title-block { flex: 1; }
.plan-card-title {
    font-size: 15px;
    font-weight: 600;
    color: #0F172A;
    letter-spacing: -0.01em;
    margin-bottom: 3px;
}
.plan-card-summary {
    font-size: 13px;
    color: #64748B;
    line-height: 1.5;
}
.plan-priority-badge {
    flex-shrink: 0;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 4px;
    margin-top: 2px;
}
.priority-high   { background: #FEF2F2; color: #B91C1C; }
.priority-medium { background: #FFF7ED; color: #C2410C; }
.priority-low    { background: #ECFDF5; color: #047857; }

.plan-insights { margin: 0 0 18px; padding: 0; list-style: none; }
.plan-insights li {
    display: flex;
    align-items: flex-start;
    gap: 9px;
    padding: 6px 0;
    font-size: 13px;
    color: #334155;
    line-height: 1.5;
    border-bottom: 1px solid #F8FAFC;
}
.plan-insights li:last-child { border-bottom: none; }
.insight-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #CBD5E1;
    flex-shrink: 0;
    margin-top: 7px;
}
.insight-dot.dot-green  { background: #10B981; }
.insight-dot.dot-yellow { background: #F59E0B; }
.insight-dot.dot-red    { background: #EF4444; }
.insight-dot.dot-blue   { background: #3B82F6; }

.plan-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
}
.action-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 5px 11px;
    font-size: 12px;
    font-weight: 500;
    color: #334155;
}
.action-chip.chip-green { background: #ECFDF5; border-color: #A7F3D0; color: #065F46; }
.action-chip.chip-blue  { background: #EFF6FF; border-color: #BFDBFE; color: #1E40AF; }
.action-chip.chip-orange{ background: #FFF7ED; border-color: #FED7AA; color: #9A3412; }

.plan-impact-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 4px;
    padding-top: 14px;
    border-top: 1px solid #F1F5F9;
}
.impact-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    color: #047857;
}
.impact-pill.impact-alert {
    background: #FFF1F2;
    border-color: #FECDD3;
    color: #BE123C;
}
.impact-pill.impact-info {
    background: #EFF6FF;
    border-color: #BFDBFE;
    color: #1E40AF;
}

.alloc-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid #F8FAFC;
    font-size: 12px;
}
.alloc-row:last-of-type { border-bottom: none; }
.alloc-label { width: 150px; color: #64748B; flex-shrink: 0; font-weight: 500; }
.alloc-track {
    flex: 1;
    height: 6px;
    background: #F1F5F9;
    border-radius: 4px;
    overflow: hidden;
}
.alloc-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.alloc-amount { width: 90px; text-align: right; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; }

.plan-two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
}
.plan-metric-box {
    background: #F8FAFC;
    border: 1px solid #F1F5F9;
    border-radius: 9px;
    padding: 14px 16px;
}
.plan-metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 5px;
}
.plan-metric-value {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 24px;
    color: #0F172A;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 3px;
}
.plan-metric-sub { font-size: 11px; color: #94A3B8; }

.action-timeline { margin: 0; padding: 0; list-style: none; }
.action-phase {
    display: flex;
    gap: 16px;
    margin-bottom: 4px;
}
.action-phase-left {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 36px;
    flex-shrink: 0;
}
.phase-dot {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
}
.phase-dot-now    { background: #0F172A; color: #FFFFFF; }
.phase-dot-soon   { background: #3B82F6; color: #FFFFFF; }
.phase-dot-future { background: #E2E8F0; color: #64748B; }
.phase-line {
    width: 1px;
    flex: 1;
    background: #E2E8F0;
    margin: 4px 0;
    min-height: 16px;
}
.action-phase-right { flex: 1; padding-bottom: 20px; }
.phase-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 4px;
}
.phase-label-now    { color: #0F172A; }
.phase-label-soon   { color: #2563EB; }
.phase-label-future { color: #64748B; }
.phase-items { display: flex; flex-direction: column; gap: 6px; }
.phase-item {
    display: flex;
    align-items: center;
    gap: 9px;
    background: #F8FAFC;
    border: 1px solid #F1F5F9;
    border-radius: 8px;
    padding: 9px 13px;
    font-size: 13px;
    color: #334155;
    font-weight: 500;
}
.phase-item-now {
    background: #0F172A;
    border-color: #0F172A;
    color: #FFFFFF;
}
.phase-item-check {
    width: 16px; height: 16px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 9px;
    flex-shrink: 0;
}
.check-now    { background: #10B981; color: #FFFFFF; }
.check-soon   { background: #3B82F6; color: #FFFFFF; }
.check-future { background: #E2E8F0; color: #94A3B8; }

.tax-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #F8FAFC;
    font-size: 13px;
}
.tax-row:last-child { border-bottom: none; }
.tax-section { color: #64748B; font-weight: 400; }
.tax-limit { color: #0F172A; font-weight: 600; font-variant-numeric: tabular-nums; }
.tax-saving {
    font-size: 11px;
    font-weight: 600;
    background: #ECFDF5;
    color: #047857;
    padding: 2px 8px;
    border-radius: 4px;
}

.goal-progress-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #F8FAFC;
    font-size: 13px;
}
.goal-progress-row:last-child { border-bottom: none; }
.goal-name { width: 160px; font-weight: 500; color: #0F172A; flex-shrink: 0; }
.goal-track-wrap { flex: 1; }
.goal-track {
    height: 5px;
    background: #F1F5F9;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 4px;
}
.goal-fill { height: 100%; border-radius: 3px; background: #10B981; }
.goal-meta { font-size: 11px; color: #94A3B8; }
.goal-monthly { width: 90px; text-align: right; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; font-size: 12px; }

.plan-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 28px;
    padding: 14px 16px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
}
.plan-nav-pill {
    font-size: 12px;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 6px;
    color: #64748B;
    background: #F8FAFC;
    border: 1px solid #F1F5F9;
    cursor: default;
    display: flex;
    align-items: center;
    gap: 5px;
}

@media (max-width: 768px) {
    .fp-page { padding: 0 20px; }
    .fp-navbar { padding: 0 20px; }
    .fp-hero-title { font-size: 26px; }
    .fp-score-big { font-size: 48px; }
    .plan-two-col { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)


# ─── NAVBAR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="fp-navbar">
  <div class="fp-logo">
    <span class="fp-logo-dot"></span>
    FinPilot
  </div>
  <ul class="fp-nav-links">
    <li><a href="#">Overview</a></li>
    <li><a href="#">Planning</a></li>
    <li><a href="#">Investments</a></li>
    <li><span class="fp-nav-badge">AI Beta</span></li>
  </ul>
</div>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "emis" not in st.session_state:
    st.session_state.emis = [{"name": "", "amount": 0}]
if "misc" not in st.session_state:
    st.session_state.misc = [{"name": "", "min": 0, "max": 0}]
if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False
if "full_response" not in st.session_state:
    st.session_state.full_response = ""
if "financial_data" not in st.session_state:
    st.session_state.financial_data = {}


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def compute_health_score(income, total_emi, savings_target, medicine_avg, total_misc_avg, family_size):
    score = 0
    details = {}

    emi_ratio = (total_emi / income * 100) if income > 0 else 100
    if emi_ratio < 10:
        emi_pts = 30; emi_label = "Excellent"; emi_color = "excellent"
    elif emi_ratio < 25:
        emi_pts = 18; emi_label = "Moderate"; emi_color = "good"
    else:
        emi_pts = 6; emi_label = "High Burden"; emi_color = "poor"
    score += emi_pts
    details["emi"] = {"ratio": emi_ratio, "pts": emi_pts, "label": emi_label, "color": emi_color}

    expenses = total_emi + medicine_avg + total_misc_avg
    surplus = income - expenses
    savings_rate = (surplus / income * 100) if income > 0 else 0
    if savings_rate >= 20:
        sav_pts = 30; sav_label = "Excellent"; sav_color = "excellent"
    elif savings_rate >= 10:
        sav_pts = 18; sav_label = "Moderate"; sav_color = "good"
    else:
        sav_pts = 6; sav_label = "Below Target"; sav_color = "poor"
    score += sav_pts
    details["savings"] = {"rate": savings_rate, "pts": sav_pts, "label": sav_label, "color": sav_color, "surplus": surplus}

    recommended_ef = family_size * 15000 * 6
    months_to_ef = recommended_ef / max(surplus, 1)
    if months_to_ef <= 12:
        ef_pts = 20; ef_label = "Achievable < 12 mo"; ef_color = "excellent"
    elif months_to_ef <= 24:
        ef_pts = 12; ef_label = "12–24 months"; ef_color = "good"
    else:
        ef_pts = 4; ef_label = "> 24 months"; ef_color = "poor"
    score += ef_pts
    details["emergency"] = {"months": months_to_ef, "pts": ef_pts, "label": ef_label, "color": ef_color, "target": recommended_ef}

    ins_pts = 14
    score += ins_pts
    details["insurance"] = {"pts": ins_pts, "label": "Verify Coverage", "color": "good"}

    if score >= 80:
        grade = "Excellent"; grade_class = "status-excellent"
    elif score >= 60:
        grade = "Good"; grade_class = "status-good"
    elif score >= 40:
        grade = "Fair"; grade_class = "status-fair"
    else:
        grade = "Needs Attention"; grade_class = "status-poor"

    return score, grade, grade_class, details


CHART_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color="#64748B", size=12),
    margin=dict(t=40, b=16, l=8, r=8),
    height=320,
)


def render_charts(income, total_emi, medicine_avg, total_misc_avg):
    surplus = income - total_emi - medicine_avg - total_misc_avg

    labels, values, colors = [], [], []
    if total_emi > 0:
        labels.append("Loan Repayments"); values.append(total_emi); colors.append("#3B82F6")
    if medicine_avg > 0:
        labels.append("Healthcare"); values.append(medicine_avg); colors.append("#8B5CF6")
    if total_misc_avg > 0:
        labels.append("Bills & Living"); values.append(total_misc_avg); colors.append("#F59E0B")
    if surplus > 0:
        labels.append("Available Surplus"); values.append(surplus); colors.append("#10B981")

    fig_donut = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2.5)),
        textinfo="percent",
        textfont=dict(size=11, family="Inter"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
        direction="clockwise", sort=False,
    ))
    fig_donut.update_layout(
        **CHART_DEFAULTS,
        title=dict(text="Budget Allocation", font=dict(size=13, family="Inter", color="#0F172A", weight=600), x=0.02, y=0.97),
        legend=dict(font=dict(size=11, color="#64748B"), bgcolor="rgba(0,0,0,0)", orientation="v", x=1.02, y=0.5),
        annotations=[dict(
            text=f"₹{income:,.0f}<br><span style='font-size:10px;color:#94A3B8'>Income</span>",
            x=0.5, y=0.5, font=dict(size=14, family="Instrument Serif, Georgia", color="#0F172A"),
            showarrow=False
        )]
    )

    needs_rec = income * 0.50; wants_rec = income * 0.30; savings_rec = income * 0.20
    needs_act = total_emi + total_misc_avg + medicine_avg
    wants_act = min(max(surplus * 0.4, 0), wants_rec)
    savings_act = max(surplus - wants_act, 0)

    cats = ["Needs", "Wants", "Savings"]
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Recommended", x=cats, y=[needs_rec, wants_rec, savings_rec],
        marker_color=["#BFDBFE", "#DDD6FE", "#A7F3D0"],
        marker_line=dict(color=["#3B82F6", "#8B5CF6", "#10B981"], width=1.5),
        hovertemplate="<b>%{x}</b><br>Recommended: ₹%{y:,.0f}<extra></extra>",
    ))
    fig_bar.add_trace(go.Bar(
        name="Actual", x=cats, y=[needs_act, wants_act, savings_act],
        marker_color=["#3B82F6", "#8B5CF6", "#10B981"],
        hovertemplate="<b>%{x}</b><br>Actual: ₹%{y:,.0f}<extra></extra>",
    ))
    fig_bar.update_layout(
        **CHART_DEFAULTS,
        title=dict(text="50 / 30 / 20 Rule", font=dict(size=13, family="Inter", color="#0F172A", weight=600), x=0.02, y=0.97),
        barmode="group", bargap=0.3, bargroupgap=0.1,
        legend=dict(font=dict(size=11, color="#64748B"), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.12),
        xaxis=dict(showgrid=False, tickfont=dict(size=12), linecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", tickprefix="₹", tickfont=dict(size=11), zeroline=False),
    )

    monthly_save = max(surplus * 0.5, 0)
    annual_rate = 0.12
    months = list(range(0, 61))
    sip_corpus = [monthly_save * (((1 + annual_rate/12)**m - 1) / (annual_rate/12)) if m > 0 else 0 for m in months]
    simple_corpus = [monthly_save * m for m in months]

    fig_sip = go.Figure()
    fig_sip.add_trace(go.Scatter(
        x=months, y=sip_corpus, name="SIP @ 12% p.a.",
        fill="tozeroy", fillcolor="rgba(16,185,129,0.06)",
        line=dict(color="#10B981", width=2), mode="lines",
        hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>"
    ))
    fig_sip.add_trace(go.Scatter(
        x=months, y=simple_corpus, name="Savings Deposit",
        line=dict(color="#CBD5E1", width=1.5, dash="dot"), mode="lines",
        hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>"
    ))
    fig_sip.update_layout(
        **CHART_DEFAULTS,
        title=dict(text=f"Wealth Growth — SIP ₹{monthly_save:,.0f}/mo over 5 years", font=dict(size=13, family="Inter", color="#0F172A", weight=600), x=0.02, y=0.97),
        legend=dict(font=dict(size=11, color="#64748B"), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.12),
        xaxis=dict(showgrid=False, tickfont=dict(size=11), title=dict(text="Month", font=dict(size=11)), linecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", tickprefix="₹", tickfont=dict(size=11), title=dict(text="Corpus", font=dict(size=11)), zeroline=False),
    )

    wf_x, wf_y, wf_measure, wf_text = ["Income"], [income], ["absolute"], [f"₹{income:,.0f}"]
    if total_emi > 0:
        wf_x.append("Loan EMIs"); wf_y.append(-total_emi); wf_measure.append("relative"); wf_text.append(f"−₹{total_emi:,.0f}")
    if medicine_avg > 0:
        wf_x.append("Healthcare"); wf_y.append(-medicine_avg); wf_measure.append("relative"); wf_text.append(f"−₹{medicine_avg:,.0f}")
    if total_misc_avg > 0:
        wf_x.append("Living Costs"); wf_y.append(-total_misc_avg); wf_measure.append("relative"); wf_text.append(f"−₹{total_misc_avg:,.0f}")
    surplus_val = income - total_emi - medicine_avg - total_misc_avg
    wf_x.append("Surplus"); wf_y.append(None); wf_measure.append("total"); wf_text.append(f"₹{surplus_val:,.0f}")

    fig_wf = go.Figure(go.Waterfall(
        x=wf_x, y=wf_y, measure=wf_measure,
        textposition="outside", text=wf_text,
        textfont=dict(size=11, color="#334155"),
        connector=dict(line=dict(color="#E2E8F0", width=1, dash="dot")),
        increasing=dict(marker=dict(color="#10B981", line=dict(width=0))),
        decreasing=dict(marker=dict(color="#EF4444", line=dict(width=0))),
        totals=dict(marker=dict(color="#3B82F6", line=dict(width=0))),
    ))
    fig_wf.update_layout(
        **CHART_DEFAULTS,
        title=dict(text="Monthly Cash Flow", font=dict(size=13, family="Inter", color="#0F172A", weight=600), x=0.02, y=0.97),
        showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=11), linecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", tickprefix="₹", tickfont=dict(size=11), zeroline=False),
    )

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig_sip, use_container_width=True, config={"displayModeBar": False})
    with c4:
        st.plotly_chart(fig_wf, use_container_width=True, config={"displayModeBar": False})


INSURANCE_DB = {
    "health": [
        {"name": "HDFC Ergo Optima Secure", "cover": "₹5L – ₹2Cr", "note": "No-claim bonus up to 100%, restore benefit included"},
        {"name": "Niva Bupa ReAssure 2.0",   "cover": "₹3L – ₹1Cr", "note": "Unlimited restore, zero room-rent restrictions"},
        {"name": "Star Health Comprehensive", "cover": "₹5L – ₹1Cr", "note": "Wide hospital network; pre-existing covered after 1 year"},
    ],
    "term": [
        {"name": "LIC Tech Term",              "cover": "10× Annual Income", "note": "Government-backed, highest claim settlement ratio"},
        {"name": "HDFC Life Click2Protect",    "cover": "10× Annual Income", "note": "Return-of-premium option available"},
        {"name": "ICICI Pru iProtect Smart",   "cover": "10× Annual Income", "note": "Critical illness rider included"},
    ],
}


def render_insurance(income, family_size):
    health_cover = max(500000, family_size * 300000)
    term_cover = income * 12 * 10
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:16px 20px;margin-bottom:14px;">
            <div style="font-size:11px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:#94A3B8;margin-bottom:6px;">Health Insurance</div>
            <div style="font-family:'Instrument Serif',Georgia,serif;font-size:22px;color:#0F172A;">&#8377;{health_cover/100000:.0f}L recommended cover</div>
        </div>
        """, unsafe_allow_html=True)
        for ins in INSURANCE_DB["health"]:
            st.markdown(f"""<div class="fp-ins-card">
                <div class="fp-ins-name">{ins['name']}</div>
                <div class="fp-ins-detail">{ins['note']}</div>
                <div class="fp-ins-cover">{ins['cover']}</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:16px 20px;margin-bottom:14px;">
            <div style="font-size:11px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:#94A3B8;margin-bottom:6px;">Term Life Insurance</div>
            <div style="font-family:'Instrument Serif',Georgia,serif;font-size:22px;color:#0F172A;">&#8377;{term_cover/100000:.0f}L recommended cover</div>
        </div>
        """, unsafe_allow_html=True)
        for ins in INSURANCE_DB["term"]:
            st.markdown(f"""<div class="fp-ins-card">
                <div class="fp-ins-name">{ins['name']}</div>
                <div class="fp-ins-detail">{ins['note']}</div>
                <div class="fp-ins-cover">{ins['cover']}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURED AI PLAN RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def extract_section(text, keywords):
    lines = text.split("\n")
    content = []
    capturing = False
    for line in lines:
        lower = line.lower().strip()
        is_heading = line.strip().startswith("#") or (line.strip().startswith("**") and line.strip().endswith("**"))
        if is_heading and any(k in lower for k in keywords):
            capturing = True
            continue
        if capturing:
            if is_heading and not any(k in lower for k in keywords):
                break
            content.append(line)
    return "\n".join(content).strip()


def bullets_from_text(text, max_items=5):
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        is_bullet = (
            stripped.startswith("-") or
            stripped.startswith("•") or
            (stripped.startswith("*") and not stripped.startswith("**")) or
            (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in ".)")
        )
        if not is_bullet:
            continue
        clean = stripped.lstrip("-•*123456789.) ").strip()
        if 15 < len(clean) < 180:
            items.append(clean)
        if len(items) >= max_items:
            break
    return items


def render_structured_plan(full_text, fd):
    income         = fd["income"]
    total_emi      = fd["total_emi"]
    medicine_avg   = fd["medicine_avg"]
    total_misc_avg = fd["total_misc_avg"]
    disposable     = fd["disposable"]
    family_size    = fd["family_size"]
    location       = fd["location"]
    goals          = fd.get("goals", [])

    surplus        = max(disposable, 0)
    emi_ratio      = (total_emi / income * 100) if income > 0 else 0
    savings_rate   = (surplus / income * 100) if income > 0 else 0
    expense_ratio  = ((total_emi + medicine_avg + total_misc_avg) / income * 100) if income > 0 else 0
    sip_amount     = max(int(surplus * 0.30 / 500) * 500, 1000)
    ef_target      = family_size * 15000 * 6
    ef_monthly     = max(int(surplus * 0.20 / 500) * 500, 500)
    ef_months      = int(ef_target / max(ef_monthly, 1))
    tax_saving     = min(int((150000 + 50000) * 0.30), 60000)
    sip_5yr        = int(sip_amount * (((1 + 0.12/12)**(60) - 1) / (0.12/12)))
    ppf_amount     = min(max(int(surplus * 0.10 / 500) * 500, 500), 12500)
    fd_amount      = max(int(surplus * 0.10 / 500) * 500, 500)
    nps_amount     = min(max(int(surplus * 0.05 / 500) * 500, 500), 4167)

    health_text = extract_section(full_text, ["health assessment", "financial health"])
    budget_text = extract_section(full_text, ["budget", "50/30/20", "optimization"])
    invest_text = extract_section(full_text, ["investment", "allocation", "sip", "mutual"])
    ef_text     = extract_section(full_text, ["emergency fund", "emergency"])
    tax_text    = extract_section(full_text, ["tax", "80c", "deduction"])
    goal_text   = extract_section(full_text, ["goal", "planning"])
    action_text = extract_section(full_text, ["action", "step", "this week", "this month"])

    # ── Section nav ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="plan-nav">
        <span style="font-size:11px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:#94A3B8;margin-right:4px;align-self:center;">Jump to</span>
        <span class="plan-nav-pill">&#127973; Health Assessment</span>
        <span class="plan-nav-pill">&#128176; Budget</span>
        <span class="plan-nav-pill">&#128200; Investments</span>
        <span class="plan-nav-pill">&#128737; Emergency Fund</span>
        <span class="plan-nav-pill">&#127968; Insurance</span>
        <span class="plan-nav-pill">&#128203; Tax</span>
        <span class="plan-nav-pill">&#127919; Goals</span>
        <span class="plan-nav-pill">&#9889; Action Plan</span>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 1. IMMEDIATE ACTION PLAN
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="fp-section-header" style="margin-top:4px;">
        <span class="fp-section-title">&#9889; Immediate Action Plan</span>
        <span class="fp-section-meta">Your 3-phase roadmap</span>
    </div>
    """, unsafe_allow_html=True)

    short_goals = []
    long_goals  = []
    goal_cost_map = {
        "House": ("&#8377;50L target", 5000000),
        "Car": ("&#8377;8L target", 800000),
        "Child Education": ("&#8377;20L target", 2000000),
        "Retirement": ("&#8377;1Cr+ target", 10000000),
        "International Travel": ("&#8377;3L target", 300000),
        "Emergency Fund": (f"&#8377;{ef_target/100000:.0f}L target", ef_target),
    }
    for g in goals:
        cost_label, cost = goal_cost_map.get(g, (g, 1000000))
        monthly = int(cost / 120)
        if cost <= 1000000:
            short_goals.append(f"{g} — &#8377;{monthly:,}/mo")
        else:
            long_goals.append(f"{g} — &#8377;{monthly:,}/mo")

    phase1_items = [
        (f"Start SIP — &#8377;{sip_amount:,}/month", "now"),
        (f"Open Emergency Fund account — &#8377;{ef_monthly:,}/mo", "now"),
    ]
    if emi_ratio > 25:
        phase1_items.append(("Review & refinance high-interest loans", "now"))
    if income * 0.12 > 100000:
        phase1_items.append(("Set up PPF contribution", "now"))

    phase2_items = [
        (f"Emergency fund target: &#8377;{ef_target/100000:.0f}L in {ef_months} months", "soon"),
        ("Max 80C deduction — &#8377;1,50,000/year", "soon"),
        ("NPS Tier-I for extra &#8377;50,000 deduction", "soon"),
    ] + [(g, "soon") for g in short_goals]

    phase3_items = [
        (f"SIP corpus target: &#8377;{sip_5yr/100000:.0f}L in 5 years", "future"),
        ("Annual portfolio review & rebalancing", "future"),
    ] + [(g, "future") for g in long_goals]

    def render_phase_items(items, phase_type):
        html = '<div class="phase-items">'
        for label, _ in items:
            item_cls = "phase-item-now" if phase_type == "now" else "phase-item"
            check_cls = "check-" + phase_type
            html += (
                '<div class="phase-item ' + item_cls + '">'
                '<span class="phase-item-check ' + check_cls + '">&#10003;</span>'
                + label +
                '</div>'
            )
        html += '</div>'
        return html

    action_card = (
        '<div class="plan-card card-green">'
        '<ul class="action-timeline">'
        '<li><div class="action-phase">'
        '<div class="action-phase-left">'
        '<div class="phase-dot phase-dot-now">1</div>'
        '<div class="phase-line"></div>'
        '</div>'
        '<div class="action-phase-right">'
        '<div class="phase-label phase-label-now">This Month</div>'
        + render_phase_items(phase1_items, "now") +
        '</div></div></li>'
        '<li><div class="action-phase">'
        '<div class="action-phase-left">'
        '<div class="phase-dot phase-dot-soon">2</div>'
        '<div class="phase-line"></div>'
        '</div>'
        '<div class="action-phase-right">'
        '<div class="phase-label phase-label-soon">Next 6 Months</div>'
        + render_phase_items(phase2_items, "soon") +
        '</div></div></li>'
        '<li><div class="action-phase">'
        '<div class="action-phase-left">'
        '<div class="phase-dot phase-dot-future">3</div>'
        '</div>'
        '<div class="action-phase-right">'
        '<div class="phase-label phase-label-future">1&#8211;3 Years</div>'
        + render_phase_items(phase3_items, "future") +
        '</div></div></li>'
        '</ul></div>'
    )
    st.markdown(action_card, unsafe_allow_html=True)
    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 2. FINANCIAL HEALTH ASSESSMENT
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="fp-section-header">
        <span class="fp-section-title">&#127973; Financial Health Assessment</span>
        <span class="fp-section-meta">Diagnosis across key metrics</span>
    </div>
    """, unsafe_allow_html=True)

    emi_status = "&#127823; Healthy" if emi_ratio < 10 else ("&#127825; Moderate" if emi_ratio < 25 else "&#128308; High")
    sav_status = "&#127823; Excellent" if savings_rate >= 20 else ("&#127825; Moderate" if savings_rate >= 10 else "&#128308; Low")
    exp_status = "&#127823; Lean" if expense_ratio < 60 else ("&#127825; Moderate" if expense_ratio < 80 else "&#128308; High")

    health_insights = bullets_from_text(health_text, 4)
    if not health_insights:
        health_insights = [
            f"EMI-to-income ratio is {emi_ratio:.1f}% — benchmark is under 25%",
            f"Savings rate of {savings_rate:.1f}% against 20% recommended target",
            f"Monthly surplus of &#8377;{surplus:,.0f} available for wealth creation",
        ]

    dot_cls = "dot-green" if savings_rate >= 20 else "dot-yellow"
    insights_html = "".join(
        '<li><span class="insight-dot ' + dot_cls + '"></span>' + i + '</li>'
        for i in health_insights
    )

    if savings_rate < 10 or emi_ratio > 25:
        priority_cls = "priority-high"
        priority_lbl = "Needs Focus"
    elif savings_rate >= 20:
        priority_cls = "priority-low"
        priority_lbl = "On Track"
    else:
        priority_cls = "priority-medium"
        priority_lbl = "Improving"

    emi_alert_pill = (
        '<span class="impact-pill impact-alert">EMI burden above threshold</span>'
        if emi_ratio > 25 else
        '<span class="impact-pill">EMI within safe range</span>'
    )

    health_card = (
        '<div class="plan-card card-blue">'
        '<div class="plan-card-header">'
        '<div class="plan-card-icon icon-bg-blue">&#127973;</div>'
        '<div class="plan-card-title-block">'
        '<div class="plan-card-title">Health Snapshot</div>'
        f'<div class="plan-card-summary">Your finances in {location} — {family_size}-member household</div>'
        '</div>'
        f'<span class="plan-priority-badge {priority_cls}">{priority_lbl}</span>'
        '</div>'
        '<div class="plan-two-col">'
        '<div class="plan-metric-box">'
        '<div class="plan-metric-label">EMI Burden</div>'
        f'<div class="plan-metric-value">{emi_ratio:.1f}%</div>'
        f'<div class="plan-metric-sub">{emi_status} &middot; target &lt;25%</div>'
        '</div>'
        '<div class="plan-metric-box">'
        '<div class="plan-metric-label">Savings Rate</div>'
        f'<div class="plan-metric-value">{savings_rate:.1f}%</div>'
        f'<div class="plan-metric-sub">{sav_status} &middot; target &ge;20%</div>'
        '</div>'
        '<div class="plan-metric-box">'
        '<div class="plan-metric-label">Expense Ratio</div>'
        f'<div class="plan-metric-value">{expense_ratio:.1f}%</div>'
        f'<div class="plan-metric-sub">{exp_status} &middot; target &lt;80%</div>'
        '</div>'
        '<div class="plan-metric-box">'
        '<div class="plan-metric-label">Monthly Surplus</div>'
        f'<div class="plan-metric-value">&#8377;{surplus/1000:.0f}K</div>'
        '<div class="plan-metric-sub">Available for investment</div>'
        '</div>'
        '</div>'
        f'<ul class="plan-insights">{insights_html}</ul>'
        '<div class="plan-impact-row">'
        f'<span class="impact-pill">&#8377;{surplus:,.0f}/mo investable surplus</span>'
        + emi_alert_pill +
        '</div>'
        '</div>'
    )
    st.markdown(health_card, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 3. BUDGET OPTIMIZATION  ← THE FIXED SECTION
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="fp-section-header" style="margin-top:32px;">
        <span class="fp-section-title">&#128176; Budget Optimization</span>
        <span class="fp-section-meta">50/30/20 framework applied</span>
    </div>
    """, unsafe_allow_html=True)

    needs_actual   = total_emi + total_misc_avg + medicine_avg
    needs_rec      = income * 0.50
    wants_rec      = income * 0.30
    savings_rec    = income * 0.20
    wants_actual   = min(max(surplus * 0.30, 0), wants_rec)
    savings_actual = max(surplus - wants_actual, 0)

    def alloc_row(label, actual, color):
        pct = min(actual / max(income, 1) * 100, 100)
        return (
            '<div class="alloc-row">'
            '<div class="alloc-label">' + label + '</div>'
            '<div class="alloc-track">'
            '<div class="alloc-fill" style="width:' + f"{pct:.1f}" + '%;background:' + color + ';"></div>'
            '</div>'
            '<div class="alloc-amount">&#8377;' + f"{actual:,.0f}" + '</div>'
            '</div>'
        )

    needs_gap  = needs_actual - needs_rec
    if abs(needs_gap) > 0.5:
        direction  = "over" if needs_gap > 0.5 else "under"
        needs_note = f"&#8377;{abs(needs_gap):,.0f} {direction} the 50% cap"
    else:
        needs_note = "exactly at target"

    budget_insights = [
        f"Needs (EMI + healthcare + living): &#8377;{needs_actual:,.0f}/mo — recommended cap &#8377;{needs_rec:,.0f} ({needs_note})",
        f"Wants (discretionary spending): budget up to &#8377;{wants_rec:,.0f}/month from surplus",
        f"Savings target: &#8377;{savings_rec:,.0f}/month (20%) — currently directing &#8377;{savings_actual:,.0f} to wealth creation",
    ]
    bi_html = "".join(
        '<li><span class="insight-dot dot-blue"></span>' + i + '</li>'
        for i in budget_insights
    )
    rows_html = (
        alloc_row("Needs (50% rec.)",   needs_actual,   "#3B82F6")
        + alloc_row("Wants (30% rec.)",   wants_actual,   "#8B5CF6")
        + alloc_row("Savings (20% rec.)", savings_actual, "#10B981")
    )

    budget_card = (
        '<div class="plan-card card-teal">'
        '<div class="plan-card-header">'
        '<div class="plan-card-icon icon-bg-teal">&#128176;</div>'
        '<div class="plan-card-title-block">'
        '<div class="plan-card-title">50 / 30 / 20 Budget Split</div>'
        f'<div class="plan-card-summary">Actual vs recommended allocation of &#8377;{income:,.0f}/month</div>'
        '</div>'
        '</div>'
        + rows_html
        + f'<ul class="plan-insights" style="margin-top:16px;">{bi_html}</ul>'
        + '<div class="plan-impact-row">'
        + f'<span class="impact-pill">&#8377;{savings_actual:,.0f} directed to savings</span>'
        + f'<span class="impact-pill impact-info">&#8377;{savings_rec:,.0f} is recommended minimum</span>'
        + '</div>'
        + '</div>'
    )
    st.markdown(budget_card, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 4. INVESTMENT STRATEGY
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="fp-section-header" style="margin-top:32px;">
        <span class="fp-section-title">&#128200; Investment Strategy</span>
        <span class="fp-section-meta">Instrument-level allocation</span>
    </div>
    """, unsafe_allow_html=True)

    total_invest = sip_amount + ppf_amount + fd_amount + nps_amount

    col_a, col_b = st.columns(2)
    with col_a:
        invest_insights = bullets_from_text(invest_text, 4)
        if not invest_insights:
            invest_insights = [
                f"SIP in equity mutual funds: &#8377;{sip_amount:,}/month (60% large-cap, 30% flexi-cap, 10% international)",
                f"PPF contribution: &#8377;{ppf_amount:,}/month — tax-free at 7.1% p.a.",
                f"FD / Liquid fund for short-term goals: &#8377;{fd_amount:,}/month",
                f"NPS Tier-I for retirement + &#8377;50K extra 80CCD deduction: &#8377;{nps_amount:,}/month",
            ]
        ii_html = "".join(
            '<li><span class="insight-dot dot-green"></span>' + i + '</li>'
            for i in invest_insights
        )
        invest_rows = (
            alloc_row("SIP — Equity MF",    sip_amount,  "#10B981")
            + alloc_row("PPF",              ppf_amount,  "#3B82F6")
            + alloc_row("FD / Liquid Fund", fd_amount,   "#F59E0B")
            + alloc_row("NPS Tier-I",       nps_amount,  "#8B5CF6")
        )
        invest_card = (
            '<div class="plan-card card-green" style="height:100%;">'
            '<div class="plan-card-header">'
            '<div class="plan-card-icon icon-bg-green">&#128200;</div>'
            '<div class="plan-card-title-block">'
            '<div class="plan-card-title">Monthly Investment Plan</div>'
            f'<div class="plan-card-summary">&#8377;{total_invest:,}/month total deployment</div>'
            '</div>'
            '<span class="plan-priority-badge priority-high">Priority 1</span>'
            '</div>'
            + invest_rows
            + f'<ul class="plan-insights" style="margin-top:16px;">{ii_html}</ul>'
            + '</div>'
        )
        st.markdown(invest_card, unsafe_allow_html=True)

    with col_b:
        sip_3yr  = int(sip_amount * (((1 + 0.12/12)**(36)  - 1) / (0.12/12)))
        sip_10yr = int(sip_amount * (((1 + 0.12/12)**(120) - 1) / (0.12/12)))
        corpus_card = (
            '<div class="plan-card card-purple" style="height:100%;">'
            '<div class="plan-card-header">'
            '<div class="plan-card-icon icon-bg-purple">&#128302;</div>'
            '<div class="plan-card-title-block">'
            '<div class="plan-card-title">Projected Corpus Growth</div>'
            f'<div class="plan-card-summary">SIP of &#8377;{sip_amount:,}/month at 12% CAGR</div>'
            '</div>'
            '</div>'
            '<div class="plan-two-col" style="margin-bottom:12px;">'
            '<div class="plan-metric-box">'
            '<div class="plan-metric-label">3-Year Corpus</div>'
            f'<div class="plan-metric-value">&#8377;{sip_3yr/100000:.1f}L</div>'
            '<div class="plan-metric-sub">@ 12% p.a.</div>'
            '</div>'
            '<div class="plan-metric-box">'
            '<div class="plan-metric-label">5-Year Corpus</div>'
            f'<div class="plan-metric-value">&#8377;{sip_5yr/100000:.1f}L</div>'
            '<div class="plan-metric-sub">@ 12% p.a.</div>'
            '</div>'
            '<div class="plan-metric-box">'
            '<div class="plan-metric-label">10-Year Corpus</div>'
            f'<div class="plan-metric-value">&#8377;{sip_10yr/100000:.1f}L</div>'
            '<div class="plan-metric-sub">@ 12% p.a.</div>'
            '</div>'
            '<div class="plan-metric-box">'
            '<div class="plan-metric-label">Annual Return</div>'
            '<div class="plan-metric-value">12%</div>'
            '<div class="plan-metric-sub">CAGR (historical avg)</div>'
            '</div>'
            '</div>'
            '<div class="plan-actions">'
            '<span class="action-chip chip-green">&#10003; SIP auto-debit on salary day</span>'
            '<span class="action-chip chip-blue">&#10003; Step-up 10% annually</span>'
            '<span class="action-chip">Review every 6 months</span>'
            '</div>'
            '<div class="plan-impact-row">'
            f'<span class="impact-pill">+&#8377;{sip_5yr/100000:.1f}L projected in 5 years</span>'
            f'<span class="impact-pill impact-info">vs &#8377;{sip_amount*60/100000:.1f}L in savings deposit</span>'
            '</div>'
            '</div>'
        )
        st.markdown(corpus_card, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 5. EMERGENCY FUND
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="fp-section-header" style="margin-top:32px;">
        <span class="fp-section-title">&#128737; Emergency Fund Plan</span>
        <span class="fp-section-meta">Your financial safety net</span>
    </div>
    """, unsafe_allow_html=True)

    ef_insights = bullets_from_text(ef_text, 3)
    if not ef_insights:
        ef_insights = [
            f"Target corpus: &#8377;{ef_target/100000:.0f}L ({family_size * 6} months of fixed expenses)",
            f"Contribute &#8377;{ef_monthly:,}/month to liquid mutual fund or high-yield savings",
            f"Achievable in approximately {ef_months} months at current surplus",
        ]
    efi_html = "".join(
        '<li><span class="insight-dot dot-green"></span>' + i + '</li>'
        for i in ef_insights
    )

    ef_priority_cls = "priority-high" if ef_months > 24 else "priority-medium"
    ef_card = (
        '<div class="plan-card card-orange">'
        '<div class="plan-card-header">'
        '<div class="plan-card-icon icon-bg-orange">&#128737;</div>'
        '<div class="plan-card-title-block">'
        '<div class="plan-card-title">Emergency Fund</div>'
        f'<div class="plan-card-summary">Build {family_size * 6} months of fixed expenses as liquid reserve</div>'
        '</div>'
        f'<span class="plan-priority-badge {ef_priority_cls}">{ef_months} months away</span>'
        '</div>'
        '<div class="plan-two-col">'
        '<div class="plan-metric-box">'
        '<div class="plan-metric-label">Target Corpus</div>'
        f'<div class="plan-metric-value">&#8377;{ef_target/100000:.0f}L</div>'
        f'<div class="plan-metric-sub">{family_size * 6} months of expenses</div>'
        '</div>'
        '<div class="plan-metric-box">'
        '<div class="plan-metric-label">Monthly Contribution</div>'
        f'<div class="plan-metric-value">&#8377;{ef_monthly:,}</div>'
        '<div class="plan-metric-sub">20% of surplus</div>'
        '</div>'
        '</div>'
        f'<ul class="plan-insights">{efi_html}</ul>'
        '<div class="plan-actions">'
        '<span class="action-chip chip-green">Liquid Mutual Fund</span>'
        '<span class="action-chip chip-blue">High-Yield Savings (3.5&#8211;4%)</span>'
        '<span class="action-chip">Keep separate from investments</span>'
        '</div>'
        '<div class="plan-impact-row">'
        f'<span class="impact-pill">Achievable in {ef_months} months</span>'
        f'<span class="impact-pill impact-info">&#8377;{ef_monthly:,}/month needed</span>'
        '</div>'
        '</div>'
    )
    st.markdown(ef_card, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 6. TAX OPTIMIZATION
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="fp-section-header" style="margin-top:32px;">
        <span class="fp-section-title">&#128203; Tax Optimization</span>
        <span class="fp-section-meta">Maximize legal deductions under Income Tax Act</span>
    </div>
    """, unsafe_allow_html=True)

    tax_rows_data = [
        ("Section 80C",        "ELSS + EPF + PPF + Life Insurance",   "&#8377;1,50,000",   f"Save &#8377;{int(150000*0.30):,}"),
        ("Section 80D",        "Health Insurance Premium",            "&#8377;25,000&#8211;&#8377;50,000", f"Save &#8377;{int(25000*0.30):,}"),
        ("Section 80CCD(1B)",  "NPS Tier-I (extra deduction)",        "&#8377;50,000",     f"Save &#8377;{int(50000*0.30):,}"),
        ("Section 24(b)",      "Home Loan Interest (if applicable)",  "&#8377;2,00,000",   f"Save &#8377;{int(200000*0.30):,}"),
    ]
    tax_rows_html = "".join(
        '<div class="tax-row">'
        '<span class="tax-section">' + s + '</span>'
        '<span style="font-size:12px;color:#64748B;">' + inst + '</span>'
        '<span class="tax-limit">' + lim + '</span>'
        '<span class="tax-saving">' + sav + '</span>'
        '</div>'
        for s, inst, lim, sav in tax_rows_data
    )

    tax_insights = bullets_from_text(tax_text, 3)
    if not tax_insights:
        tax_insights = [
            "Maximize 80C limit of &#8377;1,50,000 via ELSS, EPF & PPF",
            "NPS 80CCD(1B) gives additional &#8377;50,000 deduction beyond 80C cap",
            f"Total potential tax saving: &#8377;{tax_saving:,}+ per year at 30% bracket",
        ]
    ti_html = "".join(
        '<li><span class="insight-dot dot-blue"></span>' + i + '</li>'
        for i in tax_insights
    )

    tax_card = (
        '<div class="plan-card card-indigo">'
        '<div class="plan-card-header">'
        '<div class="plan-card-icon icon-bg-indigo">&#128203;</div>'
        '<div class="plan-card-title-block">'
        '<div class="plan-card-title">Tax-Saving Opportunities</div>'
        '<div class="plan-card-summary">Reduce tax liability using available deductions</div>'
        '</div>'
        f'<span class="plan-priority-badge priority-medium">Save &#8377;{tax_saving:,}+/yr</span>'
        '</div>'
        + tax_rows_html
        + f'<ul class="plan-insights" style="margin-top:16px;">{ti_html}</ul>'
        + '<div class="plan-impact-row">'
        + f'<span class="impact-pill">Save &#8377;{tax_saving:,}+ in taxes annually</span>'
        + '<span class="impact-pill impact-info">80C + 80CCD(1B) = &#8377;2L deduction</span>'
        + '</div>'
        + '</div>'
    )
    st.markdown(tax_card, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 7. GOALS
    # ══════════════════════════════════════════════════════════════════════════
    if goals:
        st.markdown("""
        <div class="fp-section-header" style="margin-top:32px;">
            <span class="fp-section-title">&#127919; Goal-Based Planning</span>
            <span class="fp-section-meta">Savings targets for each financial goal</span>
        </div>
        """, unsafe_allow_html=True)

        goal_cost_full = {
            "House":               (5000000,  "Property + registration",    120),
            "Car":                 (800000,   "On-road price estimate",      36),
            "Child Education":     (2000000,  "Higher education fund",      180),
            "Retirement":          (10000000, "Post-retirement corpus",     300),
            "International Travel":(300000,   "Trip + forex estimate",       24),
            "Emergency Fund":      (ef_target, "6-month expense buffer",  ef_months),
        }

        goal_rows_html = ""
        total_monthly_needed = sum(
            round(goal_cost_full.get(g, (1000000, g, 60))[0] / max(goal_cost_full.get(g, (1000000, g, 60))[2], 1))
            for g in goals
        )
        for g in goals:
            cost, desc, horizon = goal_cost_full.get(g, (1000000, g, 60))
            monthly = round(cost / max(horizon, 1))
            feasibility = min(int(surplus / max(monthly, 1) * 100), 100) if monthly > 0 else 100
            feasibility_color = "#10B981" if feasibility >= 80 else ("#F59E0B" if feasibility >= 40 else "#EF4444")
            feasibility_label = f"{feasibility}% coverable"
            goal_rows_html += (
                '<div class="goal-progress-row">'
                f'<div class="goal-name">{g}</div>'
                '<div class="goal-track-wrap">'
                '<div class="goal-track">'
                f'<div class="goal-fill" style="width:{feasibility}%;background:{feasibility_color};"></div>'
                '</div>'
                f'<div class="goal-meta">&#8377;{cost/100000:.0f}L target &middot; {horizon} months &middot; {desc} &middot; {feasibility_label}</div>'
                '</div>'
                f'<div class="goal-monthly">&#8377;{monthly:,}/mo</div>'
                '</div>'
            )

        goals_exceed = total_monthly_needed > surplus
        exceed_pill = (
            '<span class="impact-pill impact-alert">Goals exceed current surplus — prioritize or extend timelines</span>'
            if goals_exceed else
            '<span class="impact-pill">Surplus covers all goal contributions</span>'
        )

        goals_card = (
            '<div class="plan-card card-rose">'
            '<div class="plan-card-header">'
            '<div class="plan-card-icon icon-bg-rose">&#127919;</div>'
            '<div class="plan-card-title-block">'
            '<div class="plan-card-title">Your Financial Goals</div>'
            f'<div class="plan-card-summary">{len(goals)} goals — monthly allocation needed from surplus of &#8377;{surplus:,.0f}</div>'
            '</div>'
            '</div>'
            '<div style="display:flex;justify-content:space-between;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;color:#94A3B8;padding-bottom:8px;border-bottom:1px solid #F1F5F9;margin-bottom:4px;">'
            '<span>Goal</span>'
            '<span style="flex:1;text-align:right;margin-right:90px;">Progress Feasibility</span>'
            '<span>Monthly</span>'
            '</div>'
            + goal_rows_html
            + '<div class="plan-impact-row">'
            + f'<span class="impact-pill">&#8377;{total_monthly_needed:,}/mo total needed across all goals</span>'
            + exceed_pill
            + '</div>'
            + '</div>'
        )
        st.markdown(goals_card, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 8. FULL AI REPORT — collapsible
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)
    with st.expander("&#128196; View full AI analysis report", expanded=False):
        st.markdown("""
        <div style="background:#F8FAFC;border-radius:8px;padding:4px 8px;margin-bottom:12px;font-size:12px;color:#94A3B8;">
            Raw analysis from LLaMA 3.3 70B &middot; Personalized for your profile
        </div>
        """, unsafe_allow_html=True)
        lines = full_text.split("\n")
        cleaned = []
        for line in lines:
            if line.startswith("### "):
                cleaned.append(f"\n**{line[4:]}**")
            elif line.startswith("## "):
                cleaned.append(f"\n**{line[3:]}**")
            elif line.startswith("# "):
                cleaned.append(f"\n**{line[2:]}**")
            else:
                cleaned.append(line)
        st.markdown("\n".join(cleaned))


# ══════════════════════════════════════════════════════════════════════════════
# LANDING
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.markdown('<div class="fp-page">', unsafe_allow_html=True)

    st.markdown("""
    <div class="fp-hero">
        <div class="fp-hero-eyebrow">AI-Powered Financial Intelligence</div>
        <div class="fp-hero-title">Your personal <em>financial advisor</em>,<br>built on data.</div>
        <div class="fp-hero-sub">
            Get a personalized financial health score, investment plan, and AI-driven
            recommendations — calibrated to your income, city, and goals.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if st.button("Get my financial analysis", type="primary", use_container_width=True):
            st.session_state.page = "form"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    features = [
        ("Financial Health Score", "A composite score across EMI burden, savings rate, emergency fund readiness, and insurance coverage."),
        ("AI Investment Plan", "Instrument-level recommendations — SIP amounts, PPF, NPS, FD allocations — anchored to your surplus."),
        ("Goal-Based Planner", "Exact monthly savings needed for every goal. Simulate income changes and loan closures with What-If scenarios."),
    ]
    for col, (title, desc) in zip([c1, c2, c3], features):
        with col:
            st.markdown(f"""
            <div class="fp-form-block" style="height:100%;">
                <div class="fp-form-block-title">{title}</div>
                <div style="height:1px;background:#F1F5F9;margin:10px 0;"></div>
                <div style="font-size:13px;color:#64748B;line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="border:1px solid #E2E8F0;border-radius:10px;padding:18px 32px;display:flex;align-items:center;justify-content:center;gap:48px;flex-wrap:wrap;background:#FFFFFF;">
        <span style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#CBD5E1;">Trusted insights from</span>
        <span style="font-size:13px;font-weight:600;color:#94A3B8;">RBI Guidelines</span>
        <span style="font-size:13px;font-weight:600;color:#94A3B8;">SEBI Frameworks</span>
        <span style="font-size:13px;font-weight:600;color:#94A3B8;">IRDAI Standards</span>
        <span style="font-size:13px;font-weight:600;color:#94A3B8;">Income Tax Act</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FORM
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "form":

    st.markdown('<div class="fp-page">', unsafe_allow_html=True)

    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Back"):
            st.session_state.page = "landing"
            st.rerun()
    with col_title:
        st.markdown("""
        <div style="padding:32px 0 24px;">
            <div style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#94A3B8;margin-bottom:8px;">New Analysis</div>
            <div style="font-family:'Instrument Serif',Georgia,serif;font-size:28px;color:#0F172A;letter-spacing:-0.02em;">Tell us about your finances</div>
            <div style="font-size:13px;color:#94A3B8;margin-top:6px;">All figures are used only to generate your report. Nothing is stored.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="fp-step-label">Step 1 — Household</div>', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block">', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block-title">Basic Information</div><div class="fp-form-block-sub">Your take-home income and household details.</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_income = st.number_input("Monthly in-hand income (&#8377;)", min_value=0, step=1000, placeholder="e.g. 90,000")
    with col2:
        family_size = st.number_input("Family members", min_value=1, max_value=20, value=3)
    with col3:
        location = st.text_input("City", placeholder="e.g. Mumbai, Bangalore, Patna")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fp-step-label">Step 2 — Loan Repayments</div>', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block">', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block-title">EMIs</div><div class="fp-form-block-sub">Home loan, car loan, personal loan, education loan — list each separately.</div>', unsafe_allow_html=True)

    def add_emi(): st.session_state.emis.append({"name": "", "amount": 0})
    def remove_emi(i): st.session_state.emis.pop(i)

    for i, emi in enumerate(st.session_state.emis):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.session_state.emis[i]["name"] = st.text_input(
                "Loan name", value=emi["name"], placeholder="e.g. Home Loan",
                key=f"emi_name_{i}", label_visibility="collapsed" if i > 0 else "visible"
            )
        with c2:
            st.session_state.emis[i]["amount"] = st.number_input(
                "Monthly (&#8377;)", value=emi["amount"], min_value=0, step=500,
                key=f"emi_amt_{i}", label_visibility="collapsed" if i > 0 else "visible"
            )
        with c3:
            st.write(""); st.write("")
            if len(st.session_state.emis) > 1 and st.button("Remove", key=f"del_emi_{i}"):
                remove_emi(i); st.rerun()
    st.button("Add EMI", on_click=add_emi)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fp-step-label">Step 3 — Healthcare</div>', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block">', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block-title">Medicine & Healthcare</div><div class="fp-form-block-sub">Enter your typical monthly range.</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        medicine_min = st.number_input("Minimum monthly (&#8377;)", min_value=0, step=100, value=0)
    with col2:
        medicine_max = st.number_input("Maximum monthly (&#8377;)", min_value=0, step=100, value=0)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fp-step-label">Step 4 — Monthly Expenses</div>', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block">', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block-title">Bills & Living Costs</div><div class="fp-form-block-sub">Rent, electricity, groceries, fuel, subscriptions — list each expense with a min and max.</div>', unsafe_allow_html=True)

    def add_misc(): st.session_state.misc.append({"name": "", "min": 0, "max": 0})
    def remove_misc(i): st.session_state.misc.pop(i)

    for i, item in enumerate(st.session_state.misc):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        with c1:
            st.session_state.misc[i]["name"] = st.text_input(
                "Expense name", value=item["name"], placeholder="e.g. Rent",
                key=f"misc_name_{i}", label_visibility="collapsed" if i > 0 else "visible"
            )
        with c2:
            st.session_state.misc[i]["min"] = st.number_input(
                "Min (&#8377;)", value=item["min"], min_value=0, step=100,
                key=f"misc_min_{i}", label_visibility="collapsed" if i > 0 else "visible"
            )
        with c3:
            st.session_state.misc[i]["max"] = st.number_input(
                "Max (&#8377;)", value=item["max"], min_value=0, step=100,
                key=f"misc_max_{i}", label_visibility="collapsed" if i > 0 else "visible"
            )
        with c4:
            st.write(""); st.write("")
            if len(st.session_state.misc) > 1 and st.button("Remove", key=f"del_misc_{i}"):
                remove_misc(i); st.rerun()
    st.button("Add Expense", on_click=add_misc)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fp-step-label">Step 5 — Goals</div>', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block">', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block-title">Financial Goals</div><div class="fp-form-block-sub">Select everything you are working towards. The AI tailors recommendations around each goal.</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        g_house = st.checkbox("Buy a House")
        g_car   = st.checkbox("Buy a Car")
    with g2:
        g_edu    = st.checkbox("Child's Education")
        g_retire = st.checkbox("Retirement Planning")
    with g3:
        g_trip      = st.checkbox("International Travel")
        g_emergency = st.checkbox("Build Emergency Fund")
    st.markdown('</div>', unsafe_allow_html=True)

    goal_labels = []
    if g_house:     goal_labels.append("House")
    if g_car:       goal_labels.append("Car")
    if g_edu:       goal_labels.append("Child Education")
    if g_retire:    goal_labels.append("Retirement")
    if g_trip:      goal_labels.append("International Travel")
    if g_emergency: goal_labels.append("Emergency Fund")

    st.markdown('<div class="fp-step-label">Step 6 — Scenario Planning (Optional)</div>', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block">', unsafe_allow_html=True)
    st.markdown('<div class="fp-form-block-title">What-If Simulator</div><div class="fp-form-block-sub">Adjust these sliders to explore different financial scenarios before running your analysis.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        income_change_pct = st.slider("Income change (%)", min_value=-30, max_value=50, value=0, step=5, help="Simulate a raise, promotion, or pay cut")
    with c2:
        emi_override = st.number_input("Override total EMI (&#8377;) — 0 uses actual", min_value=0, step=500, value=0, help="Simulate closing a loan or taking a new one")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate my financial plan", type="primary", use_container_width=True):
            if monthly_income <= 0:
                st.error("Please enter your monthly income.")
            elif not location.strip():
                st.error("Please enter your city.")
            else:
                sim_income = monthly_income * (1 + income_change_pct / 100)
                total_emi_raw = sum(e["amount"] for e in st.session_state.emis if e["amount"] > 0)
                total_emi = emi_override if emi_override > 0 else total_emi_raw
                medicine_avg = (medicine_min + medicine_max) / 2
                total_misc_avg = sum((m["min"] + m["max"]) / 2 for m in st.session_state.misc if m["min"] > 0 or m["max"] > 0)
                total_fixed = total_emi + medicine_avg + total_misc_avg
                disposable = sim_income - total_fixed

                emi_details = "\n".join(f"  - {e['name'] or 'Loan'}: &#8377;{e['amount']:,}" for e in st.session_state.emis if e["amount"] > 0) or "  None"
                misc_details = "\n".join(f"  - {m['name'] or 'Expense'}: &#8377;{m['min']:,}–&#8377;{m['max']:,}" for m in st.session_state.misc if m["min"] > 0 or m["max"] > 0) or "  None"

                st.session_state.financial_data = {
                    "income": sim_income, "original_income": monthly_income,
                    "income_change_pct": income_change_pct,
                    "total_emi": total_emi, "medicine_avg": medicine_avg,
                    "total_misc_avg": total_misc_avg, "total_fixed": total_fixed,
                    "disposable": disposable, "family_size": family_size,
                    "location": location, "goals": goal_labels,
                    "emi_details": emi_details, "misc_details": misc_details,
                    "medicine_min": medicine_min, "medicine_max": medicine_max,
                }

                goals_str = ", ".join(goal_labels) if goal_labels else "General financial stability"
                prompt = f"""You are a senior Indian personal finance advisor at a premium wealth management firm. Generate a precise, professional financial plan.

## Client Financial Profile
- Monthly In-Hand Income: &#8377;{sim_income:,.0f}
- Location: {location}
- Family Size: {family_size} members
- Financial Goals: {goals_str}

### Loan EMIs (Total: &#8377;{total_emi:,}/month)
{emi_details}

### Healthcare Budget: &#8377;{medicine_min:,}–&#8377;{medicine_max:,}/month (avg &#8377;{medicine_avg:,.0f})

### Monthly Living Costs
{misc_details}

### Financial Summary
- Total Committed Outflows: &#8377;{total_fixed:,.0f}/month
- Estimated Monthly Surplus: &#8377;{disposable:,.0f}/month
- EMI-to-Income Ratio: {(total_emi/sim_income*100) if sim_income > 0 else 0:.1f}%

---

Generate a structured financial plan with these sections:

1. **Executive Summary** — 4 bullet points with the most critical insights and specific &#8377; figures.

2. **Financial Health Assessment** — EMI burden analysis, savings rate evaluation, emergency fund readiness.

3. **Budget Optimization** — Recommended vs actual 50/30/20 split with &#8377; amounts.

4. **Emergency Fund Plan** — Target corpus, monthly contribution, timeline to achieve it.

5. **Investment Allocation** — Specific instruments with exact &#8377; amounts:
   - SIP in equity mutual funds (specify fund categories)
   - PPF / EPF contribution
   - FD / liquid fund for short-term
   - NPS if applicable

6. **Goal Planning** — For each goal in: {goals_str}
   - Estimated cost at today's value
   - Monthly savings requirement
   - Recommended instruments

7. **Tax Optimization** — 80C, 80D, NPS 80CCD opportunities with exact amounts.

8. **3-Step Action Plan** — Concrete actions for this week, this month, this quarter.

Use formal financial advisory language. Reference cost of living in {location} where relevant. All amounts in &#8377;."""

                with st.spinner("Analyzing your finances and generating your plan..."):
                    try:
                        client = Groq()
                        full_response = ""
                        stream = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            max_tokens=3500,
                            messages=[{"role": "user", "content": prompt}],
                            stream=True
                        )
                        for chunk in stream:
                            delta = chunk.choices[0].delta.content or ""
                            full_response += delta
                        st.session_state.full_response = full_response
                        st.session_state.plan_generated = True
                        st.session_state.page = "results"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating plan: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "results":
    fd = st.session_state.financial_data
    income         = fd["income"]
    total_emi      = fd["total_emi"]
    medicine_avg   = fd["medicine_avg"]
    total_misc_avg = fd["total_misc_avg"]
    disposable     = fd["disposable"]
    family_size    = fd["family_size"]
    location       = fd["location"]

    st.markdown('<div class="fp-page">', unsafe_allow_html=True)

    col_back, col_header = st.columns([1, 6])
    with col_back:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Edit inputs"):
            st.session_state.page = "form"; st.rerun()
    with col_header:
        st.markdown(f"""
        <div style="padding:32px 0 16px;">
            <div style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#94A3B8;margin-bottom:8px;">Financial Report — {location}</div>
            <div style="font-family:'Instrument Serif',Georgia,serif;font-size:28px;color:#0F172A;letter-spacing:-0.02em;">Your financial health overview</div>
            <div style="font-size:13px;color:#94A3B8;margin-top:6px;">Based on &#8377;{income:,.0f}/month &middot; {family_size} family members &middot; AI-generated</div>
        </div>
        """, unsafe_allow_html=True)

    if fd["income_change_pct"] != 0:
        pct = fd["income_change_pct"]
        direction = "increase" if pct > 0 else "decrease"
        st.markdown(f"""<div class="fp-alert-banner">
            Scenario active: {abs(pct)}% income {direction} applied.
            Showing results for &#8377;{income:,.0f}/month (original: &#8377;{fd['original_income']:,}).
        </div>""", unsafe_allow_html=True)

    score, grade, grade_class, details = compute_health_score(
        income, total_emi, disposable * 0.5, medicine_avg, total_misc_avg, family_size
    )
    emi_ratio    = total_emi / income * 100 if income > 0 else 0
    savings_rate = details["savings"]["rate"]
    surplus      = disposable
    expense_ratio = ((total_emi + medicine_avg + total_misc_avg) / income * 100) if income > 0 else 0
    months_to_ef = details["emergency"]["months"]

    # ── KPI Cards ──────────────────────────────────────────────────────────
    st.markdown('<div class="fp-section">', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    def kpi_card(col, label, value, status_label, status_class):
        with col:
            st.markdown(f"""
            <div class="fp-kpi-card">
                <div class="fp-kpi-label">{label}</div>
                <div class="fp-kpi-value">{value}</div>
                <span class="fp-kpi-status {status_class}">{status_label}</span>
                <div class="fp-kpi-accent"></div>
            </div>
            """, unsafe_allow_html=True)

    kpi_card(k1, "Financial Health Score", f"{score}/100", grade, grade_class)
    sav_cls = "status-excellent" if savings_rate >= 20 else ("status-good" if savings_rate >= 10 else "status-poor")
    kpi_card(k2, "Savings Rate", f"{savings_rate:.1f}%", "Excellent" if savings_rate >= 20 else ("Moderate" if savings_rate >= 10 else "Below Target"), sav_cls)
    ef_cls  = "status-excellent" if months_to_ef <= 12 else ("status-good" if months_to_ef <= 24 else "status-fair")
    kpi_card(k3, "Emergency Fund", f"{int(months_to_ef)} mo", "On track" if months_to_ef <= 12 else ("Building" if months_to_ef <= 24 else "Needs focus"), ef_cls)
    inv_surplus = max(surplus * 0.5, 0)
    inv_cls = "status-excellent" if inv_surplus > 10000 else ("status-good" if inv_surplus > 3000 else "status-poor")
    kpi_card(k4, "Investment Capacity", f"&#8377;{inv_surplus:,.0f}", "Per month available", inv_cls)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ── Score & Ratios ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="fp-section-header">
        <span class="fp-section-title">Health Score Breakdown</span>
        <span class="fp-section-meta">Scored across 4 dimensions, 100 points total</span>
    </div>
    """, unsafe_allow_html=True)

    col_score, col_ratios = st.columns([1, 2])

    with col_score:
        st.markdown(f"""
        <div class="fp-score-card">
            <div class="fp-score-ring-label">Overall Score</div>
            <div class="fp-score-big">{score}<span class="fp-score-denom">/100</span></div>
            <span class="fp-score-grade {grade_class}">{grade}</span>
            <div style="margin-top:20px;width:100%;">
        """, unsafe_allow_html=True)

        rows = [
            ("EMI Burden",      details["emi"]["label"],      f"{details['emi']['pts']}/30"),
            ("Savings Rate",    details["savings"]["label"],   f"{details['savings']['pts']}/30"),
            ("Emergency Fund",  details["emergency"]["label"], f"{details['emergency']['pts']}/20"),
            ("Insurance",       details["insurance"]["label"], f"{details['insurance']['pts']}/20"),
        ]
        for label, status, pts in rows:
            st.markdown(f"""
            <div class="fp-breakdown-row">
                <div>
                    <div style="font-size:13px;color:#334155;font-weight:500;">{label}</div>
                    <div class="fp-breakdown-label" style="font-size:11px;">{status}</div>
                </div>
                <span class="fp-breakdown-score">{pts}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col_ratios:
        st.markdown("""
        <div class="fp-form-block" style="height:100%;">
            <div class="fp-form-block-title">Key Financial Ratios</div>
            <div style="height:1px;background:#F1F5F9;margin:10px 0 16px;"></div>
        """, unsafe_allow_html=True)

        def ratio_row(label, value, max_val, green_thresh, yellow_thresh):
            pct = min(value / max_val * 100, 100)
            if value <= green_thresh:
                fill_cls = "fill-green"; tag_cls = "tag-green"; tag = "Healthy"
            elif value <= yellow_thresh:
                fill_cls = "fill-yellow"; tag_cls = "tag-yellow"; tag = "Moderate"
            else:
                fill_cls = "fill-red"; tag_cls = "tag-red"; tag = "High"
            return (
                '<div class="fp-ratio-row">'
                f'<div class="fp-ratio-label">{label}</div>'
                '<div class="fp-ratio-track">'
                f'<div class="fp-ratio-fill {fill_cls}" style="width:{pct:.1f}%"></div>'
                '</div>'
                f'<div class="fp-ratio-value">{value:.1f}%</div>'
                f'<div class="fp-ratio-tag {tag_cls}">{tag}</div>'
                '</div>'
            )

        st.markdown(ratio_row("EMI / Income", emi_ratio, 100, 10, 25), unsafe_allow_html=True)
        st.markdown(ratio_row("Savings Rate", max(savings_rate, 0), 100, 20, 10), unsafe_allow_html=True)
        st.markdown(ratio_row("Expense Ratio", expense_ratio, 100, 60, 80), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ── AI Insight Cards ───────────────────────────────────────────────────
    st.markdown("""
    <div class="fp-section-header">
        <span class="fp-section-title">Key Recommendations</span>
        <span class="fp-section-meta">AI-generated, based on your profile</span>
    </div>
    """, unsafe_allow_html=True)

    sip_amount = max(int(surplus * 0.3 / 500) * 500, 1000)
    ef_target_val = details["emergency"]["target"]
    ef_monthly_val = max(int(surplus * 0.2 / 500) * 500, 500)

    insights = [
        ("icon-blue", "Investment Strategy",
         f"Start a SIP of &#8377;{sip_amount:,}/month in diversified equity mutual funds. Allocate 60% to large-cap, 30% to flexi-cap, and 10% to an international fund.",
         f"+&#8377;{int(sip_amount * 12 * 1.12):,} estimated annual corpus at 12% CAGR", False),
        ("icon-green", "Emergency Fund",
         f"Target emergency corpus of &#8377;{ef_target_val:,.0f} ({family_size * 6} months of fixed expenses). Contribute &#8377;{ef_monthly_val:,}/month to a liquid mutual fund or high-yield savings account.",
         f"Achievable in approximately {int(ef_target_val / max(ef_monthly_val, 1))} months", False),
        ("icon-orange", "Tax Optimization",
         f"Maximize 80C deduction of &#8377;1.5L/year via ELSS, EPF, and PPF. Add NPS Tier-I for extra &#8377;50,000 deduction under 80CCD(1B). Save up to &#8377;{int((150000 + 50000) * 0.30):,} in taxes annually.",
         f"Potential tax saving: &#8377;{int(200000 * 0.30):,}/year at 30% bracket", False),
    ]
    if emi_ratio > 25:
        insights.append((
            "icon-purple", "EMI Burden Alert",
            f"Your EMI-to-income ratio of {emi_ratio:.1f}% exceeds the recommended 25% threshold. Consider prepaying the highest-interest loan or refinancing to reduce the monthly outflow.",
            f"Reducing EMI by 10% frees &#8377;{int(total_emi * 0.1):,}/month", True
        ))

    for icon_cls, title, desc, impact, is_alert in insights:
        st.markdown(f"""
        <div class="fp-insight-card">
            <div class="fp-insight-icon {icon_cls}">{"!" if is_alert else "&#8594;"}</div>
            <div class="fp-insight-content">
                <div class="fp-insight-title">{title}</div>
                <div class="fp-insight-desc">{desc}</div>
                <div class="fp-insight-impact {'fp-insight-alert' if is_alert else ''}">{impact}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="fp-section-header">
        <span class="fp-section-title">Visual Analysis</span>
        <span class="fp-section-meta">Hover charts for exact figures</span>
    </div>
    """, unsafe_allow_html=True)
    render_charts(income, total_emi, medicine_avg, total_misc_avg)

    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ── Insurance ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="fp-section-header">
        <span class="fp-section-title">Insurance Coverage</span>
        <span class="fp-section-meta">Recommended based on income and family size</span>
    </div>
    """, unsafe_allow_html=True)
    render_insurance(income, family_size)

    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ── STRUCTURED AI PLAN ─────────────────────────────────────────────────
    st.markdown("""
    <div class="fp-section-header">
        <span class="fp-section-title">AI Financial Strategy</span>
        <span class="fp-section-meta">Structured plan &middot; Personalized by LLaMA 70B</span>
    </div>
    """, unsafe_allow_html=True)

    render_structured_plan(st.session_state.full_response, fd)

    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ── Goals tracker ─────────────────────────────────────────────────────
    if fd.get("goals"):
        st.markdown("""
        <div class="fp-section-header">
            <span class="fp-section-title">Goal Tracker</span>
            <span class="fp-section-meta">Monthly targets to reach each goal</span>
        </div>
        """, unsafe_allow_html=True)
        goal_cost = {
            "House": 5000000, "Car": 800000, "Child Education": 2000000,
            "Retirement": 10000000, "International Travel": 300000,
            "Emergency Fund": family_size * 90000,
        }
        gcols = st.columns(min(len(fd["goals"]), 3))
        for i, goal in enumerate(fd["goals"]):
            with gcols[i % 3]:
                cost = goal_cost.get(goal, 1000000)
                monthly_need = cost / 120
                st.markdown(f"""
                <div class="fp-kpi-card">
                    <div class="fp-kpi-label">{goal}</div>
                    <div class="fp-kpi-value">&#8377;{cost/100000:.0f}L</div>
                    <span class="fp-kpi-status status-good">&#8377;{monthly_need:,.0f}/month needed</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<hr class="fp-divider">', unsafe_allow_html=True)

    # ── Actions ───────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Run a new scenario", use_container_width=True):
            st.session_state.page = "form"; st.rerun()
    with col2:
        if st.button("Start fresh", use_container_width=True):
            for key in ["emis", "misc", "plan_generated", "full_response", "financial_data"]:
                if key in st.session_state: del st.session_state[key]
            st.session_state.page = "landing"; st.rerun()

    st.markdown("""
    <div class="fp-footer">
        FinPilot is an AI-assisted planning tool. Recommendations are indicative and do not constitute regulated financial advice.
        Consult a SEBI-registered investment advisor before making investment decisions.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
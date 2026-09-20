"""
CareerPlus — Streamlit UI.

Three panels:
  1. Sidebar: deterministic company search + filter
  2. Main: chat with the agent (company intelligence, applications)
  3. Expander: tool trace for each agent response (transparency)

Backend: FastAPI at http://localhost:8000/api/v1
"""
from __future__ import annotations

import json
from typing import Any

import requests
import streamlit as st

# ---------------------------------------------------------------------- #
# Config
# ---------------------------------------------------------------------- #
API_BASE = "http://localhost:8000/api/v1"
REQUEST_TIMEOUT = 300  # seconds (LLM may be slow)


# ---------------------------------------------------------------------- #
# Page setup
# ---------------------------------------------------------------------- #
st.set_page_config(
    page_title="CareerPlus",
    page_icon="💼",
    layout="wide",
)


# ---------------------------------------------------------------------- #
# Session state
# ---------------------------------------------------------------------- #
if "messages" not in st.session_state:
    st.session_state.messages: list[dict[str, str]] = []

if "companies" not in st.session_state:
    st.session_state.companies: list[dict[str, Any]] = []

if "prepared" not in st.session_state:
    st.session_state.prepared: dict[str, Any] | None = None


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def api_get(path: str) -> dict | None:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"API error (GET {path}): {exc}")
        return None


def api_post(path: str, payload: dict) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", "")
        except Exception:
            pass
        st.error(f"API error (POST {path}): {exc} — {detail}")
        return None
    except Exception as exc:
        st.error(f"API error (POST {path}): {exc}")
        return None


def display_companies(companies: list[dict]) -> None:
    if not companies:
        st.info("No companies to display.")
        return
    for c in companies:
        with st.container(border=True):
            cols = st.columns([3, 2, 2, 1])
            cols[0].markdown(f"**{c.get('name', '—')}**")
            cols[1].markdown(f"🌍 {c.get('country', '—')}")
            cols[2].markdown(f"👥 {c.get('size', '—')}")
            cols[3].markdown(f"📅 {c.get('founded_year', '—')}")

            st.caption(f"**Domain:** {c.get('domain', '—')}")
            if c.get("description"):
                st.write(c["description"][:400] + ("..." if len(c["description"]) > 400 else ""))

            meta_cols = st.columns(3)
            if c.get("website"):
                meta_cols[0].markdown(f"🔗 [{c['website']}]({c['website']})")
            if c.get("contacts"):
                meta_cols[1].markdown(f"📧 {', '.join(c['contacts'])}")

            if st.button(
                "Prepare application",
                key=f"prep_{c.get('company_id', c.get('name'))}",
            ):
                prepare_and_store(c["name"])


def prepare_and_store(company_name: str) -> None:
    with st.spinner(f"Preparing application for {company_name}..."):
        result = api_post(
            "/applications/prepare",
            {"company_name": company_name, "recipient": None},
        )
    if result and result.get("status") == "prepared":
        st.session_state.prepared = result
        st.success(f"Application prepared for {company_name}. See the panel below.")
    else:
        st.error("Preparation failed.")


# ---------------------------------------------------------------------- #
# Sidebar — company search
# ---------------------------------------------------------------------- #
with st.sidebar:
    st.header("🔍 Company search")

    with st.form("company_search_form"):
        country = st.text_input("Country (exact match)")
        domain_kw = st.text_input("Domain keyword")
        name_kw = st.text_input("Name contains")
        size_max = st.number_input("Max size (0 = ignore)", min_value=0, value=0)
        size_min = st.number_input("Min size (0 = ignore)", min_value=0, value=0)
        founded_after = st.number_input("Founded after (0 = ignore)", min_value=0, value=0)
        founded_before = st.number_input("Founded before (0 = ignore)", min_value=0, value=0)

        submitted = st.form_submit_button("Search")

    if submitted:
        payload: dict[str, Any] = {}
        if country:
            payload["country"] = country
        if domain_kw:
            payload["domain_contains"] = domain_kw
        if name_kw:
            payload["name_contains"] = name_kw
        if size_max > 0:
            payload["size_max"] = int(size_max)
        if size_min > 0:
            payload["size_min"] = int(size_min)
        if founded_after > 0:
            payload["founded_after"] = int(founded_after)
        if founded_before > 0:
            payload["founded_before"] = int(founded_before)

        result = api_post("/companies/search", payload)
        if result:
            st.session_state.companies = result.get("results", [])
            st.success(f"{result.get('matches_found', 0)} companies found.")

    if st.session_state.companies:
        st.divider()
        st.caption(f"**{len(st.session_state.companies)} companies loaded**")
        if st.button("Clear results"):
            st.session_state.companies = []
            st.rerun()

    st.divider()
    st.caption("Backend: FastAPI · LLM: Qwen3 8B · DB: Supabase")
    if st.button("🔄 Health check"):
        health = api_get("/health")
        if health:
            st.success(f"API OK — model: {health.get('model', '?')}")


# ---------------------------------------------------------------------- #
# Main area
# ---------------------------------------------------------------------- #
st.title("💼 CareerPlus")
st.caption("AI company intelligence & spontaneous application assistant")

left, right = st.columns([3, 2], gap="large")


# ---------------------------------------------------------------------- #
# Left: chat
# ---------------------------------------------------------------------- #
with left:
    st.subheader("💬 Ask the agent")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tool_calls"):
                with st.expander("Tool trace"):
                    for tc in msg["tool_calls"]:
                        st.markdown(f"**step {tc['step']} — `{tc['tool']}`**")
                        try:
                            st.json(tc["arguments"])
                        except Exception:
                            st.code(str(tc["arguments"]))

    user_input = st.chat_input("Ask about companies, projects, or applications...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = api_post(
                    "/chat",
                    {
                        "message": user_input,
                        "history": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages[:-1]
                        ],
                        "include_trace": True,
                    },
                )

            if result:
                answer = result.get("response", "")
                tool_calls = result.get("tool_calls", [])
                st.markdown(answer)
                if tool_calls:
                    with st.expander("Tool trace"):
                        for tc in tool_calls:
                            st.markdown(f"**step {tc['step']} — `{tc['tool']}`**")
                            try:
                                st.json(tc["arguments"])
                            except Exception:
                                st.code(str(tc["arguments"]))

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "tool_calls": tool_calls,
                    }
                )
            else:
                st.error("Agent did not respond.")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()


# ---------------------------------------------------------------------- #
# Right: companies + prepared application
# ---------------------------------------------------------------------- #
with right:
    st.subheader("🏢 Companies")

    if st.session_state.companies:
        display_companies(st.session_state.companies)
    else:
        st.info("No companies loaded. Use the sidebar to search.")

    # --- Prepared application panel ---
    if st.session_state.prepared:
        st.divider()
        st.subheader("✉️ Prepared application")
        p = st.session_state.prepared

        st.markdown(f"**Company:** {p.get('company', {}).get('name', '—')}")
        st.markdown(f"**Recipient:** {p.get('recipient', '—')}")
        st.markdown(f"**CV:** `{p.get('cv_id', '—')}` ({p.get('cv_label', '')})")
        if p.get("projects_names"):
            st.markdown(f"**Projects mentioned:** {', '.join(p['projects_names'])}")

        st.text_input("Subject", value=p.get("subject", ""), key="prep_subject")
        st.text_area(
            "Body",
            value=p.get("body", ""),
            height=220,
            key="prep_body",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Confirm & send", type="primary"):
                send_result = api_post(
                    "/applications/send",
                    {
                        "recipient": p["recipient"],
                        "subject": st.session_state.prep_subject,
                        "body": st.session_state.prep_body,
                        "company": p["company"]["name"],
                        "cv_id": p["cv_id"],
                        "company_id": p["company"].get("company_id"),
                        "projects_selected": p.get("projects_selected", []),
                    },
                )
                if send_result and send_result.get("status") == "success":
                    st.success(
                        f"✅ Sent to {send_result['recipient']} "
                        f"(message id: {send_result.get('message_id')})"
                    )
                    st.session_state.prepared = None
                else:
                    st.error("Send failed.")

        with col_b:
            if st.button("❌ Cancel"):
                st.session_state.prepared = None
                st.rerun()
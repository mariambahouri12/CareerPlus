import asyncio

import streamlit as st

from agent.agent import CareerPlusAgent
from agent.tool_registry import ToolRegistry
from llm.ollama_client import OllamaClient
from utils.cv_parser import CVParser


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareerPlus",
    page_icon="💼",
)


st.title("💼 CareerPlus")
st.caption("AI-powered job search assistant")


# ============================================================
# INITIALIZE COMPONENTS
# ============================================================

if "agent" not in st.session_state:

    llm = OllamaClient(
        model="qwen3:8b",
    )

    tools = ToolRegistry()

    st.session_state.agent = CareerPlusAgent(
        llm=llm,
        tool_registry=tools,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "cv_text" not in st.session_state:

    st.session_state.cv_text = None


if "cv_name" not in st.session_state:

    st.session_state.cv_name = None


# ============================================================
# DISPLAY CV STATUS
# ============================================================

if st.session_state.cv_text:

    st.success(
        f"📄 CV loaded: {st.session_state.cv_name}"
    )


# ============================================================
# DISPLAY CONVERSATION
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT + FILE UPLOAD
# ============================================================

chat_input = st.chat_input(
    "Ask CareerPlus something...",
    accept_file=True,
    file_type=["pdf"],
)


# ============================================================
# PROCESS USER INPUT
# ============================================================

if chat_input:

    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    user_query = chat_input.text.strip()

    uploaded_files = chat_input.files

    # --------------------------------------------------------
    # CV upload
    # --------------------------------------------------------

    if uploaded_files:

        uploaded_file = uploaded_files[0]

        try:

            parser = CVParser()

            pdf_bytes = uploaded_file.getvalue()

            cv_text = parser.parse_bytes(
                pdf_bytes
            )

            if not cv_text:

                st.error(
                    "Could not extract text from the CV."
                )

                st.stop()

            st.session_state.cv_text = cv_text

            st.session_state.cv_name = (
                uploaded_file.name
            )

            st.success(
                f"📄 CV uploaded successfully: "
                f"{uploaded_file.name}"
            )

        except Exception as exc:

            st.error(
                f"Error while parsing the CV: {exc}"
            )

            st.stop()

    # --------------------------------------------------------
    # If only CV was uploaded
    # --------------------------------------------------------

    if not user_query:

        st.info(
            "Your CV has been uploaded. "
            "You can now ask me questions about it "
            "or ask me to find matching jobs."
        )

        st.stop()

    # --------------------------------------------------------
    # Store user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(user_query)

    # --------------------------------------------------------
    # Agent
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            answer = asyncio.run(
                st.session_state.agent.run(
                    user_query=user_query,

                    history=(
                        st.session_state.messages[:-1]
                    ),

                    cv_text=(
                        st.session_state.cv_text
                    ),
                )
            )

        st.markdown(answer)

    # --------------------------------------------------------
    # Store assistant response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
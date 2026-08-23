import asyncio

import streamlit as st

from agent.agent import CareerPlusAgent
from agent.tool_registry import ToolRegistry
from llm.ollama_client import OllamaClient


st.set_page_config(
    page_title="CareerPlus",
    page_icon="💼",
)


st.title("💼 CareerPlus")
st.caption("AI-powered job search assistant")


# ---------------------------------------------------------
# Initialize components once
# ---------------------------------------------------------

if "agent" not in st.session_state:

    llm = OllamaClient(
        model="qwen3:8b",
    )

    tools = ToolRegistry()

    st.session_state.agent = CareerPlusAgent(
        llm=llm,
        tool_registry=tools,
    )


if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# Display conversation
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------------------------
# User input
# ---------------------------------------------------------

user_query = st.chat_input(
    "Ask CareerPlus something..."
)


if user_query:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = asyncio.run(
                st.session_state.agent.run(
                    user_query=user_query,
                    history=st.session_state.messages[:-1],
                )
            )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
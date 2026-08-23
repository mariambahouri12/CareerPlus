import json
from typing import Any, Dict, Optional

from agent.prompts import SYSTEM_PROMPT
from agent.state import AgentState


class CareerPlusAgent:
    """
    Agent that uses Qwen3 to decide which tools to call.
    """

    MAX_STEPS = 5

    def __init__(
        self,
        llm,
        tool_registry,
    ):
        self.llm = llm
        self.tool_registry = tool_registry

    # ==========================================================
    # SIMPLE RUN
    # ==========================================================

    async def run(
        self,
        user_query: str,
        history: Optional[list] = None,
        cv_text: Optional[str] = None,
    ) -> str:
        """
        Backward-compatible method.

        Returns only the final response.
        """

        result = await self.run_with_trace(
            user_query=user_query,
            history=history,
            cv_text=cv_text,
        )

        return result["response"]

    # ==========================================================
    # RUN WITH TRACE
    # ==========================================================

    async def run_with_trace(
        self,
        user_query: str,
        history: Optional[list] = None,
        cv_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the agent using an explicit AgentState.
        """

        state = AgentState(
            user_query=user_query,
            history=history or [],
            cv_text=cv_text,
        )

        # ------------------------------------------------------
        # Initial messages
        # ------------------------------------------------------

        state.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        if history:
            state.messages.extend(history)

        state.messages.append(
            {
                "role": "user",
                "content": user_query,
            }
        )

        # ------------------------------------------------------
        # Agent loop
        # ------------------------------------------------------

        for step in range(
            1,
            self.MAX_STEPS + 1,
        ):

            state.current_step = step

            response = await self.llm.chat(
                messages=state.messages,
                tools=self.tool_registry.schemas(),
            )

            message = response.message

            tool_calls = message.tool_calls or []

            print(
                f"\n=== AGENT STEP {step} ==="
            )

            # ==================================================
            # NO TOOL CALL
            # ==================================================

            if not tool_calls:

                final_response = (
                    message.content or ""
                )

                print("No tool call.")
                print(
                    "========================\n"
                )

                state.finish(
                    response=final_response
                )

                return {
                    "response": state.final_response,

                    "tool_calls": [
                        {
                            "step": call.step,
                            "tool": call.tool,
                            "arguments": call.arguments,
                        }
                        for call in state.tool_calls
                    ],

                    "steps": state.current_step,

                    "status": state.status,
                }

            # ==================================================
            # ADD ASSISTANT TOOL MESSAGE
            # ==================================================

            state.messages.append(message)

            # ==================================================
            # EXECUTE TOOLS
            # ==================================================

            for tool_call in tool_calls:

                tool_name = (
                    tool_call.function.name
                )

                arguments = (
                    tool_call.function.arguments
                )

                print(
                    f"Tool: {tool_name}"
                )

                print(
                    f"Arguments: {arguments}"
                )

                state.add_tool_call(
                    step=step,
                    tool=tool_name,
                    arguments=arguments,
                )

                # ------------------------------------------------
                # Execute
                # ------------------------------------------------

                try:

                    result = (
                        await self.tool_registry.execute(
                            tool_name=tool_name,
                            arguments=arguments,
                            cv_text=state.cv_text,
                        )
                    )

                except Exception as exc:

                    result = {
                        "status": "error",
                        "tool": tool_name,
                        "message": str(exc),
                    }

                # ------------------------------------------------
                # Record result
                # ------------------------------------------------

                state.add_tool_result(
                    step=step,
                    tool=tool_name,
                    result=result,
                )

                # ------------------------------------------------
                # Give result back to Qwen
                # ------------------------------------------------

                state.messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": json.dumps(
                            result,
                            ensure_ascii=False,
                        ),
                    }
                )

            print(
                "========================\n"
            )

        # ======================================================
        # MAX STEPS
        # ======================================================

        error_message = (
            "The agent reached its maximum "
            "number of execution steps."
        )

        state.fail(
            error=error_message
        )

        return {
            "response": error_message,

            "tool_calls": [
                {
                    "step": call.step,
                    "tool": call.tool,
                    "arguments": call.arguments,
                }
                for call in state.tool_calls
            ],

            "steps": state.current_step,

            "status": state.status,

            "error": state.error,
        }
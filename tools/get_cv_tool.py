class GetCVTool:
    """
    Tool used by the agent to access the user's uploaded CV.

    This tool does not perform job matching.
    It simply provides the CV content to the LLM so that
    the agent can answer questions about the CV.
    """

    name = "get_cv"

    description = (
            "Returns the raw content of the user's uploaded CV, so the agent can reason about it directly (skills, experience, education, etc.). Use this when the question is about the CV itself, not about matching it against job offers."
    )

    def run(self, cv_text: str | None = None):
        """
        Return the uploaded CV content.
        """

        if not cv_text:
            return {
                "status": "error",
                "message": (
                    "No CV has been uploaded. "
                    "Ask the user to upload their CV first."
                ),
            }

        return {
            "status": "success",
            "cv_available": True,
            "cv_text": cv_text,
        }
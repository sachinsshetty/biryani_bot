# Setup
- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt
- uvicorn main:app


Inferece raw
@router.post("/visual-query-raw/",
summary="Raw Visual Query with Prompt",
description="Process a prompt with a selected LLM model and return the response.",
tags=["Chat"],
responses={
    200: {"description": "Model response"},
    400: {"description": "Invalid prompt"},
    500: {"description": "Model error"}
})
async def visual_query_raw(
    prompt: str = Form(..., description="Prompt to process"),
    model: str = Form("gemma3", description="LLM model", enum=["gemma3", "moondream", "smolvla"])
    ):
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        client = get_openai_client(model)  # Replace with your LLM client getter
        # No streaming: get the full response at once
        response_obj = client.chat.completions.create(
            model=model,
            messages=prompt,
            temperature=0.3,
            max_tokens=500,
            stream=False  # Important: disable streaming
        )
        # Extract the response text (adjust depending on your client)
        response_text = response_obj.choices[0].message.content
        return JSONResponse(content=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
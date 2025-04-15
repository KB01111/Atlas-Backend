import google.generativeai as genai

from app.services.key_service import get_api_key


async def gemini_generate_text(user_id: str, prompt: str, model: str = "gemini-pro", options: dict = None):
    api_key = await get_api_key(user_id, "gemini")
    if not api_key:
        raise Exception("No Gemini API key found for user.")
    genai.configure(api_key=api_key)
    model_obj = genai.GenerativeModel(model)
    response = await model_obj.generate_content_async(prompt, **(options or {}))
    return response.text if hasattr(response, "text") else response

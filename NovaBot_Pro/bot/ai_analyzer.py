# bot/ai_analyzer.py
import google.generativeai as genai
from config.config import GEMINI_API_KEY

# تهيئة Gemini
genai.configure(api_key=GEMINI_API_KEY)


def summarize_video(url: str) -> str:
    """
    يستخدم Gemini لتحليل محتوى الفيديو من الرابط
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    أنت مُحلل محتوى ذكي. رجاءً حلّل هذا الفيديو من الرابط التالي:
    {url}

    وقدم إجابة واضحة ومنظمة بالعربية في 3 نقاط:
    1. ما هو الموضوع الرئيسي للفيديو؟
    2. ما أبرز 3 معلومات مهمة فيه؟
    3. لماذا قد يكون مفيدًا للمشاهد؟

    لا تكتب أكثر من 120 كلمة. استخدم لغة بسيطة وجذابة.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return "⚠️ تعذر تحليل الفيديو الآن. جرّب لاحقًا."
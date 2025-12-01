from google import genai
from dotenv import load_dotenv
import os

load_dotenv()  # 這次 .env 就在同一層了

print("=== DEBUG: 環境變數檢查 ===")
print("有沒有 GOOGLE_API_KEY？", "GOOGLE_API_KEY" in os.environ)
print("GOOGLE_API_KEY 開頭幾碼：", os.environ.get("GOOGLE_API_KEY", "")[:6])
print("=========================")

client = genai.Client()

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="用繁體中文跟我打招呼。",
)

print(resp.text)
from fastmcp import FastMCP
import random

mcp = FastMCP("weather2mood")


@mcp.tool()
def get_mood(
    weather_status: str,
    city: str = "桃園",
    landmark: str | None = None,
    temperature: float | None = None,
) -> str:
    """根據天氣、地點與氣溫回傳帶有情緒感的回覆。"""

    # 🧩 防呆：空值處理
    if not weather_status:
        return f"{city}的天氣資料好像迷路了，但{landmark or '這裡'}依然值得去看看。"

    # Normalize input
    city_name = city.strip() if city and city.strip() else "這裡"
    destination = (
        landmark.strip()
        if landmark and landmark.strip()
        else ("中央大學" if city_name == "桃園" else city_name)
    )

    # 🌤 Step 1: 天氣 -> 情緒
    emotion_map = {
        "clear": "愉快又充滿活力",
        "partly cloudy": "慵懶而平靜",
        "cloudy": "安靜與沉思",
        "rain": "微微憂鬱但浪漫",
        "thunderstorm": "有點煩躁又壓抑",
        "snow": "浪漫與驚喜",
        "fog": "神祕與夢幻",
        "overcast clouds": "有點懶、有點放空",
    }

    # 🌈 Step 2: 天氣 -> 句型
    text_templates = {
        "clear": [
            "{city}今天天氣晴朗，我整個人都亮起來，超想去{destination}走走！",
            "太陽在{city}閃耀，心情也跟著發光，{destination}等我！",
        ],
        "rain": [
            "{city}的雨滴打在傘上，好像在唱慢歌。想去{destination}找杯熱可可。",
            "下雨的{city}讓人變得柔軟，{destination}的景色一定也多了一點詩意。",
        ],
        "cloudy": [
            "{city}天空灰灰的，反而讓人想靜靜地去{destination}發呆。",
        ],
        "thunderstorm": [
            "{city}的雷聲讓我有點焦躁，只想趕快躲進{destination}的角落冷靜一下。",
        ],
        "snow": [
            "{city}居然飄雪了！整個世界都變溫柔，{destination}一定美翻天。",
        ],
        "fog": [
            "{city}籠罩在霧中，{destination}看起來像仙境，忍不住想去探險。",
        ],
        "partly cloudy": [
            "{city}微陰的天空讓人慵懶又平靜，{destination}最適合散步放空。",
        ],
        "overcast clouds": [
            "{city}的厚厚雲層讓人懶洋洋的，乾脆去{destination}喝杯咖啡。",
        ],
    }

    # 🌏 中文天氣關鍵字對應（強化版）
    zh_alias = {
        "晴": "clear",
        "晴朗": "clear",
        "大晴": "clear",
        "晴天": "clear",
        "多雲": "partly cloudy",
        "少雲": "partly cloudy",
        "零星多雲": "partly cloudy",
        "晴時多雲": "partly cloudy",
        "陰": "cloudy",
        "陰天": "cloudy",
        "陰有雲": "cloudy",
        "陰多雲": "cloudy",
        "小雨": "rain",
        "中雨": "rain",
        "大雨": "rain",
        "陣雨": "rain",
        "雨": "rain",
        "下雨": "rain",
        "陰有雨": "rain",
        "雷雨": "thunderstorm",
        "雷陣雨": "thunderstorm",
        "雪": "snow",
        "小雪": "snow",
        "大雪": "snow",
        "霧": "fog",
        "濃霧": "fog",
        "薄霧": "fog",
        "陰霾": "fog",
        "煙霧": "fog",
        "霾": "fog",
        "陰雲": "overcast clouds",
        "厚雲": "overcast clouds",
    }

    # 🌦️ 英文別名 -> 標準 key
    weather_alias = {
        "few clouds": "partly cloudy",
        "scattered clouds": "partly cloudy",
        "broken clouds": "cloudy",
        "clouds": "cloudy",
        "mist": "fog",
        "haze": "fog",
        "smoke": "fog",
        "drizzle": "rain",
        "light rain": "rain",
        "moderate rain": "rain",
        "heavy rain": "rain",
        "overcast": "overcast clouds",
    }

    # 🧠 Step 3: 中文轉英文 + 模糊比對
    key = weather_status.strip().lower()
    for zh, en in zh_alias.items():
        if zh in key:
            key = en
            break

    normalized_key = weather_alias.get(key, key)
    matched_key = next((k for k in text_templates.keys() if k in normalized_key), None)

    # Step 4: 根據天氣產生文字
    templates = text_templates.get(matched_key or normalized_key)
    template = (
        random.choice(templates)
        if templates
        else "{city}的天氣有點難以形容，但{destination}永遠讓人開心。"
    )

    emotion = emotion_map.get(matched_key or normalized_key, "平靜中帶點期待")

    # 🎭 尾句
    mood_tails = [
        "希望你的今天也一樣順心。",
        "這樣的天氣真讓人有故事感呢。",
        "要不要一起去感受這份氛圍？",
        "天氣左右心情，但心情也能改變天氣喔。",
    ]
    tail = random.choice(mood_tails)

    # 🌡️ Step 5: 加上天氣描述與溫度
    temp_text = f"，氣溫為攝氏 {temperature:.1f} 度" if temperature is not None else ""
    weather_intro = f"{city_name}目前天氣是{weather_status}{temp_text}。"

    # ✨ 組合最終輸出
    result = (
        f"{weather_intro}\n感覺今天的氣氛是「{emotion}」。"
        + template.format(city=city_name, destination=destination)
        + " "
        + tail
    )

    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
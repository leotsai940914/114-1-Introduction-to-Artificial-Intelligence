import random
from fastmcp import FastMCP

mcp = FastMCP(name="budget_server")

@mcp.tool
def calculate_budget(
    total_budget: float,
    days: int,
    country: str,
    num_people: int = 1,
) -> dict:
    """
    Hell-Snake Budget Calculator v5.1 — Final Polished Edition
    - 極低預算：地獄毒蛇模式（嘴砲但仍給建設性）
    - 低預算：柔性提醒，避免情緒化語氣
    - 中高預算：正常友善建議
    - 豪華預算：沉穩高級語氣
    - 重新梳理 floor / rescue / normalize → 無衝突版本
    - 所有國家物價、需求參數統一整理
    - 算式一致、行為確定、不會隨機暴走

    單位：台幣 / 人 / 日
    """

    warnings: list[str] = []
    flags = {
        "used_floor": False,
        "used_rescue": False,
        "used_normalize_down": False,
        "used_normalize_up": False,
    }

    # -------------------------------------------------
    # STEP 0 — sanity check
    # -------------------------------------------------
    if days <= 0 or num_people <= 0:
        warnings.append("天數或人數為 0，行程無法成立。請至少提供 1 天、1 人。")
        return {
            "daily_budget": 0,
            "budget_level": "invalid",
            "budget_level_label": "輸入錯誤",
            "price_level": "unknown",
            "price_level_label": "未知物價",
            "needs": {"survival_per_day": 0, "basic_per_day": 0},
            "minimum_need": {},
            "allocation": {k: 0 for k in ["food","transport","accommodation","attractions","others"]},
            "flags": flags,
            "warnings": warnings,
            "suggestion": "請提供有效的天數與人數。",
            "formatted_result": "輸入錯誤，無法計算。",
        }

    if total_budget <= 0:
        warnings.append("預算為零或負數，系統將以『極低』方式處理。")
        daily_budget = 0
    else:
        daily_budget = total_budget / days / num_people

    if 0 < daily_budget <= 200:
        warnings.append("每日預算極低，可能難以應付基本生活需求。")

    # -------------------------------------------------
    # STEP 1 — normalize city → country
    # -------------------------------------------------
    CITY_TO_COUNTRY = {
        "tokyo":"japan","osaka":"japan","kyoto":"japan","sapporo":"japan","nagoya":"japan",
        "fukuoka":"japan","kobe":"japan",
        "seoul":"korea","busan":"korea","daegu":"korea","incheon":"korea",
        "bangkok":"thailand","chiang mai":"thailand","phuket":"thailand","pattaya":"thailand",
        "london":"uk","manchester":"uk","edinburgh":"uk","liverpool":"uk",
        "new york":"usa","los angeles":"usa","san francisco":"usa","chicago":"usa",
        "las vegas":"usa","boston":"usa",
        "singapore":"singapore",
        "taipei":"taiwan","kaohsiung":"taiwan","taichung":"taiwan","tainan":"taiwan",
        "paris":"france","lyon":"france","nice":"france",
        "sydney":"australia","melbourne":"australia","brisbane":"australia",
    }

    c_raw = country.strip().lower()
    c = CITY_TO_COUNTRY.get(c_raw, c_raw)

    # -------------------------------------------------
    # STEP 2 — price level
    # -------------------------------------------------
    VHIGH = {"switzerland","norway","denmark","iceland","luxembourg","singapore"}
    HIGH = {"japan","uk","united kingdom","france","germany","australia","new zealand",
            "usa","united states","hong kong","ireland","sweden"}
    MID = {"taiwan","korea","south korea","spain","italy","portugal","greece",
           "canada","netherlands","belgium","israel","chile"}
    LOW = {"thailand","malaysia","turkey","mexico","brazil","argentina",
           "china","poland","czech republic","hungary","philippines"}
    VLOW = {"vietnam","indonesia","india","cambodia","laos","nepal",
            "pakistan","bangladesh","kenya","tanzania","egypt","morocco"}

    if c in VHIGH: price = "vhigh"
    elif c in HIGH: price = "high"
    elif c in MID: price = "mid"
    elif c in LOW: price = "low"
    elif c in VLOW: price = "vlow"
    else: price = "mid"

    price_label_map = {
        "vhigh":"超高物價國家","high":"高物價國家","mid":"中等物價國家",
        "low":"低物價國家","vlow":"超低物價國家"
    }

    # -------------------------------------------------
    # STEP 3 — minimum needs
    # -------------------------------------------------
    minimum = {
        "vhigh":{"food_soft":2100,"food_hard":1400,"transport_min":450,"accom_soft":5500,"accom_hard":4000},
        "high":{"food_soft":1800,"food_hard":1100,"transport_min":350,"accom_soft":4200,"accom_hard":2800},
        "mid":{"food_soft":900,"food_hard":600,"transport_min":250,"accom_soft":3300,"accom_hard":2100},
        "low":{"food_soft":650,"food_hard":400,"transport_min":180,"accom_soft":2200,"accom_hard":1300},
        "vlow":{"food_soft":450,"food_hard":250,"transport_min":120,"accom_soft":1300,"accom_hard":850},
    }

    m = minimum[price]

    survival_need = m["food_hard"] + m["transport_min"]
    basic_need = m["food_soft"] + m["transport_min"] + m["accom_soft"]

    # -------------------------------------------------
    # STEP 4 — determine budget level
    # -------------------------------------------------
    difficulty = {"vhigh":1.20,"high":1.10,"mid":1.0,"low":0.9,"vlow":0.8}
    D = difficulty[price]

    if daily_budget <= 0:
        level = "extreme_low"
    elif daily_budget < survival_need * D:
        level = "extreme_low"
    elif daily_budget < basic_need * D:
        level = "low"
    elif daily_budget < basic_need * 1.3 * D:
        level = "mid"
    elif daily_budget < basic_need * 2.0 * D:
        level = "high"
    else:
        level = "luxury"

    level_label_map = {
        "extreme_low":"異地求生等級",
        "low":"可活但緊縮",
        "mid":"中等旅行品質",
        "high":"舒適旅行",
        "luxury":"豪華旅遊",
    }

    # -------------------------------------------------
    # STEP 5 — ratio distribution
    # -------------------------------------------------
    base_ratios = {
        "luxury":{"food":0.35,"transport":0.10,"accommodation":0.45},
        "high":{"food":0.32,"transport":0.10,"accommodation":0.40},
        "mid":{"food":0.36,"transport":0.14,"accommodation":0.35},
        "low":{"food":0.42,"transport":0.20,"accommodation":0.25},
        "extreme_low":{"food":0.70,"transport":0.30,"accommodation":0},
    }

    ratios = base_ratios[level].copy()

    ratios["attractions"] = {
        "luxury":0.20,"high":0.15,"mid":0.10,"low":0.05,"extreme_low":0,
    }[level]

    used = sum(ratios.values())
    ratios["others"] = max(0, 1 - used)

    ratios["accommodation"] *= (1.05 - min(days * 0.02, 0.15))

    # -------------------------------------------------
    # STEP 6 — initial allocation
    # -------------------------------------------------
    allocation = {k: daily_budget * v for k, v in ratios.items()}

    transport_factor = {
        "japan":1.3,"korea":1.2,"south korea":1.2,"singapore":1.1,
        "thailand":0.9,"vietnam":0.7
    }
    if level != "extreme_low":
        tf = transport_factor.get(c, 1.0)
        if tf > 1:
            warnings.append(f"當地交通成本較高，已自動套用 transport ×{tf}。")
        allocation["transport"] *= tf

    # -------------------------------------------------
    # STEP 7 — floor + cap
    # -------------------------------------------------
    min_attraction = {"luxury":500,"high":250,"mid":120,"low":0,"extreme_low":0}
    use_hard = (level == "extreme_low")

    floor_table = {
        "food": m["food_hard"] if use_hard else m["food_soft"],
        "transport": m["transport_min"],
        "accommodation": (m["accom_hard"] if use_hard else m["accom_soft"]) if level!="extreme_low" else 0,
        "attractions": min_attraction[level],
        "others": 0,
    }

    cap_scale = 2.7
    cap_table = {
        "food": m["food_soft"] * cap_scale,
        "transport": m["transport_min"] * cap_scale,
        "accommodation": m["accom_soft"] * cap_scale,
        "attractions": 4000,
        "others": 3000,
    }

    for k in cap_table:
        cap_table[k] = min(cap_table[k], daily_budget * 0.95 if daily_budget > 0 else cap_table[k])

    for k in allocation:
        before = allocation[k]
        if before < floor_table[k] or before > cap_table[k]:
            flags["used_floor"] = True
        allocation[k] = min(max(allocation[k], floor_table[k]), cap_table[k])

    # -------------------------------------------------
    # STEP 8 — accommodation rescue
    # -------------------------------------------------
    if level != "extreme_low" and allocation["accommodation"] < m["accom_hard"]:
        flags["used_rescue"] = True
        warnings.append("住宿費偏低，已從其他項目挪動預算補強。")

        diff = m["accom_hard"] - allocation["accommodation"]
        adj_ratio = min(0.5, max(0.1, daily_budget / 20000 if daily_budget > 0 else 0.1))

        order = ["others","attractions","transport","food"]
        for key in order:
            if diff <= 0:
                break
            room = max(0, allocation[key] - floor_table[key])
            if room <= 0:
                continue
            take = min(diff, room * adj_ratio)
            allocation[key] -= take
            allocation["accommodation"] += take
            diff -= take

    # -------------------------------------------------
    # STEP 9 — normalize
    # -------------------------------------------------
    total_now = sum(allocation.values())

    if daily_budget > 0 and abs(total_now - daily_budget) > 1:
        if total_now > daily_budget:
            flags["used_normalize_down"] = True
            need_reduce = total_now - daily_budget
            reducible = ["attractions","others","transport"]
            max_reducible = sum(max(0, allocation[k]-floor_table[k]) for k in reducible)

            if max_reducible > 0:
                rate = min(1, need_reduce / max_reducible)
                for k in reducible:
                    room = max(0, allocation[k] - floor_table[k])
                    allocation[k] -= room * rate

            total_now = sum(allocation.values())
            if total_now > daily_budget:
                factor = daily_budget / total_now
                for k in allocation:
                    allocation[k] *= factor

        else:
            flags["used_normalize_up"] = True
            remaining = daily_budget - total_now
            if remaining > 0:
                if level in ("luxury","high"):
                    allocation["attractions"] += remaining * 0.6
                    allocation["others"] += remaining * 0.4
                else:
                    allocation["others"] += remaining
            # enforce cap after normalize_up
            for k in ["attractions", "others"]:
                allocation[k] = min(allocation[k], cap_table[k])

    # -------------------------------------------------
    # STEP 10 — suggestions
    # -------------------------------------------------
    if level == "extreme_low":
        suggestion = (
            "你的預算屬於地獄級，相當緊縮：\n"
            "• 吃：以溫飽為目標，口味期待請降低\n"
            "• 住：須考慮非常基本或共用空間\n"
            "• 行：以步行＋大眾交通為主\n"
            "• 景點：以免費景點為核心\n"
            "建議：務必保留安全預備金，行程請務實規劃。"
        )
    elif level == "low":
        suggestion = (
            "此預算較拮据但可維持基本品質：\n"
            "• 吃：一般餐點為主，偶爾可小升級\n"
            "• 住：經濟型旅宿或青年旅館\n"
            "• 行：以大眾運輸搭配步行\n"
            "• 景點：免費＋低價景點優先\n"
            "建議：彈性安排、避免不必要的額外支出。"
        )
    elif level == "mid":
        suggestion = (
            "你的預算屬於正常旅遊等級：\n"
            "• 吃：多數餐廳皆能負擔\n"
            "• 住：舒適乾淨的住宿品質\n"
            "• 行：大眾運輸搭配偶爾計程車\n"
            "• 景點：可安排付費景點\n"
            "整體：能獲得穩定且愉快的旅遊體驗。"
        )
    elif level == "high":
        suggestion = (
            "你的預算偏向舒適旅行：\n"
            "• 吃：可享受較高品質餐點\n"
            "• 住：舒適便利的飯店選擇\n"
            "• 行：交通以節省時間為主\n"
            "• 景點：多種類型體驗皆可納入\n"
            "整體：能享受到完整且自在的旅程。"
        )
    else:
        suggestion = (
            "你的預算屬於豪華等級：\n"
            "• 吃：高級料理、特色餐廳皆可嘗試\n"
            "• 住：高星級或精品住宿\n"
            "• 行：包車或專車接送\n"
            "• 景點：私人導覽、高端體驗皆可安排\n"
            "整體：建議好好規劃，享受高品質旅程。"
        )

    # -------------------------------------------------
    # STEP 11 — format output
    # -------------------------------------------------
    formatted_allocation = {k: round(float(v), 2) for k, v in allocation.items()}

    level_label = level_label_map[level]
    price_label = price_label_map[price]

    disclaimer = "※ 本工具為預算建議模型，提供參考分配，不代表實際物價與必需支出。請依個人習慣、目的、節奏調整。"

    formatted = [
        f"目的地：{country}",
        f"總預算：{total_budget} 元 / {days} 天 / {num_people} 人",
        f"每人每日預算：{round(daily_budget,2)} 元",
        f"預算等級：{level}（{level_label}）",
        f"物價等級：{price}（{price_label}）",
        "",
        f"⚙ 生存需求：約 {survival_need} 元／日（最低）",
        f"⚙ 舒適需求：約 {basic_need} 元／日",
        "",
        "【每日預算分配】",
        f"- 餐飲：{formatted_allocation['food']} 元",
        f"- 交通：{formatted_allocation['transport']} 元",
        f"- 住宿：{formatted_allocation['accommodation']} 元",
        f"- 景點：{formatted_allocation['attractions']} 元",
        f"- 其他：{formatted_allocation['others']} 元",
    ]

    if warnings:
        formatted.append("")
        formatted.append("【提醒】")
        for w in warnings:
            formatted.append(f"- {w}")

    formatted.append("")
    formatted.append("【整體建議】")
    formatted.append(suggestion)
    formatted.append("")
    formatted.append(disclaimer)

    formatted_text = "\n".join(formatted)

    # -------------------------------------------------
    # STEP 12 — return
    # -------------------------------------------------
    return {
        "daily_budget": daily_budget,
        "budget_level": level,
        "budget_level_label": level_label,
        "price_level": price,
        "price_level_label": price_label,
        "needs": {"survival_per_day": survival_need, "basic_per_day": basic_need},
        "minimum_need": {
            "food_soft": m["food_soft"],
            "food_hard": m["food_hard"],
            "transport_min": m["transport_min"],
            "accommodation_soft": m["accom_soft"],
            "accommodation_hard": m["accom_hard"],
        },
        "allocation": formatted_allocation,
        "flags": flags,
        "warnings": warnings,
        "suggestion": suggestion,
        "formatted_result": formatted_text,
    }


if __name__ == "__main__":
    mcp.run(transport="sse", port=5002)
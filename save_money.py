#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦营养省钱分析仪 · 省钱闭环演示（领券 + 计价）

真实调用麦当劳 MCP，串起「选门店 → 选套餐 → 真实计价 → 实时可领券 → (可选)一键领 → 算到手价」。

用法:
    export MCD_MCP_TOKEN="你的Token"
    python save_money.py                       # 上海人民广场，默认 3 个餐品
    python save_money.py 北京 中关村            # 指定城市 + 关键词
    python save_money.py --bind                 # 额外执行一键领券（会真实绑定到账号）
"""
import os
import sys
import re
import mcp_client as m


def main():
    token = os.environ.get("MCD_MCP_TOKEN")
    if not token:
        print("请先设置环境变量 MCD_MCP_TOKEN（在 https://open.mcd.cn/mcp 领取）")
        sys.exit(1)

    city = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "上海"
    keyword = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "人民广场"
    bind = "--bind" in sys.argv

    print(f"🔎 搜索门店：{city} · {keyword}")
    stores = m.fetch_nearby_stores(city, keyword)
    if not stores:
        print("未找到门店，换个城市 / 关键词试试")
        sys.exit(1)
    st = stores[0]
    sc, bc = st.get("storeCode"), st.get("beCode", "")
    print(f"🏪 选中门店：{st.get('storeName')}（storeCode={sc}, beCode={bc}）\n")

    print("🍽️ 取菜单并真实计价：")
    meals = m.fetch_meals(sc, bc)
    codes = []
    for cat in meals.get("categories", []):
        for it in cat.get("meals", []):
            if it.get("code"):
                codes.append(it["code"])
        if len(codes) >= 3:
            break

    total_fen = 0
    rows = []
    for code in codes[:3]:
        d = m.fetch_calculate_price([{"productCode": code, "quantity": 1}], sc, bc)
        if not d:
            continue
        name = (d.get("productList") or [{}])[0].get("productName", code)
        price = d.get("price", 0)
        total_fen += price
        rows.append((name, price / 100))
        print(f"   · {name}：¥{price / 100:.2f}")

    print(f"\n💰 套餐原价合计：¥{total_fen / 100:.2f}")

    print("\n🎟️ 实时可领券（麦麦省）：")
    cp_list = m.fetch_coupons(token)
    faces = []
    for c in cp_list:
        title = c.get("title", "")
        mt = re.search(r"([\d.]+)\s*元", title)
        val = float(mt.group(1)) if mt else 0.0
        faces.append({"title": title, "value": val, "free": ("免费" in title) or val == 0})
    for c in faces:
        tag = "免费" if c["free"] else f"券面额 ¥{c['value']:.2f}"
        print(f"   · {c['title']}（{tag}）")

    best = max(faces, key=lambda c: c["value"]) if faces else None
    if best and best["value"]:
        save = best["value"]
        after = max(0.0, total_fen / 100 - save)
        print(f"\n✅ 组合推荐：用「{best['title']}」抵扣")
        print(f"   预估到手价 ≈ ¥{after:.2f}（节省 ¥{save:.2f}）")
        print("   ⚠️ 券面额抵扣为估算：calculate-price 未直接应用券，到店以实际可用券为准")

    if bind:
        print("\n🤖 执行一键领券：")
        print(m.fetch_auto_bind_coupons(token)[:600])


if __name__ == "__main__":
    main()

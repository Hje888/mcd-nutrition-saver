#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦营养省钱分析仪 · 本地可视化报告生成器

纯标准库实现，无外部依赖（不依赖 matplotlib / 网络）。
输入 JSON（stdin 或 --input 文件）：
{
  "title": "我的麦当劳午餐",
  "items": [
    {"name":"巨无霸","energy_kcal":513,"protein":27,"fat":26,"carbs":42,"sodium":961,"calcium":171}
  ],
  "price": {"original": 45.5, "discounted": 32.0, "coupon": "麦麦省-满30减13"},   # 可选
  "coupons": ["11.9元麦辣鸡腿堡", "免费脆薯饼"]                                  # 可选，真实可领券
}
输出：单文件离线 HTML（内联 SVG，深色主题，中文），写入 --output 或打印到 stdout。

字段兼容：items 可用 energy_kcal 或 calories；其余为 protein/fat/carbs/sodium/calcium。
"""
import json, sys, math, argparse, datetime, html

REF = {"calories": 2500, "protein": 150, "fat": 150, "carbs": 300, "sodium": 3000, "calcium": 1500}
AXES = [("calories", "能量"), ("protein", "蛋白"), ("fat", "脂肪"),
        ("carbs", "碳水"), ("sodium", "钠"), ("calcium", "钙")]


def _cal(it):
    return it.get("calories", it.get("energy_kcal", 0))


def norm(v, k):
    return max(0.0, min(100.0, v / REF[k] * 100))


def build(data):
    raw_items = data.get("items", [])
    items = []
    for it in raw_items:
        d = dict(it)
        d["calories"] = _cal(it)
        items.append(d)
    title = data.get("title", "麦当劳营养省钱报告")
    price = data.get("price", {})
    coupons = data.get("coupons", [])

    tot = {k: sum(it.get(k, 0) for it in items) for k, _ in AXES}
    n = len(AXES)
    cx = cy = 180
    R = 130
    grid = ""
    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = []
        for i, (k, lab) in enumerate(AXES):
            ang = -90 + 360 * i / n
            rad = math.radians(ang)
            pts.append(f"{cx + R * ring * math.cos(rad):.1f},{cy + R * ring * math.sin(rad):.1f}")
        grid += f'<polygon points="{" ".join(pts)}" fill="none" stroke="#3a3a4a" stroke-width="1"/>'
    dpts = []
    for i, (k, lab) in enumerate(AXES):
        ang = -90 + 360 * i / n
        rad = math.radians(ang)
        rr = R * norm(tot[k], k) / 100
        dpts.append(f"{cx + rr * math.cos(rad):.1f},{cy + rr * math.sin(rad):.1f}")
    data_poly = f'<polygon points="{" ".join(dpts)}" fill="rgba(219,39,119,0.35)" stroke="#db2777" stroke-width="2"/>'
    labels = ""
    for i, (k, lab) in enumerate(AXES):
        ang = -90 + 360 * i / n
        rad = math.radians(ang)
        lx = cx + (R + 22) * math.cos(rad)
        ly = cy + (R + 22) * math.sin(rad)
        labels += f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#cbd5e1" font-size="12" text-anchor="middle" dominant-baseline="middle">{lab}</text>'
        labels += f'<text x="{lx:.1f}" y="{ly+14:.1f}" fill="#f472b6" font-size="11" text-anchor="middle" dominant-baseline="middle">{tot[k]}</text>'
    radar = f'''<svg viewBox="0 0 360 360" width="320" height="320">
      {grid}{data_poly}{labels}
      <text x="180" y="350" fill="#94a3b8" font-size="11" text-anchor="middle">营养雷达（占每日参考摄入%）</text>
    </svg>'''
    rows = ""
    for it in items:
        rows += (f"<tr><td>{html.escape(str(it.get('name', '')))}</td><td>{it.get('calories', 0)}</td>"
                 f"<td>{it.get('protein', 0)}</td><td>{it.get('fat', 0)}</td><td>{it.get('carbs', 0)}</td>"
                 f"<td>{it.get('sodium', 0)}</td><td>{it.get('calcium', 0)}</td></tr>")
    table = f'''<table class="t"><thead><tr><th>餐品</th><th>能量</th><th>蛋白</th><th>脂肪</th><th>碳水</th><th>钠</th><th>钙</th></tr></thead><tbody>{rows}</tbody></table>'''

    # 省钱模块：真实优惠券卡片
    ccards = ""
    if coupons:
        spans = "".join(f'<span class="coupon">🎟️ {html.escape(str(c))}</span>' for c in coupons)
        ccards = (f'<div class="ccards">{spans}</div>'
                  f'<p class="tip">↑ 以上为麦当劳 MCP「麦麦省」实时可领优惠券，可在麦当劳 App 直接领取使用。</p>')
    # 省钱模块：价格对比（如有真实用券价）
    bars = ""
    orig = price.get("original")
    disc = price.get("discounted")
    if orig is not None and disc is not None:
        save = orig - disc
        pct = (save / orig * 100) if orig else 0
        dw = (disc / orig * 100) if orig else 0
        coupon = f" · 券：{html.escape(price['coupon'])}" if price.get("coupon") else ""
        bars = (f'<div class="bar"><span class="lab">原价</span><div class="track"><div class="fill o" style="width:100%"></div></div><b>¥{orig:.2f}</b></div>'
                f'<div class="bar"><span class="lab">用券</span><div class="track"><div class="fill p" style="width:{dw:.0f}%"></div></div><b>¥{disc:.2f}</b></div>'
                f'<div class="save">💰 本单节省 ¥{save:.2f}（{pct:.0f}%）{coupon}</div>')
    save_block = (bars + ccards) if (bars or ccards) else \
        '<p class="tip">💡 开启麦当劳 MCP 后，Skill 会调 available-coupons / calculate-price 给出用券价与可领券。</p>'

    html_out = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
body{{background:#0f1020;color:#e2e8f0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:680px;margin:0 auto;padding:20px}}
h1{{color:#f472b6;font-size:20px}} .card{{background:#1a1b2e;border:1px solid #2a2b40;border-radius:14px;padding:16px;margin:14px 0}}
.t{{width:100%;border-collapse:collapse;font-size:13px}} .t th,.t td{{border:1px solid #2a2b40;padding:6px 8px;text-align:center}}
.t th{{color:#f472b6}} .bar{{display:flex;align-items:center;gap:10px;margin:8px 0}} .lab{{width:40px;color:#94a3b8}}
.track{{flex:1;background:#25263a;border-radius:8px;height:18px;overflow:hidden}} .fill{{height:100%}} .o{{background:#475569}} .p{{background:#db2777}}
.save{{color:#34d399;font-weight:700;margin-top:8px}} .tip{{color:#94a3b8;font-size:12px}}
.ccards{{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0}} .coupon{{background:#2a1b2e;border:1px solid #db2777;color:#f9a8d4;border-radius:999px;padding:6px 12px;font-size:13px}}
</style></head><body>
<h1>🍔 {html.escape(title)}</h1>
<div class="card" style="text-align:center">{radar}</div>
<div class="card">{table}</div>
<div class="card">{save_block}</div>
<p class="tip">⚠️ 餐品/价格/供应以麦当劳官方实时结果为准；营养数据仅供参考，不构成医疗或营养专业建议。本报告由「麦麦营养省钱分析仪」(WorkBuddy × 麦当劳 MCP) 生成。</p>
<p class="tip">生成时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</body></html>'''
    return html_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i")
    ap.add_argument("--output", "-o")
    args = ap.parse_args()
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    out = build(data)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print("报告已生成：" + args.output)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()

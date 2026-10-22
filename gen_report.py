#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用本地缓存的真实数据（data/）生成示例报告，无需 Token。

数据来源：
  - data/nutrition_real.json   由 mcp_client.fetch_nutrition() 抓取的 160 项真实营养
  - data/coupons_raw.txt       由 mcp_client.fetch_coupons() 抓取的真实可领优惠券

运行: python gen_report.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import make_report as m  # noqa: E402

rows = json.load(open(os.path.join(ROOT, "data", "nutrition_real.json"), encoding="utf-8"))
by = {r["name"]: r for r in rows}
combo = ["巨无霸", "中薯条", "可乐中杯"]
items = [by[n] for n in combo if n in by]

ct = open(os.path.join(ROOT, "data", "coupons_raw.txt"), encoding="utf-8").read()
coupons = []
for blk in ct.split("- 优惠券标题："):
    if "状态" in blk:
        coupons.append(blk.split("\n")[0].strip())

html = m.build({
    "title": "示例 · 巨无霸套餐（真实营养数据）",
    "items": items,
    "coupons": coupons,
})
out = os.path.join(ROOT, "example_report.html")
open(out, "w", encoding="utf-8").write(html)
print(f"OK 已生成 {out} | 餐品 {len(items)} 项 | 优惠券 {len(coupons)} 张")
print("套餐:", [it["name"] for it in items])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦营养省钱分析仪 · 麦当劳 MCP 真实客户端 (Streamable HTTP)

仅依赖 Python 标准库（urllib），无需 pip 安装任何第三方包。
直接对接 open.mcd.cn 提供的官方 MCP 能力，是本项目 Skill 的取数后端。

环境变量:
    MCD_MCP_TOKEN   在 https://open.mcd.cn/mcp 手机号登录 → 控制台 → 激活 领取

用法:
    export MCD_MCP_TOKEN="你的Token"
    python mcp_client.py                 # 联调：打印营养/优惠券/菜单概要
    python mcp_client.py --report        # 拉真实数据并直接生成 example_report.html
    python mcp_client.py --nutrition     # 仅打印营养清单
    python mcp_client.py --coupons       # 仅打印可领优惠券
    python mcp_client.py --meals         # 仅打印菜单分类
"""
import urllib.request
import urllib.error
import json
import os
import sys
import datetime

MCD_MCP_URL = "https://mcp.mcd.cn"
PROTOCOL = "2024-11-05"


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }


def _parse_sse(body):
    events = []
    for line in body.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            payload = line[5:].strip()
            try:
                events.append(json.loads(payload))
            except json.JSONDecodeError:
                pass
    return events


def _rpc(token, method, params=None, session=None):
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(MCD_MCP_URL, data=data, method="POST")
    for k, v in _headers(token).items():
        req.add_header(k, v)
    if session:
        req.add_header("Mcp-Session-Id", session)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            sid = resp.headers.get("Mcp-Session-Id")
            ct = resp.headers.get("Content-Type", "")
            if "text/event-stream" in ct:
                return _parse_sse(raw), sid
            return [json.loads(raw)], sid
    except urllib.error.HTTPError as e:
        return [{"_http": e.code, "_body": e.read().decode("utf-8", "ignore")}], None
    except Exception as e:  # noqa: BLE001
        return [{"_err": str(e)}], None


def _session(token):
    res, sid = _rpc(token, "initialize", {
        "protocolVersion": PROTOCOL,
        "capabilities": {},
        "clientInfo": {"name": "mcd-nutrition-saver", "version": "1.0.0"},
    })
    _rpc(token, "notifications/initialized", None, session=sid)
    return sid


def _call(token, name, params, sid):
    res, _ = _rpc(token, "tools/call", {"name": name, "arguments": params}, session=sid)
    for ev in res:
        if "result" in ev:
            return ev["result"]
    return {"raw": res}


def _text(result):
    try:
        return result["content"][0]["text"]
    except Exception:  # noqa: BLE001
        return ""


def _extract_json(text):
    """从 MCP 返回的 markdown 文本里抠出最外层 {..} JSON（data 字段内含 {} 也能正确匹配）。"""
    start = text.find('{"success"')
    if start < 0:
        start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


# ---------- 业务取数 ----------

def fetch_nutrition(token=None):
    token = token or os.environ.get("MCD_MCP_TOKEN")
    if not token:
        raise RuntimeError("缺少 MCD_MCP_TOKEN")
    sid = _session(token)
    res = _call(token, "list-nutrition-foods", {}, sid)
    obj = _extract_json(_text(res))
    if not obj:
        return []
    data_str = obj.get("data", "")
    idx = data_str.find("}:")
    body = data_str[idx + 2:] if idx >= 0 else data_str
    rows = []
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            continue
        p = [x.strip() for x in line.split(",")]
        if len(p) >= 9:
            try:
                rows.append({
                    "name": p[0],
                    "energy_kcal": int(p[3]),
                    "protein": int(p[4]),
                    "fat": int(p[5]),
                    "carbs": int(p[6]),
                    "sodium": int(p[7]),
                    "calcium": int(p[8]),
                })
            except ValueError:
                pass
    return rows


def fetch_coupons(token=None):
    token = token or os.environ.get("MCD_MCP_TOKEN")
    sid = _session(token)
    res = _call(token, "available-coupons", {}, sid)
    text = _text(res)
    coupons = []
    for blk in text.split("- 优惠券标题："):
        if "状态" in blk:
            title = blk.split("\n")[0].strip().rstrip("\\").strip()
            coupons.append({"title": title})
    return coupons


def fetch_meals(token=None, order_type=1):
    token = token or os.environ.get("MCD_MCP_TOKEN")
    sid = _session(token)
    res = _call(token, "query-meals", {"orderType": order_type}, sid)
    obj = _extract_json(_text(res))
    return obj.get("data", {}) if obj else {}


def main():
    token = os.environ.get("MCD_MCP_TOKEN")
    mode = sys.argv[1] if len(sys.argv) > 1 else "--all"
    if not token:
        print("请先设置环境变量 MCD_MCP_TOKEN（在 https://open.mcd.cn/mcp 领取）")
        sys.exit(1)

    if mode in ("--nutrition", "--all", "--report"):
        rows = fetch_nutrition(token)
        print(f"[营养] 共 {len(rows)} 项真实餐品，示例: {rows[0] if rows else '空'}")

    if mode in ("--coupons", "--all", "--report"):
        cps = fetch_coupons(token)
        print(f"[优惠券] 共 {len(cps)} 张实时可领: {[c['title'] for c in cps]}")

    if mode in ("--meals", "--all"):
        meals = fetch_meals(token)
        print(f"[菜单] 分类数: {len(meals.get('categories', []))}")

    if mode == "--report":
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
        import make_report as m
        rows = fetch_nutrition(token)
        by = {r["name"]: r for r in rows}
        combo = ["巨无霸", "中薯条", "可乐中杯"]
        items = [by[n] for n in combo if n in by]
        cps = fetch_coupons(token)
        html = m.build({
            "title": "巨无霸套餐 · 真实营养 & 省钱分析",
            "items": items,
            "coupons": [c["title"] for c in cps],
        })
        out = os.path.join(os.path.dirname(__file__), "example_report.html")
        open(out, "w", encoding="utf-8").write(html)
        print(f"[报告] 已生成: {out}（{len(items)} 餐品 / {len(cps)} 优惠券）")
        print(f"[时间] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    main()

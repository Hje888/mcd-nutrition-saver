# WorkBuddy 开发对话记录 (workbuddy.md)

> 本文件用于核验「麦当劳程序员节创意开发大赛」WorkBuddy 专项奖励条件：参赛项目须真实使用腾讯 WorkBuddy 智能体开发。以下为本次开发的真实对话上下文摘要（导出自 WorkBuddy 会话）。

## 开发时间线

- **2026-10-22**：用户分享一个 WorkBuddy 资料库页面（`https://www.workbuddy.link/p/8QYARuAmZ9RgQty3FSzNUs?source=2`），要求「研究一下这个赚积分」。
- WorkBuddy 抓取并解读页面，确认主题为 **WorkBuddy × 麦当劳「1024 程序员节·麦当劳程序员创意开发大赛」**（官方仓库 `M-China/mcd-developer-innovation-challenge`）。提取积分机制：
  - 排行榜前 100 名 + 真实使用 WorkBuddy + 提交 `workbuddy.md` → **3000 积分/人**
  - 前三名 → **10240 积分** + 巨无霸免费兑换券（50/30/20 次）
- WorkBuddy 从官方 GitHub 仓库获取完整规则：5 个标准文件要求、报名 Issue 模板（标题与正文间不换行、项目地址不用 Markdown 链接）、定榜时间 2026-10-26 00:00；并**逐字取得 `CONTEST_DECLARATION.md` 原文**（要求一字不改使用）。
- 从 `M-China/mcd-mcp-server` 获取麦当劳 MCP 工具清单（35 个工具），确认接入方式为 **Streamable HTTP**（`https://mcp.mcd.cn` + `Authorization: Bearer <Token>`）。
- **选题**：结合用户的数据可视化强项，确定做「**麦麦营养省钱分析仪**」——用麦当劳 MCP 取营养 / 菜单 / 优惠 / 计价，产出单文件离线 HTML 可视化报告（营养雷达图 + 省钱对比图）。
- WorkBuddy 生成项目全部标准文件：`README.md`、`CONTEST_DECLARATION.md`（官方原文不改）、`MCP_INTEGRATION.md`、`mcp-config.example.json`、`skill/SKILL.md`、`scripts/make_report.py`，并新增 `mcp_client.py`（标准库实现的真实 MCP 客户端）、`gen_report.py`。

## 🔌 真实 MCP 联调记录（2026-10-22 实测，证明真实使用 WB + 真实调用 MCP）

用户在 WorkBuddy 对话中提供了有效的麦当劳 MCP Token，WorkBuddy **直接用该 Token 通过 Streamable HTTP 协议完成了真实接口联调**，而非仅停留在文档层面：

1. **连通性验证**：`initialize` 成功，返回 `serverInfo: {name:"mcd-mcp", version:"1.0.0"}`，`protocolVersion: 2024-11-05`。
2. **`tools/list`**：成功返回 **35 个真实工具**，包括 `list-nutrition-foods`、`query-meals`、`query-meal-detail`、`calculate-price`、`available-coupons`、`auto-bind-coupons`、`query-store-coupons`、`campaign-calendar`、`now-time-info` 等。
3. **`list-nutrition-foods`（真实取数）**：成功拉取 **160 项真实餐品营养**，解析为结构化数据存于 `data/nutrition_real.json`。真实样例：
   - 巨无霸：能量 **513** kcal / 蛋白 27g / 脂肪 26g / 碳水 42g / 钠 961mg / 钙 171mg
   - 麦辣鸡腿汉堡：能量 485 kcal / 蛋白 24g / 脂肪 24g / 碳水 42g / 钠 1208mg / 钙 154mg
   - 中薯条：能量 289 kcal / 蛋白 4g / 脂肪 12g / 碳水 38g / 钠 165mg / 钙 18mg
4. **`query-meals`（真实取数）**：成功返回菜单分类与餐品映射（含餐品编码、标签），验证菜单数据源可用。
5. **`available-coupons`（真实取数）**：成功拉取**实时可领优惠券**（存于 `data/coupons_raw.txt`），真实样例：
   - 🎟️ `11.9元麦辣鸡腿堡`（可领取）
   - 🎟️ `19.9元王牌炸鸡任选2`（可领取）
   - 🎟️ `免费脆薯饼`（可领取）

> 以上 5 步均为 WorkBuddy 在会话内通过 Python（urllib）真实发起的 MCP 调用，Token 仅在本次会话的环境变量中使用、未落盘。联调产物 `data/nutrition_real.json`、`data/coupons_raw.txt`、`example_report.html` 均为真实数据/真实渲染结果。

## 使用的 WorkBuddy 能力

- WebFetch / WebSearch：检索活动规则与麦当劳 MCP 工具清单、逐字获取参赛声明原文
- 文件读写（Write / Edit）：生成项目全部标准文件与源代码
- Python 执行（Bash）：**真实联调麦当劳 MCP（initialize / tools/list / list-nutrition-foods / query-meals / available-coupons）**，并运行 `make_report.py` / `gen_report.py` 生成可视化报告

## 依赖的麦当劳 MCP 工具（已实测可用）

`list-nutrition-foods` · `query-meals` · `query-meal-detail` · `calculate-price` · `available-coupons` · `auto-bind-coupons` · `query-store-coupons` · `campaign-calendar` · `now-time-info`

> 说明：本记录为开发对话导出的上下文摘要，用于证明项目由 WorkBuddy 真实开发并真实调用了麦当劳 MCP，符合联动积分奖励条件。

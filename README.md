# 麦麦营养省钱分析仪 (McDonald's Nutrition & Saver Analyst)

基于**麦当劳中国官方 MCP** 能力开发的 WorkBuddy Skill，帮你在点麦当劳前「吃得明白、花得明白」。

- 🥗 **营养透视**：根据所选餐品，汇总能量、蛋白质、脂肪、碳水、钠、钙，生成可视化营养雷达图；
- 💰 **省钱对比**：结合麦当劳 MCP「麦麦省」实时可领优惠券（`available-coupons`）与计价能力（`calculate-price`），告诉你这单能省多少；
- 📊 **一键报告**：输出**单文件离线 HTML** 报告（深色主题、内联 SVG 图表），手机可直接看、可分享。

> 全程由 WorkBuddy 真实驱动（开发对话 + **真实 MCP 联调记录**见 `workbuddy.md`），体现「用 WB 把 MCP 原子能力拼成可用产品」的赛事主旨。本项目已用真实 Token 实测拉取 160 项真实营养数据与实时优惠券。

## 安装方法

1. 申请麦当劳 MCP Token：访问 https://open.mcd.cn/mcp ，手机号登录 → 控制台 → 激活，一键复制 Token。
2. 在 WorkBuddy 左侧【连接器】→【自定义连接器】→【配置 MCP】，粘贴以下 JSON（把 `${MCD_MCP_TOKEN}` 换成你的真实 Token，或在本机环境变量设置 `MCD_MCP_TOKEN`）：
   ```json
   {
     "mcpServers": {
       "mcd-mcp": {
         "type": "streamablehttp",
         "url": "https://mcp.mcd.cn",
         "headers": { "Authorization": "Bearer ${MCD_MCP_TOKEN}" }
       }
     }
   }
   ```
   保存并**启用** mcd-mcp。
3. 把本仓库 `skill/` 目录作为 WorkBuddy 用户级 Skill 安装（复制到 `~/.workbuddy/skills/mcd-nutrition-saver/`）。
4. `scripts/make_report.py` 与根目录 `mcp_client.py` 均为**纯标准库 Python 脚本，无需 pip 安装**任何依赖。

## 使用示例

- 「帮我看看巨无霸套餐的热量，配成不超过 800 大卡的午餐」
- 「用我现在的券，这单能省多少」
- 「生成一份这顿麦当劳的营养 + 省钱报告」

WorkBuddy 会调用麦当劳 MCP 工具（`list-nutrition-foods` / `query-meals` / `calculate-price` / `available-coupons` 等）取数，再调用 `scripts/make_report.py` 生成可视化报告。

## 本地验证（无需 WorkBuddy，命令行即可跑通）

```bash
export MCD_MCP_TOKEN="你的Token"
python mcp_client.py            # 联调：打印营养/优惠券/菜单概要
python mcp_client.py --report   # 拉真实数据并直接生成 example_report.html
python gen_report.py            # 用本地缓存的真实数据(data/)生成示例报告
```

## 目录结构

| 文件 | 说明 | 是否必须 |
|---|---|---|
| README.md | 项目介绍、安装、使用示例、目标用户 | 必须（文件名不可改） |
| CONTEST_DECLARATION.md | 官方参赛声明（内容不可改） | 必须（文件名+内容不可改） |
| MCP_INTEGRATION.md | 实际使用的 MCP Server / Tool / 调用流程 / 业务价值 | 必须（文件名不可改） |
| mcp-config.example.json | 脱敏 MCP 配置示例（仅环境变量占位符） | 必须（文件名不可改） |
| skill/SKILL.md | WorkBuddy Skill 定义（工作流） | 源代码（形式不限） |
| mcp_client.py | 麦当劳 MCP 真实客户端（标准库，Streamable HTTP） | 源代码（形式不限） |
| scripts/make_report.py | 本地可视化报告生成器（纯标准库） | 源代码（形式不限） |
| gen_report.py | 用本地缓存真实数据生成示例报告 | 辅助脚本 |
| data/nutrition_real.json | 实测抓取的 160 项真实营养数据 | 辅助（证据） |
| data/coupons_raw.txt | 实测抓取的真实可领优惠券 | 辅助（证据） |
| example_report.html | 用真实数据生成的示例报告 | 辅助（演示） |
| workbuddy.md | WorkBuddy 开发对话 + 真实 MCP 联调记录（积分核验用） | 参加 WB 专项奖励必须提交 |

⚠️ 餐品信息、价格及供应状态以麦当劳官方渠道实时结果为准；营养数据仅供参考，不构成医疗或营养专业建议。支付由用户本人完成，Skill 只建单不付款。

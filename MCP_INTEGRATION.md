# MCP 接入说明 (MCP_INTEGRATION.md)

> 官方文档：https://open.mcd.cn/mcp/doc
> 本文与官方文档逐条对齐，并已用真实 Token 实测联调通过。

## 1. 接入概要（官方口径）

| 项 | 值 |
|---|---|
| 协议 | **Streamable HTTP**（非 SSE、非 stdio） |
| Endpoint | `https://mcp.mcd.cn` |
| 认证 | 请求头 `Authorization: Bearer <MCP_TOKEN>` |
| Token 领取 | https://open.mcd.cn/mcp → 手机号登录 → 右上角「控制台」→ 激活 → 复制 |
| 频率限制 | 每 Token **600 次 / 分钟**，超限返回 **429** |
| 错误码 | `401` = Token 无效/过期/未提供；`429` = 限流 |
| 安全 | Token 等同于账号钥匙，**切勿公开分享或提交到公开仓库**（本仓库 `mcp-config.example.json` 已脱敏为 `${MCD_MCP_TOKEN}` 占位符） |

## 2. 配置 JSON（脱敏，填 Token 即可用）

`mcp-config.example.json`：

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": {
        "Authorization": "Bearer ${MCD_MCP_TOKEN}"
      }
    }
  }
}
```

把 `${MCD_MCP_TOKEN}` 替换成你的真实 Token 即可。本项目 `mcp_client.py` 同时支持读环境变量 `MCD_MCP_TOKEN`（命令行本地用）和上面这个 JSON（客户端导入用）。

## 3. 本项目实际使用的 Tool（已实测）

围绕「营养分析 + 省钱对比」两个场景，本项目调用以下 Tool（均为 `tools/list` 返回的 35 个真实工具之一）：

| Tool | 用途 | 实测 |
|---|---|---|
| `list-nutrition-foods` | 餐品营养基准（能量/蛋白/脂肪/碳水/钠/钙），无需入参，返回 160 项 | ✅ |
| `query-meals` | 当前可售餐品菜单（编码/分类） | ✅ |
| `query-meal-detail` | 餐品/套餐详情、可替换项（`code` 必填） | 计划 |
| `calculate-price` | 含优惠券计价（`items` 必填，需门店上下文） | 计划 |
| `available-coupons` | 麦麦省可领券列表，无需入参 | ✅ 实时 3 张 |
| `auto-bind-coupons` | 一键领麦麦省券，无需入参（需用户授权） | 计划 |
| `query-store-coupons` | 当前门店可用券（`storeCode`/`beCode`/`orderType`/`beType` 必填） | 计划 |
| `campaign-calendar` | 当月活动日历（`specifiedDate` 选填） | 计划 |
| `now-time-info` | 当前时间，无需入参 | 计划 |

## 4. 完整工具清单（35 个，官方口径）

### 点餐模块
| Tool | 用途 | 关键入参 |
|---|---|---|
| `list-nutrition-foods` | 餐品营养信息列表 | 无 |
| `delivery-query-addresses` | 用户可配送地址列表 | 无 |
| `delivery-create-address` | 新增配送地址 | `city,contactName,phone,address,addressDetail`(必) |
| `delivery-query-stores` | 可配送门店列表 | `addressId,beType`(必) |
| `query-meal-assistance` | 团餐助餐服务 | `storeCode,beCode,beType,orderType`(必) |
| `query-nearby-stores` | 附近可用门店 | `searchType,beType`(必) |
| `query-store-coupons` | 门店可用券 | `storeCode,beCode,orderType,beType`(必) |
| `query-meals` | 可售餐品列表 | `storeCode,beCode,orderType,beType`(必) |
| `query-meal-detail` | 餐品详情 | `code`(必) |
| `calculate-price` | 价格计算 | `items[].productCode/quantity`(必) |
| `create-order` | 创建订单 | `items`(必) + 地址/取餐码 |
| `cancel-order` | 取消订单 | `orderId,cancelReasonCode`(必) |
| `query-order` | 订单详情 | `orderId`(必) |
| `order-list` | 历史订单（最多最近 10 笔） | 无 |

### 互动 / 内容模块
| Tool | 用途 | 关键入参 |
|---|---|---|
| `campaign-calendar` | 活动日历 | `specifiedDate`(选) |
| `query-lottery-info` | 积分抽奖活动信息 | 无 |
| `draw-lottery` | 积分抽奖（1 秒限 1 次） | 无 |
| `query-my-prizes` | 我的奖品 | `pageNum,pageSize`(选) |

### 麦麦省领券模块
| Tool | 用途 | 关键入参 |
|---|---|---|
| `available-coupons` | 麦麦省券列表 | 无 |
| `auto-bind-coupons` | 一键领券 | 无 |
| `query-my-coupons` | 我的优惠券 | 无 |

### 麦麦商城 / 积分模块
| Tool | 用途 | 关键入参 |
|---|---|---|
| `query-my-account` | 我的积分 | 无 |
| `mall-points-products` | 商城商品列表 | `catRuleIds`(选) |
| `mall-product-detail` | 商品详情 | `spuId`(必) |
| `mall-create-order` | 积分兑换下单 | `skuId,spuCategory`(必) |
| `mall-order-list` | 商城订单 | `lastId,size`(选) |
| `mall-order-detail` | 商城订单详情 | `orderId`(必) |

### 主题活动模块
| Tool | 用途 | 关键入参 |
|---|---|---|
| `query-party-city` | 主题活动城市 | `spuId`(必) |
| `query-party-store` | 主题活动门店 | `spuId,code`(必) |
| `query-partystore-date` | 可预约日期 | `spuId,storeCode`(必) |
| `query-partystore-session` | 可预约场次 | `spuId,storeCode,dateStr`(必) |
| `party-order-create` | 主题活动下单 | 多项必填 |

### 通用模块
| Tool | 用途 | 关键入参 |
|---|---|---|
| `now-time-info` | 当前时间信息 | 无 |

## 5. 客户端接入步骤

### A. WorkBuddy（本机，推荐）
1. 把上面的 JSON 填好 Token。
2. 写入本机 MCP 配置 `~/.workbuddy/mcp.json`（与已有 server 合并，不要覆盖）。
3. 打开 WorkBuddy 自定义连接器入口，对 `mcd-mcp` 点「信任」启用。
4. 之后在对话里直接自然语言调用（见 `skill/SKILL.md` 的用法示例），WorkBuddy 会自动走 `initialize` 握手并调用工具。

> 也可以不写配置文件：在 WorkBuddy 连接器 UI 里选「自定义连接器 → 配置 MCP」粘贴 JSON 即可。

### B. 其他客户端（官方参考）
- **Cherry Studio**：设置 → MCP → 添加 → 从 JSON 导入
- **Cursor**：设置 → Tools & MCP → Add Custom MCP → 编辑 `mcp.json`
- **TRAE**：设置 → MCP → 手动添加
- **VSCode**：Copilot → 自定义 MCP Server

### C. 命令行 / 自研（本项目 `mcp_client.py`）
纯标准库实现，已封装取数与报告生成：
```bash
export MCD_MCP_TOKEN="你的Token"
python mcp_client.py --report     # 拉真实数据生成 example_report.html
python mcp_client.py --all         # 打印营养/优惠券/菜单概要
python mcp_client.py --nutrition   # 仅营养
python mcp_client.py --coupons     # 仅优惠券
python mcp_client.py --meals       # 仅菜单
```

## 6. 典型调用流程（本项目）

1. 用户需求（营养透视 / 省钱对比 / 完整报告）。
2. **营养取数**：`list-nutrition-foods` + `query-meals`/`query-meal-detail`。
3. **优惠取数**：`query-store-coupons` + `available-coupons` + `campaign-calendar`；用户同意可 `auto-bind-coupons`。
4. **计价**：`calculate-price` 算原价 vs 用券价。
5. **出报告**：`scripts/make_report.py` 生成单文件 HTML（营养雷达图 + 省钱对比 + 真实券卡片）。

## 7. 数据 Schema（与真实工具对齐）

`list-nutrition-foods` 返回 TOON 紧凑文本，每行：`name,kj,kcal,protein,fat,carbs,sodium,calcium`。
`make_report.py` 内部字段：`name, energy_kcal, protein, fat, carbs, sodium, calcium`。

## 8. 业务价值

把麦当劳分散的原子能力（营养/菜单/优惠/计价/订单）编排成「吃得明白 + 花得明白」闭环；已用真实 Token 实测联调（`initialize`/`tools/list`/`list-nutrition-foods`/`query-meals`/`available-coupons` 均成功），确保是真实可跑的产品，契合赛事主旨。

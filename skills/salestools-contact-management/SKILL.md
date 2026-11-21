---
name: salestools-contact-management
description: 在 Salestools 联系人库、M2、Zoho CRM 和公开网页中查找联系人，比较来源，浏览关系图谱，导入简历、名片或文字，维护档案并审核疑似重复。用户说「找一下某公司的联系人」「查 CRM 里的人」「这个人是谁、在哪工作」「导入名片/简历」「这段新闻里的人存一下」「这两个是不是同一个人」时使用。企业研究和拜访准备用 salestools-customer-assessment，复盘 Zoho 商机用 sales-deal-review。
---

# Salestools 联系人管理

先识别用户要查共享库、M2、CRM 或公开网页，或要导入、维护资料。以当前 MCP 工具声明为准，只使用实际可用的工具、参数和返回记录。

按[实际 MCP 调用与结果核对](references/mcp-execution.md)执行。共享图谱的搜索、档案、关系与分页直接调用并核对真实返回。账户确认、可能同步图谱的发现、导入和档案变更使用本 Skill 的[校验器](scripts/validate_mcp_call.py)执行 request/result，交回企业研究前执行 handoff。来自企业研究的找人任务先读[企业与联系人衔接](references/company-context.md)。

## 按意图选择工具与参考

| 意图 | 首选操作 | 何时读取参考 |
| --- | --- | --- |
| 复盘已有 Zoho 商机、评估成交风险或比较商机历史 | 使用[商机复盘 Skill](../sales-deal-review/SKILL.md)。 | 查看 MEDDPICC 证据、风险和历史复盘。 |
| 已有具体沟通，问下一次怎么推、见谁、问什么、写跟进邮件 | 使用[商机下一步 Skill](../sales-deal-next-steps/SKILL.md)，这里只提供所需人物资料。 | 核实参会人或引荐路径时按库内搜索参考。 |
| 在联系人库找姓名、公司、岗位或技能 | `search_contacts`，优先展示联系人图谱 App。 | 要翻页、核对证据、查未核实线索或项目客户时读 [库内搜索与图谱](references/library-search.md)。 |
| 看某人档案、问已有关系 | 用真实 `entity_id` 调用 `get_contact`；关系问答用 `ask_contacts`。 | 同上；多候选无法区分时先请用户选定。 |
| 查看符合条件的 M2 联系人的完整联系方式 | 在联系人图谱详情点击「查看完整联系方式」，在 Salestools 页面点击「显示联系方式」。 | 读 [M2 网页查看与额度](references/library-search.md#m2-网页查看与额度)。 |
| 查 Zoho CRM 公司联系人 | `discover_contacts(source:"zoho")`。 | 调用前读 [Zoho 查询与入库](references/zoho-discovery.md)。 |
| 查 M2 或并查 Zoho CRM 和 M2 | `discover_contacts(source:"m2")` 或 `discover_contacts(source:"zoho_m2")`。 | M2 使用部署配置的统一只读账号。启用共享图谱后，已取得的联系人自动同步并保留 M2 来源。 |
| 查公开网页联系人 | `discover_contacts(source:"web")`；并查网页和 Zoho CRM 用 `source:"all"`。 | 调用或续页前读 [网页发现与快照分页](references/web-discovery.md)。 |
| 导入简历或名片 | `open_contact_upload`，在 App 选文件、预览和确认。 | 操作前读 [导入与恢复](references/import-workflow.md)。 |
| 从文字提取/保存联系人 | `import_contacts_text`，复用预览与确认。 | 同上；不需要上传或 Docling。 |
| 从新闻或纪要提取/保存多人 | 按人摘录原文，逐人调用 `import_contacts_text`，汇总预览和结果。 | 先读[多人文字导入](references/import-workflow.md#多人文字导入)，逐人查重并核对公司归属。 |
| 修改、合并、归档、恢复或审核线索 | 先 `get_contact` 核对版本，再调用对应写工具。 | 操作前读 [维护与身份核对](references/record-maintenance.md)。 |
| 某企业的决策层、研发骨干或关键人 | 转到企业研究 skill 的 `get_company_key_people`；启用图谱时会异步同步公开人物线索。库内按姓名核对待核实记录时用 `search_contacts` 的 `include_unverified:true`。 | 读 [关键人](../salestools-customer-assessment/references/key-people.md)。 |
| 企业关联或背景 | 现有工具的企业上下文功能。 | 读 [企业关联](references/company-context.md)。 |
| 客户开发简报、首次拜访或会前准备 | 转到企业研究 skill 的共享拜访或只读草稿场景；这里只提供所需人物与 CRM 资料。 | 读 [客户开发简报与拜访准备](../salestools-customer-assessment/references/sales-briefs.md)。 |
| 持续企业研究、产品销售专题或单产品多企业比较 | 转到企业研究 skill，按相应研究/比较工具执行，不靠联系人搜索生成机会评级。 | 读 [企业研究与客户开发](../salestools-customer-assessment/SKILL.md)。 |

只读取当前任务需要的参考，不默认加载全部文档。企业研究或产品机会判断使用 [企业研究 skill](../salestools-customer-assessment/SKILL.md)。

## M2 查询与展示

- M2 单查用 `source:"m2"`，与 Zoho CRM 并查用 `source:"zoho_m2"`。并查时分别读取 `m2` 和 `zoho`，标明各自来源和状态。一个来源失败时仍展示另一来源已取得的结果。区分查询完成但无结果、待确认公司、分页未完和来源失败。
- `m2.status="needs_confirmation"` 时请用户确认公司，再把该候选的 `selection` 作为 `m2_cursor`。续页使用 `m2.next_cursor`。两种调用均保留原 `query`、`source` 和已有的 CRM 选择参数。游标只用于工具调用。
- 脱敏以服务端结果为准，保留姓名掩码、来源标签和独立联系人记录，见[联系人边界](references/contact-limits.md#联系方式与脱敏)。需要查看符合条件的 M2 完整业务联系方式时，指引用户通过图谱按钮在网页查看。
- OAuth 刷新由服务端使用统一只读账号处理。收到 `M2_AUTH_REQUIRED` 时提示联系管理员核对或重新授权该账号。查询用户无需提供令牌或密码。遇到限流、超时或其他失败时按实际错误报告，仍保留已取得的 CRM 结果。

“综合查找”未限定来源时，先查库；有明确目标公司再查网页，最后核对相关档案。用户指定来源或顺序时遵从；项目客户或学校关键词不自动作为招聘目标公司。

## 呈现与边界

- 按[展示格式](references/display.md)呈现：UI 优先，聊天先汇总再列明细，列表默认不超过 10 行。文字入口、CRM 或 M2 公司候选确认在聊天完成。不为浏览图谱打开上传 App，也不反复创建会话。UI 优先不改变保存或合并授权。
- 现任、项目客户、疑似重复、会写入的操作、脱敏和企业额度按[联系人边界](references/contact-limits.md)处理。
- 交付前按[质量自检](references/quality-check.md)静默检查。

## 完成标准

搜索报告实际命中范围、来源与警告；档案核对引用真实记录与证据；导入只有提交成功并回读才能称已入库；分别说明 Zoho、M2 的查询完整性与图谱同步状态。

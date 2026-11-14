---
name: salestools-contact-management
description: Use when looking up contacts in the Salestools library, M2, Zoho CRM, or public web, comparing contact sources, browsing the relationship graph, importing resumes, business cards, or text, or reviewing contact records and possible duplicates.
---

# Salestools 联系人管理

先识别用户要查共享库、M2、CRM 或公开网页，或要导入、维护资料。以当前 MCP 工具声明为准，只使用实际可用的工具、参数和返回记录。

调用前后遵循[实际 MCP 调用与结果核对](references/mcp-execution.md)，执行 [参数/结果校验脚本](scripts/validate_mcp_call.py) 的 request/result 阶段；交回企业研究前执行 handoff。脚本使用本次在线元数据和真实调用记录，未通过就修正或报告缺口，不凭 ok:true 宣称成果已生成。来自企业研究的找人任务先读[企业与联系人衔接](references/company-context.md)，将已核实事实、待核实线索和未完成范围分别返回研究。

## 按意图选择工具与参考

| 意图 | 首选操作 | 何时读取参考 |
| --- | --- | --- |
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
- MCP 服务端统一脱敏。查询、图谱详情、来源证据、问答和导入预览中的敏感字段以服务端掩码或省略为准。保留姓名掩码、来源标签和独立联系人记录。需要查看符合条件的 M2 完整业务联系方式时，指引用户通过图谱按钮在网页查看。
- OAuth 刷新由服务端使用统一只读账号处理。收到 `M2_AUTH_REQUIRED` 时提示联系管理员核对或重新授权该账号。查询用户无需提供令牌或密码。遇到限流、超时或其他失败时按实际错误报告，仍保留已取得的 CRM 结果。

“综合查找”未限定来源时，先查库；有明确目标公司再查网页，最后核对相关档案。用户指定来源或顺序时遵从；项目客户或学校关键词不自动作为招聘目标公司。

## 默认优先 UI

- 搜索用 `search_contacts` 附带的图谱，文件导入用 `open_contact_upload`；用户不必额外说“打开 UI”。聊天只补充关键结论与警告，不默认输出 JSON 或重复全部详情。
- 宿主需要手动展开时提示用户；调用成功不证明界面已显示。UI 不可用时提供真实工具结果的文字/表格，上传可用工具返回的备用链接。
- 文字入口、CRM 或 M2 公司候选确认在聊天完成。Zoho 或 M2 同步后可按公司关键词查看图谱，并说明当前显示的库内命中范围。
- 不为浏览图谱打开上传 App，也不反复创建会话。UI 优先不改变保存或合并授权。

## 关键边界

- 正式图谱事实不等于人工核实。`jobTitle`、CRM 更新时间或没有离职日期都不能证明现任；核对对应 `worksFor` 的状态、时间和证据。
- 企业研究引用个人技能、历史任职或项目软件经历时，保留人物、企业归属、项目角色和日期限制；这些是需求探索线索，不能提升成企业当前部署或采购事实。比较中的职业联系条件独立展示，不参与产品机会排名。
- 同名、同机构或联系方式匹配只提示可能重复，不自动合并。身份线索长期保留；审核方法见维护参考。
- `discover_contacts` 不返回电话、邮箱；Zoho、M2 和已配置的网页快照同步可能写图谱。用户要求“不保存”时先确认部署支持，现有工具没有单次关闭同步参数。
- 只查看或提取资料不授权正式写入。明确授权保存后按导入参考执行；新建有效资料不必先解决疑似重复。
- 来源失败、未查到或分页未完成不等于不存在。保留不确定性，不自动新增档案来填补查询缺口。

## 完成标准

搜索报告实际命中范围、来源与警告；档案核对引用真实记录与证据；导入只有提交成功并回读才能称已入库；分别说明 Zoho、M2 的查询完整性与图谱同步状态。
向用户展示人物、公司和岗位名称，内部 ID 仅用于工具调用、来源核对或用户明确需要时展示。

联系人读取返回 `CONTACT_COMPANY_QUOTA_EXCEEDED` 时，展示服务端 `retry_at`（含时区），停止本次联系人读取，包括网页查看。收到 `CONTACT_COMPANY_QUOTA_UNAVAILABLE` 时说明额度暂不可核验，可稍后由用户重新发起。

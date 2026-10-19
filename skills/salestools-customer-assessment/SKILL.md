---
name: salestools-customer-assessment
description: Use when researching Chinese companies through Salestools MCP, continuing shared company research, exploring product sales scenarios, preparing first visits, comparing companies for one product, asking company questions, or requesting formal seven-product assessments. Standalone contact search and imports belong to salestools-contact-management.
---

# Salestools 企业研究与客户开发

以当前连接实际提供的 MCP 工具和返回结果为准。四阶段代码已实施，不证明当前连接已部署或开启功能；缺少工具时说明缺失环节，不模拟成果或自动修改部署配置。只编排调用、解释证据，不自行补算产品等级。普通了解先提供基础画像，正式七产品评估仍须用户明确要求。

执行时遵循[实际 MCP 调用与结果核对](../salestools-contact-management/references/mcp-execution.md)，使用本 Skill 的 [执行校验入口](scripts/validate_mcp_call.py) 做 request/result 检查；两个 Skill 保持同级安装，共享实现和依赖。需要联系人资料时，按[企业与联系人衔接](../salestools-contact-management/references/company-context.md)传递已核验主体、所需产品/岗位与访问限制；联系人结果通过 handoff 检查后才作为已确认路径纳入研究，候选/缺证据单列为待核实。

## 按意图选择工具

| 用户意图 | 工具与必要动作 |
| --- | --- |
| 初步了解、公司基本情况 | `get_company_profile`；简称可用于候选搜索，多候选请用户选定。 |
| 持续研究、补充企业资料、核查软件使用或更新已有研究 | 读 [共享研究与产品专题](references/company-research.md)；读取已有成果后，按需求选择 `start_company_research` 的 initial/continue/refresh。持续表示可按需积累版本，不是定时监控。 |
| 围绕指定产品找新购、替换或补充机会 | 同一研究工具选择 `template_id:"product_sales_scenario"` 和明确 `products`，没有独立专题工具；读 [共享研究与产品专题](references/company-research.md)。 |
| 客户开发简报、怎么切入或开发某企业 | 读 [客户开发简报与拜访准备](references/sales-briefs.md)，复用研究及内部资源；指定产品的结构化探索用产品专题。 |
| 首次拜访、会前准备、与某岗位交流 | 读 [客户开发简报与拜访准备](references/sales-briefs.md)，用 `prepare_company_visit` 创建共享简报，`get_company_visit` 读取状态与结果；仅要现有资料草稿时走只读整理。 |
| 比较多家企业在某款产品上的机会或拜访优先级 | 读 [单产品企业比较](references/company-comparisons.md)，调用 `compare_company_opportunities`；只比较既有研究，不自动补研。 |
| 问具体问题、解释招聘证据、查近期变化 | `ask_company`；不要求先生成完整报告。调用前读 [定向追问](references/company-questions.md)。 |
| 明确要求正式体检、完整七产品评估 | 先用画像工具核验法定主体，再 `submit_assessment`。调用前读 [评估与报告](references/assessment-reports.md)。 |
| 查进度、读报告 | 用已有 `assessment_id` 调用状态或报告工具；结果含义与恢复见 [评估与报告](references/assessment-reports.md)。 |
| 找联系人、查 CRM、导入资料或看关系 | 使用 [联系人管理 skill](../salestools-contact-management/SKILL.md)，不为找人启动评估。 |

## 呈现与解释

- 有对应 MCP App 且宿主支持时优先展示 UI，聊天补充结论和警告。用户只要文字时遵从；没有 App 的工具使用可读文字，不把工具可供 App 调用误认为它自带界面。
- 四阶段成果默认“简要结论＋按需展开固定证据”。研究用 version_id，拜访用 brief_id，比较用 comparison_id 及企业标识；不要将这些 ID 与 assessment_id 混用，也不要用最新资料替换历史引用。
- 基础画像先给确认主体、行业标签、规模与经营线索；正式报告先给综合机会、推荐产品及有证据的理由，再概括产品机会、阻碍和销售行动。
- 保留来源、发布时间、采集/核验时间、冲突与缺口。任务 partial、产品 coverage 和各来源状态分别解释；处理范围完成不等于采购需求已确认。错误按返回值说明，不猜测。
- 招聘可证明岗位或软件场景，不能单独证明采购意向；融资是公司活跃度或时机信号，不代表项目预算；行业标签只展示。
- 个人技能、历史任职、供应商或项目中的软件经历是需求探索输入，保留归属和日期限制，不证明企业当前部署。changed/unavailable 及其失效依赖不能继续支撑新结论；unavailable 也不等于客户没有需求。
- 机会等级是销售适配判断，置信度是证据可靠性，均不是成交概率。“待核实”不强行改为推荐。
- 产品机会为主，职业联系条件单独展示；Owner、认识谁或联系人数量均不参与机会排名。保留简报的准备限制和必要问题，不为压缩首屏删掉关键警告。
- 需要图谱中的企业资料、历史报告或报告生成后的关联更新时，读 [企业关联与历史](../salestools-contact-management/references/company-context.md)。

## 创建、重读与完成标准

用户要求研究、生成共享拜访简报或比较时，按该范围创建相应成果；已有足够成果时先复用。start_company_research 会保存版本并可能调用外部来源；prepare_company_visit 会保存简报，缺资料时最多补研一次；compare_company_opportunities 保存比较快照但不自动研究。用户明确“不保存”“只读”“不调用外部来源”时不能擅自调用不符合限制的创建工具；只读现有成果并在聊天整理，具体分流见参考。

共享指当前服务认证团队可读，不代表生成了公开分享链接，也不授权向客户或外部人员发送材料。

三个创建工具均需要 operation_id。同一逻辑请求保留完整参数和同一 ID；结果未知时先按已有任务 ID 查询，确需幂等重放时仅原样重放一次。改变范围、版本或明确重新生成使用新 ID；不靠换 ID 绕过冲突、失败或队列限制。

取得任务 ID 只代表已受理；研究状态完成后按返回 version_id 读成果，拜访/比较需读到非空 result 才称已生成。异步等待要有界，用户单次问进度只查询一次。失败/取消/PROCESS_RESTARTED 不自动重发；明确未完成部分，不承诺没有持久机制支持的后续自动通知。

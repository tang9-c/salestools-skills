---
name: salestools-customer-assessment
description: 通过 Salestools MCP 研究中国企业：基础画像、持续研究与七产品机会判断、指定产品销售专题、首次拜访简报、关键人、单产品多企业比较和定向追问。用户说「了解一下某公司」「研究/更新这家企业」「这家公司怎么切入」「明天去拜访」「谁拍板、谁做研发」「这几家先跟哪家」或问企业具体问题时使用。单独找联系人、导入资料用 salestools-contact-management，复盘 Zoho 商机用 sales-deal-review。
---

# Salestools 企业研究与客户开发

以当前连接实际提供的 MCP 工具和返回结果为准。只编排调用、解释证据，不自行补算产品等级。普通了解先给基础画像，七产品机会判断由持续研究产出。

执行时遵循[实际 MCP 调用与结果核对](../salestools-contact-management/references/mcp-execution.md)，用本 Skill 的[执行校验入口](scripts/validate_mcp_call.py)做 request/result 检查；两个 Skill 保持同级安装，共享实现和依赖。调用创建类工具前按[任务、标识与副作用](references/tasks-and-ids.md)核对副作用、operation_id 和用户限制。需要联系人资料时，按[企业与联系人衔接](../salestools-contact-management/references/company-context.md)传递已核验主体、所需产品/岗位与访问限制；联系人结果通过 handoff 检查后才作为已确认路径纳入研究，候选和缺证据的单列为待核实。

## 按意图选择工具

| 用户意图 | 工具与必要动作 |
| --- | --- |
| 复盘已有 Zoho 商机、评估成交风险或比较商机历史 | 使用[商机复盘 Skill](../sales-deal-review/SKILL.md)。 |
| 初步了解、公司基本情况 | `get_company_profile`；简称可用于候选搜索，多候选请用户选定。 |
| 持续研究、补充企业资料、核查软件使用或更新已有研究 | 读[共享研究与产品专题](references/company-research.md)；读取已有成果后，按需求选择 `start_company_research` 的 initial/continue/refresh。持续表示按需积累版本，不是定时监控。 |
| 围绕指定产品找新购、替换或补充机会 | 同一研究工具选择 `template_id:"product_sales_scenario"` 和明确的 `products`，没有独立专题工具；读[共享研究与产品专题](references/company-research.md)。 |
| 客户开发简报、怎么切入或开发某企业 | 读[客户开发简报与拜访准备](references/sales-briefs.md)，复用研究及内部资源；指定产品的结构化探索用产品专题。 |
| 首次拜访、会前准备、与某岗位交流 | 读[客户开发简报与拜访准备](references/sales-briefs.md)，用 `prepare_company_visit` 创建共享简报，`get_company_visit` 读取状态与结果；只要现有资料草稿时走只读整理。 |
| 比较多家企业在某款产品上的机会或拜访优先级 | 读[单产品企业比较](references/company-comparisons.md)，调用 `compare_company_opportunities`；只比较既有研究，不自动补研。 |
| 谁拍板、谁做研发、决策链或关键人 | 先用 `get_company_profile` 确认法定主体，再调用 `get_company_key_people`，法定名称与信用代码须与画像一致；读[关键人](references/key-people.md)。 |
| 问具体问题、解释招聘证据、查近期变化 | `ask_company`，不要求先做完整研究；调用前读[定向追问](references/company-questions.md)。 |
| 要完整的七产品机会判断、「体检」或评估 | 没有单独的评估工具。核验法定主体后用 `start_company_research`，省略 products 默认七产品，完成后读 `product_assessments`；读[共享研究与产品专题](references/company-research.md)。 |
| 找联系人、查 CRM、导入资料或看关系 | 使用[联系人管理 skill](../salestools-contact-management/SKILL.md)，不为找人启动研究。 |

## 常用串联

用户的目标跨多步时按下列顺序推进，每步只取下一步需要的内容，已有成果先复用。

- **陌生企业到首次拜访**：画像确认主体 → 按需查关键人 → 拜访简报。交接法定名称、信用代码或 dossier_id、关心的产品和参会岗位。
- **指定产品找机会**：读已有研究 → 产品专题 → 用户需要排序时做单产品比较。交接 dossier_id、产品键和需要核实的问题。
- **已有商机**：转[商机复盘 Skill](../sales-deal-review/SKILL.md)。研究事实只作为复盘的线索和待核实问题，不能充当买方确认。

## 呈现与解释

按[展示格式](references/display.md)精简呈现，按[证据边界](references/evidence-limits.md)解释各类信号。任务的 partial、产品 coverage 和各来源状态分别说明。交付前按[质量自检](references/quality-check.md)静默检查，写法参照[正反例](references/examples.md)。需要图谱中的企业资料或组织关联时，读[企业关联](../salestools-contact-management/references/company-context.md)。

## 创建与完成

用户要求研究、生成共享拜访简报或比较时，按该范围创建相应成果；已有足够成果时先复用。副作用、只读限制、operation_id、等待、失败处理和共享范围见[任务、标识与副作用](references/tasks-and-ids.md)。

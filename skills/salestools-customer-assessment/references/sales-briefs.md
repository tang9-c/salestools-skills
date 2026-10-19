# 客户开发简报与拜访准备

复用共享研究，将事实整理为首次拜访的背景了解与需求探索。已提供共享首次拜访工具时优先使用；客户开发的临时文字简报仍可按资料整理。两者均不默认提交正式七产品评估。普通找人按联系人管理 skill，不因出现公司名就启动本流程。

## 共同取用规则

- 先看本轮已确认主体及已有研究、简报、画像、报告、联系人、CRM 结果和用户笔记。有 brief_id 时先 get_company_visit，有信用代码或 dossier_id 时可 get_company_research；研究的逐产品版本读取见 [共享研究与产品专题](company-research.md)。资料足够就复用，缺失、过时或冲突不自行补全。
- 同名、集团和子公司歧义先确认目标，不拼接不同主体的材料。基础画像用 `get_company_profile`；具体缺口用 `ask_company`，先读 [定向追问](company-questions.md)，遵循其主体和失败规则。将相关缺口合成具体问题，不逐栏目重复研究。
- 已有报告只在 ID 可定位、主体一致且内容相关时读取；当前上下文已有所需内容不重复读取。不猜 ID，不为简报新建报告；用户明确要求正式评估才按 [评估与报告](assessment-reports.md) 执行，不另算或改写原评级。
- 联系人查询遵循 [联系人管理 skill](../../salestools-contact-management/SKILL.md)。库内用 `search_contacts`；需核对某人时用真实 ID 调用 `get_contact`，不批量读全员档案。来源足够支持任务就停止，不默认翻完所有分页或查遍所有来源。
- `discover_contacts` 可能按部署配置同步图谱，不能称纯只读。用户要求不保存时，不绕过现有无单次禁用同步的限制。除既有查询同步外，本流程不额外保存、合并、修改 CRM 或发送消息。
- 图谱复用搜索附带的 App，按宿主实际支持展示；拜访工具当前返回文字摘要与结构化结果，在聊天呈现，不假设有独立拜访 App，也不把 UI 打开成功当成数据已核实。

## 客户开发简报

适用于“准备某企业开发简报”“这家公司怎么切入”。目标是说明已知情况、内部资源及下一步，不必先询问完整销售背景。

1. 复用已明确的目标主体；有歧义先确认。先查已有内部资源：缺少库内结果时 `search_contacts`，缺少 CRM 结果时按 [Zoho 查询与入库](../../salestools-contact-management/references/zoho-discovery.md) 调用 `discover_contacts(source:"zoho")`。已有相关结果不重查；未接入或失败就保留缺口，不阻止生成可用部分。
2. Zoho 返回 `needs_confirmation` 时展示候选及客户负责人，选定后按原连接和客户记录配对查询；企业画像确认不能代替 CRM 候选确认。选择前只整理明确属于目标的内容。
3. 基本画像缺失时取画像；影响开发方向的业务、工程或近期信号缺失时才定向追问。已有足够线索就不启动新研究；不默认用 `source:"all"` 搜索全部人物。
4. 用户要持续积累企业资料或围绕指定产品生成新购/替换/补充路径时，转到 [共享研究与产品专题](company-research.md)，使用持久研究模板；ask_company 不代替专题生成，也不把聊天分析称为已保存的专题版本。

默认一屏摘要，来源附后；有内容才展开对应部分：

- **开发判断**：最值得先验证的方向及理由，标明事实与销售假设。
- **内部资源**：本次 CRM 命中情况、客户/联系人负责人、相关人物及来源。Owner 表示记录负责人，不推断其认识客户或可引荐。
- **关键线索**：少量有来源、日期的业务与工程信号；没有可用证据就说明。
- **下一步**：优先接触的人物或岗位、交流主题、待确认问题；不知道姓名时给岗位或寻找方向，不编造人物。
- **资料限制**：未查询、失败、部分返回、过时或冲突分别说明。“本次查询未发现 CRM 记录”不等于全新客户。

## 共享首次拜访准备

适用于“明天首次拜访某公司”“准备与研发经理交流”“生成可共享拜访简报”。目标是背景了解与需求探索，不假设已有预算、项目或采购承诺。无需先生成正式体检或产品专题。

调用前确认限制：prepare_company_visit 会保存共享简报，并在资料不足时最多发起一次研究，也可复用已有共享研究。没有“禁止补研”或“不保存”参数。用户只要现有资料、不调用外部来源或不保存时，不使用此创建工具，按下方草稿分流处理。

1. 已有 dossier_id 可直接用它；否则 get_company_profile 核实法定名称和信用代码，再用 legal_name＋credit_code。两种标识形式互斥，不要混传，也无需为没有档案先手工创建研究。
2. prepare_company_visit 必填 operation_id；products、attendee_roles、meeting_date、parent_brief_id 可选。已知研发经理就传岗位，不因姓名或日期缺失阻塞；已知围绕 Creo 就显式 products:["creo"]。没有产品要求时让服务端按可靠场景选择，资料不足时可能覆盖七产品。日期传 YYYY-MM-DD，不能确定相对日期时省略，不编造。
3. 保存 brief_id，用 get_company_visit({brief_id}) 查询 queued/waiting_research/generating 与最终结果，不能把受理回执称为已生成。needs_research/reasons 是受理时判断；最终同时读 coverage、result.warnings 与 sections.limitations，不能拿初始值当最终状态。
4. 完成后先给简要结论，保留七节：企业背景、工程场景、软件线索、切入假设、现场问题、人员与岗位、待核实事项。按产品机会为主、联系条件单独展示；必要事实、假设限定、问题和准备限制不能在摘要整理时消失。
5. get_company_visit_evidence({brief_id,section?,offset?,limit?}) 展开冻结引用；section 用 background/scenes/software/hypotheses/questions/people/limitations，limit 上限 20，跟随 next_offset。重读结果与证据不会调用模型或来源。

最小调用示例；档案 ID 和 operation_id 需替换为本次真实值：

```json
{
  "dossier_id": "returned-dossier-id",
  "operation_id": "unique-visit-operation-id",
  "products": [
    "creo"
  ],
  "attendee_roles": [
    "研发经理"
  ]
}
```

与用户交流时突出 3–5 个最重要问题，完整结果仍保留所有必要问题与准备限制。系统警告放资料限制，不改造成销售应向客户追问的技术问题。没有日历、邮件、纪要或历史互动证据时明确未知，不编造上次承诺、客户态度或项目进度；会后下一步写建议，不写成已约定。

已有专题仅在安全 claims、时效与完整引用仍成立时复用为待验证路径，保留 historical 等原始语义；不为拜访默认创建新专题。历史任职、个人技能、供应商或项目经历可作为软件探索输入，保留来源、日期和“不证明企业当前部署”的限定。

## 只读草稿、重新生成与取消

- 用户明确只用现有资料/不保存时，读取现有 get_company_research/get_company_visit/证据及已有笔记，在聊天生成草稿；不调用 start_company_research、prepare_company_visit、可能补查的 ask_company 或可能同步图谱的 discover_contacts。没有成果就说明缺口并给中立问题。用户只限制外部调用但允许保存时，也不能假装 prepare_company_visit 可禁止自动补研。
- 工具在当前连接不可用时，可按用户允许的范围整理聊天草稿，明确不是服务端共享简报；不得声称已部署或已持久保存。
- 旧简报冻结于 source_selection_at，不随研究更新。用户明确要重新生成时，用新 operation_id，可带同企业 parent_brief_id；不覆盖原简报。
- 用户明确取消时用 cancel_company_visit({brief_id})；简报取消不停止共享研究，依据返回的 research_continues 说明。不要进一步取消 research_run_id 来代替取消简报。
- partial 保留可用部分并标限制；failed/cancelled/PROCESS_RESTARTED 不自动创建替代任务。使用同一 operation_id 原样重放只用于幂等恢复；新一轮生成需真实请求和新 ID。

## 解释与完成

关键事实附实际来源和日期；用户笔记标为用户提供，缺链接不造链接。假设、未知与未回答部分保留，不为了凑模板生成空章节。
招聘支持软件或工程场景，不代表采购意向；融资支持活跃度或时机，不代表项目预算；职位不证明决策权，同校、同公司或同场参会不证明熟识、上下级或可引荐。
单源失败仍给可用部分，将系统问题留在资料限制；不循环重试、不承诺后台补齐。聊天草稿与持久简报明确区分；只有 get_company_visit 返回非空 result 才称共享简报已生成，不代表完整体检、全员覆盖或真实需求已确认。

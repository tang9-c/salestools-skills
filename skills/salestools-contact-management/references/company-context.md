# 企业关联、背景与报告历史

仅在用户需要联系人任职企业背景、组织关联或历史报告时读取。企业体检调用遵循 [客户体检 skill](../../salestools-customer-assessment/SKILL.md)。

## 企业研究与联系人衔接

企业研究需要人物、任职、项目或 CRM 资料时，携带以下已知上下文；它们用于选择操作，不是可以一起塞进 MCP 请求的新参数：

- 已确认企业法定名称、credit_code，以及已取得的 dossier_id/version_id；集团、子公司和项目客户分别保留。
- 本次指定产品、目标岗位和要验证的问题，例如“Creo 使用经历”；不因为有联系人就扩大到所有产品或所有来源。
- 用户允许的来源及“不保存/只用现有资料”等限制、已经确认过的 CRM 候选配对，以及已完成查询范围。

先按目标公司在库内检索；支持时启用 include_company_context，回读相关人物、组织或项目。只有 confirmed 企业关联且 credit_code 与目标一致时，才作为跨库主体匹配；不能把 dossier_id、credit_code 或 CRM Account ID 直接填成 organization_id。只找到同名组织时保留候选，不能自动 link_company 或声称已匹配；仍可将来源明确的候选作为待核实线索交回研究。

需要 CRM 时按 [Zoho 查询](zoho-discovery.md)选定 connection_id + account_id 配对；研究已确认法定主体不等于 CRM 候选已确认。用户已选定的配对复用，不重复确认。CRM 连接代号 qx/st 仅在当前工具或已核实配置明确表明它就是连接 ID 时才能作为 zoho_accounts 值。读取成功后若需要图谱 ID，重新搜索并核对来源，不做字符串 ID 转换。

按研究问题读取相应证据：历史任职和个人技能保留人物、公司和时间；项目软件经历核对人物→项目及项目→客户两段关系，不等同于任职。若当前工具不能提供某段证据，就列为缺口，不通过新增档案或关系补齐。

交回研究时保留四类信息：

| 内容 | 必须保留的限定 |
| --- | --- |
| 人物与企业定位 | 姓名、岗位、真实标识及来源系统；主体确认还是同名候选。 |
| 研究输入 | 技能/软件、任职或项目关系路径、证据引用与日期，正式事实或待核实线索；“现任”须有对应证据。 |
| 联系条件 | CRM 客户/联系人 Owner、可用职业关系与缺口；独立于产品机会，不推断采购权或提高机会排名。 |
| 完整性 | 已读来源与分页范围、来源失败、图谱同步状态、warnings 与待核实项；超时后返回已有部分，不解释为无人或无需求。 |

回到企业研究后，按证据实际含义纳入聊天草稿或本次任务的研究输入；查到联系人不等于已写入研究版本。已有版本、拜访简报或比较快照保持原引用，需要保存新成果时走对应创建流程，不凭聊天整理声称已更新。

## 读取

工具支持时可在 search_contacts、get_contact、get_company_profile 传 include_company_context:true。
仅 confirmed 关联用于跨库画像、统计或事实回答；同名 candidate 仍须核对，信用代码须有效且有主体证据。学校不是雇主，unknown 任职不代表现任。

get_contact 历史报告分页独立使用 report_offset/report_limit，并跟随 reports.next_offset；不能用证据/关系页码代替。stale 资料可展示但须注明时效，不绕过 ask_company 新鲜度要求。

ask_contacts 企业背景与 ask_company 库内联系人/项目可引用确认资料，保留 context_citations，不推断采购权或现任。同一文件重复导入不算独立来源；保留实际截断、范围和 warnings。

## 人工关联

存在 link_company 工具且用户明确要求时，先读组织与关联版本。
confirm 传真实 organization_id、credit_code、operation_id、expected_link_version、expected_organization_version 和 note；actor 由认证提供，不作为输入。
unlink 使用当前版本与说明，省略 credit_code；revoked 抑制自动重新关联。身份冲突先重新核对，不自动改绑或合并组织。

## 报告与更新

get_assessment_report(include_related_updates:true) 返回生成后的关联更新，原正文不变。
说明 related_updates 的 scope、truncated、warnings；since 是报告生成时间，记录时间不等于事件时间。
UUID 不证明组织归属；App 报告只从当前节点目录打开，ask_company 指定报告须匹配主体。

浏览已有档案/历史不启动新的外部研究或正式评估。动态或库外问题可按用户意图走现有定向追问。
工具提供 App 时优先在 UI 浏览；宿主未实际验收不能用浏览器模拟测试冒称可用。

企业研究 dossier_id/version_id 与正式报告 assessment_id 分开。要继续共享研究或生成产品专题，按 [共享研究与产品专题](../../salestools-customer-assessment/references/company-research.md) 执行；首次拜访和多企业比较引用各自固定版本，不用最新画像覆盖旧证据，也不因联系人或 CRM 资料更新自动重排结果。

# 实际 MCP 调用与结果核对

企业研究与联系人管理共用此流程。通过当前宿主连接调用 MCP；无需项目 checkout、npm 命令、数据库或本机 Token。此流程降低误调用，不能保证远端服务始终可用。

## 执行时校验脚本

两个 Skill 一起安装，保留同级目录关系；共享实现位于本 Skill 的 [scripts/validate_mcp_call.py](../scripts/validate_mcp_call.py)，研究 Skill 提供同名入口。依赖 Python 3.10+ 和 jsonschema 4.x，依赖声明见 [requirements.txt](../scripts/requirements.txt)。已有满足要求的环境直接使用；缺依赖会返回 INSTALL_JSONSCHEMA，不会静默略过校验。可以在独立虚拟环境安装该 requirements 文件，不需要服务端源码、Node、数据库或 Token。

每次实际调用前执行 request，收到原始 MCP 返回后执行 result；交回企业研究前执行 handoff。脚本不调用 MCP、不自动重试、不保存输入，也不回显姓名、联系方式、原文或 ID 值。请求仍由宿主发送。临时输入文件可能含业务资料，使用仅当前用户可读的文件并在执行后清理，不放进 Git。

在任意工作目录执行，`<skill目录>` 换成当前实际安装位置：

```sh
python3 <skill目录>/scripts/validate_mcp_call.py request --file <本次调用.json>
python3 <skill目录>/scripts/validate_mcp_call.py result --file <本次调用及返回.json>
python3 <skill目录>/scripts/validate_mcp_call.py handoff --file <衔接记录.json>
```

也可从标准输入读取相同 JSON。退出码 0 表示该阶段校验通过，1 表示阻断，命令用法错误为 2。`ok:true` 不等于任务完成，必须同时读取 decision：dispatch_allowed 仅允许发送本次请求；waiting 等待任务；needs_confirmation 需按操作参考选定候选；partial 保留未完成范围；not_found 仅表示本次未取得记录；validated 只表示返回契约通过；ready_with_limits 只表示衔接路径有证据，不能证明现任或企业部署了软件。

request/result 输入结构（以下 ID 为示例占位，不得原样调用）：

联系人搜索无命中或末页允许省略 next_offset，但返回的非负整数 total 必须能证明 offset 加本页条数已覆盖结果；仍有未读记录却缺少游标时会阻断。不要为通过检查自行补写游标。

```json
{
  "tools": {
    "tools": [{
      "name": "get_contact",
      "inputSchema": {
        "type": "object",
        "properties": {"entity_id": {"type": "string"}},
        "required": ["entity_id"],
        "additionalProperties": false
      }
    }]
  },
  "call": {"name": "get_contact", "arguments": {"entity_id": "returned-person-id"}},
  "history": [{
    "call": {"name": "search_contacts", "arguments": {"query": "已核实企业名称"}},
    "response": {"structuredContent": {"items": [{"entity_id": "returned-person-id", "label": "Person"}]}}
  }],
  "constraints": {"no_save": true}
}
```

实际 tools 使用**当前连接 tools/list 的原始结果或宿主导出的 JSON Schema**，包括可用时的 outputSchema；不要复制上述精简 schema 冒充在线声明。宿主仅提供参数类型时，可显式记录并校验该类型子集，但不能宣称已验证服务器全部约束；拿不到 schema 时 request 会阻断。缺少工具、输入 schema、ID 来源或必要业务关联时不能为了通过检查补造元数据/历史。history 依次追加真实的 call 和完整 MCP response，result 阶段在顶层增加本次 response；它支持 structuredContent 或单个 JSON 文本内容。脚本优先检查 isError 和业务失败，再核对 schema、ID 一致性、状态与分页推进。

未提供 outputSchema 时，脚本仅对实现中明确支持的画像、研究/拜访/比较状态与成果、联系人搜索/档案/问答和发现结果做必要字段检查；其它结果返回 OUTPUT_CONTRACT_UNAVAILABLE，不能视为已完整校验。result 阶段阻断仅表示结果未通过检查，**不代表远端没有执行成功**；保留原返回和 operation_id，先回读核实，不自动重发写入。

首次接收用户提供的 ID 时先用宿主在线声明回读核实，将真实返回放进 history，再使用脚本衔接；此初次定位不能声称已有历史来源验证。写操作仍需各自授权、版本和幂等约束，脚本不替代服务端业务校验。参数里出现未记录 ID 会返回 ID_NOT_FROM_HISTORY；不要用 CRM record_id 填图谱 entity_id。继续/刷新研究还要求历史中有未指定 version_id 的最新档案读取，以核对 base_version_id。

拜访返回的 `research_run_id` 是其自动补研任务标识，可直接作为 `get_company_research_status.run_id`；脚本认可这个来源别名。仍须来自本次成功回包的真实 history，不能自行填造或拿 `brief_id` 代替，无需为了别名再绕查版本目录。

CRM 候选必须经用户选定。提交 zoho_account_records 时，在校验输入顶层另附 `confirmations:{"crm_accounts":[{"connection_id":"实际连接ID","account_id":"用户选定的实际客户ID"}]}`；它是本轮人工选择的执行记录，不是 MCP 参数，不放进 call.arguments。脚本同时核对该配对确实出现在真实历史和选择记录中；只有候选列表不能通过。复用已确认选择时保留此记录，不重复打扰用户。此记录仍由执行者如实提供，脚本不能替用户作出选择或鉴定聊天授权。

handoff 阶段不需要 tools/call，但需要同一份 history 和明确目标：

```json
{
  "history": [],
  "handoff": {
    "credit_code": "verified-credit-code",
    "organization_id": "returned-organization-id",
    "entity_id": "returned-person-id"
  }
}
```

这里空 history 故意不能通过。实际必须包括单一已核实企业画像、Organization 档案及 confirmed 同信用代码关联、Person 档案，以及带 evidence_id 的 worksFor 关系证据。按项目客户衔接时增加 project_id，并提供 Project 档案、Person→Project 的 memberOf 和 Project→Organization 的 clientOrganization 两段证据；不能将项目关系转写为任职。脚本仅检查本次加载的证据；分页缺失导致的缺证据应继续读取必要页，不能直接认定关系不存在。

脚本校验的是提供给它的元数据与调用记录，不鉴定这些材料的真实性、远端权限或时效，也不将联系人发现结果自动写入固定研究版本。修改脚本后可执行同目录 test_validate_mcp_call.py；仓库中 tests/skill-mcp-runtime-chain.test.ts 另验证 MCP SDK 真实处理器的合成链路。

## 调用前

1. 按用户目标选择主 skill 路由，并读取该操作的参考；企业研究需要找人时，先读[企业与联系人衔接](company-context.md)。只取本次需要的来源、产品、岗位与资料范围。
2. 查看当前连接实际公开的工具名称、描述和输入 schema。宿主支持延迟工具发现时先发现所需工具；工具仍缺失则说明阻塞步骤。不能用本地实现、旧示例或相似工具名代替在线声明，也不自行建立带凭据的 HTTP 客户端绕过宿主。
3. 以在线 schema 核对必填项、类型、枚举、互斥字段和分页上限；仅发送该工具支持的字段。业务参考补充 schema 未表达的限制，例如 include_unverified 需要 keyword 和非空 query。参考与在线声明冲突时不猜参数，说明版本差异，按可核实的在线能力执行。缺少参数导致无法保留主体、范围、固定版本、只读或幂等要求时，停止该步骤并交回可用部分，不能静默省略后执行。
4. ID 取自用户明确指定且已回读核对的记录，或本轮实际返回结果；按用途区分下表。多个主体无法区分时才请求选定，已有明确选择则复用。不把名称、示例占位符或另一个系统的 ID 填入标识字段。

| 标识 | 用途与核对 |
| --- | --- |
| credit_code / dossier_id / version_id | 已核实企业、研究档案与固定版本；写研究的 base_version_id 另取档案全局最新版本。 |
| entity_id / organization_id | 图谱人物或组织；通过库内搜索、档案及 confirmed 企业关联核对。CRM Account ID 不能代替。 |
| connection_id + account_id | 同一个 CRM 连接下的客户记录配对；组织代号、显示名称不自动等于连接 ID。 |
| run_id / brief_id / comparison_id / assessment_id / import_id | 各自任务或成果的返回标识；按对应状态/读取工具继续，不相互转换。 |

有写入或自动同步的操作先遵守用户范围。特别是 discover_contacts 可能同步图谱，不能按“搜索工具”一概当作只读；“不保存”任务使用符合限制的已有资料读取。写工具要求版本或 operation_id 时按各自参考准备，不向只读工具附加这些参数。

## 调用后

先检查宿主调用异常及 MCP 的 isError，再检查业务失败码、status、found、warnings 与来源完整性。宿主保留 structuredContent 时从中读取业务对象；只有文本形式时仅在确为 JSON 时解析，保留原错误与警告。文本和结构化内容是同一结果的不同呈现，不累计成两份证据。

- content 的“操作已完成”不能覆盖结构化的 queued/running 或空 result。取得任务 ID 表示受理；研究、拜访、比较按对应参考读取最终成果。
- found:false、空列表、部分来源失败、分页未完分别说明；不能由其中一个推导“此人不存在”“企业没有需求”或“已全部同步”。
- CRM 读取结果与图谱同步结果分别核对。需要图谱档案时再搜索并回读真实 entity_id；没有图谱映射不自动手工新建或合并。
- 保存/维护成功后，按返回标识回读相关档案或导入结果，再称已生效。工具没有提供足够结果时标为待核验。

## 分页、失败与恢复

分页保持原主体、筛选、来源及固定快照/版本，只使用对应集合返回的 next_offset。网页续页保持 web_snapshot_id 并用 source:web；档案的证据、关系、待核实线索与历史报告各走独立偏移。下一页重复或偏移不推进时停止，说明未取得完整范围。只需要局部证据时可停止并注明已读范围。

| 情况 | 后续动作 |
| --- | --- |
| 纯只读调用临时网络失败 | 在本次任务内至多原样重试一次；仍失败就保留已有结果并说明缺口。discover_contacts、创建任务及导入不归入此类。 |
| 写入、同步或创建请求超时/响应丢失 | 状态未知；有任务 ID 时先查询。仅在工具明确支持幂等且确需恢复时，使用相同 operation_id 和完整原参数重放一次；不得换 ID 试探。没有安全查询/重放能力就报告未知。 |
| 参数错误、主体歧义、权限不足或版本冲突 | 修正已确认的参数或先回读主体/版本；不重复原错误，不切换身份/连接绕过，不自动覆盖更新。 |
| 限流、队列满、任务仍运行 | 尊重返回的等待提示；有界查询，单次问进度只查一次。不给无限重试或后台通知承诺。 |
| failed / cancelled / PROCESS_RESTARTED | 返回失败原因与已完成部分；不把新的任务当作自动恢复。用户要求重新执行后按对应参考创建。 |

研究接收联系人结果时，回传确认主体、来源、关系路径、证据时间、核实状态及未完成范围；结果只支持它实际证明的事实。详见[衔接约定](company-context.md)。

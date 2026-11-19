# 校验脚本输入格式

本页供组装校验输入时查阅。每次调用要做的检查见[实际 MCP 调用与结果核对](mcp-execution.md)。

## 运行

两个 Skill 一起安装并保留同级目录；共享实现位于本 Skill 的 [scripts/validate_mcp_call.py](../scripts/validate_mcp_call.py)，研究 Skill 提供同名入口。依赖 Python 3.10+ 和 jsonschema 4.x，见 [requirements.txt](../scripts/requirements.txt)；缺依赖返回 `INSTALL_JSONSCHEMA`，不会静默略过。可在独立虚拟环境安装，不需要服务端源码、Node、数据库或 Token。

```sh
python3 <skill目录>/scripts/validate_mcp_call.py request --file <本次调用.json>
python3 <skill目录>/scripts/validate_mcp_call.py result --file <本次调用及返回.json>
python3 <skill目录>/scripts/validate_mcp_call.py handoff --file <衔接记录.json>
```

也可从标准输入读取相同 JSON。退出码 0 表示该阶段通过，1 表示阻断，2 为用法错误。脚本不调用 MCP、不自动重试、不保存输入，也不回显姓名、联系方式、原文或 ID 值。临时输入文件可能含业务资料，使用仅当前用户可读的文件并在执行后清理，不放进 Git。

## request / result

以下 ID 为示例占位，不得原样调用：

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

- `tools` 使用当前连接 tools/list 的原始结果或宿主导出的 JSON Schema，包括可用时的 outputSchema；不要复制上面的精简 schema 冒充在线声明。宿主只提供参数类型时，可显式记录并校验该子集，但不能宣称已验证服务器全部约束。拿不到 schema 时 request 会阻断。
- `history` 依次追加真实的 call 和完整 MCP response；result 阶段在顶层加本次 `response`，支持 structuredContent 或单个 JSON 文本内容。缺少工具、schema、ID 来源或必要业务关联时，不能为通过检查补造元数据或历史。
- 脚本先检查 isError 和业务失败，再核对 schema、ID 一致性、状态与分页推进。未提供 outputSchema 时只对已支持的画像、研究/拜访/比较、联系人搜索/档案/问答和发现结果做必要字段检查，其余返回 `OUTPUT_CONTRACT_UNAVAILABLE`，不能视为已完整校验。
- 联系人搜索无命中或末页可以省略 `next_offset`，但返回的 `total` 必须证明 offset 加本页条数已覆盖结果；仍有未读记录却缺游标时会阻断。不要为通过检查自行补写游标。
- 参数里出现未记录的 ID 返回 `ID_NOT_FROM_HISTORY`。首次接收用户提供的 ID 时，先用在线工具回读并放进 history；这次初次定位不能声称已有历史来源验证。不要用 CRM record_id 填图谱 entity_id。

研究相关的补充：

- 继续或刷新研究要求 history 中有未指定 version_id 的最新档案读取，用于核对 base_version_id。
- 拜访返回的 `research_run_id` 可以直接作为 `get_company_research_status.run_id`，脚本认可这个来源别名；它仍须来自本次真实回包，不能拿 `brief_id` 代替。

CRM 候选必须经用户选定。提交 `zoho_account_records` 时，在校验输入顶层另附 `confirmations:{"crm_accounts":[{"connection_id":"实际连接ID","account_id":"用户选定的实际客户ID"}]}`。它是本轮人工选择的执行记录，不是 MCP 参数，不放进 `call.arguments`。脚本核对该配对确实出现在真实历史和选择记录中，只有候选列表不能通过。复用已确认的选择时保留此记录。脚本不能替用户作出选择或鉴定聊天授权。

## handoff

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

这里空 history 故意不能通过。实际 history 必须包括单一已核实企业画像、Organization 档案及 confirmed 同信用代码关联、Person 档案，以及带 evidence_id 的 worksFor 关系证据。按项目客户衔接时增加 `project_id`，并提供 Project 档案、Person→Project 的 memberOf 和 Project→Organization 的 clientOrganization 两段证据，不能把项目关系转写为任职。脚本只检查本次加载的证据；证据在未读的分页里时继续读取必要页，不能直接认定关系不存在。

脚本校验的是提供给它的元数据与调用记录，不鉴定这些材料的真实性、远端权限或时效，也不把联系人发现结果自动写入固定研究版本。

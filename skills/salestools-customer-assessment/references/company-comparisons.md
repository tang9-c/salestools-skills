# 单产品企业比较

用于用户已明确的 2–10 家企业、同一款产品的机会/拜访优先级。当前部署必须提供三个比较工具；不为缺少工具自动启用配置或模拟服务端排名。

## 受理前

- 确定一款 product；用户未指定且上下文不能确定时先问产品。companies 每项只用真实 credit_code 或 dossier_id；名称不足以提交，同一企业不能用两个标识重复加入。
- 可以 get_company_profile 消除主体歧义；已有有效标识无需为比较逐家重新查画像。没有研究档案但有已确认的信用代码可以参与比较，服务端列入 needs_research，不创建研究档案。
- 用户“只用现有研究比较”允许本地生成比较快照。compare_company_opportunities 会保存共享任务和结果，并按需读取本地图谱；不调用模型、搜索、QCC、CRM，也不自动补研。用户另有限制“不保存”时，只读已有结果，在聊天整理；没有工具参数可将新建比较改为不保存。

## 创建、读取与证据

compare_company_opportunities 参数示例；实际调用须替换为真实标识和本次唯一 operation_id：

```json
{
  "operation_id": "unique-comparison-operation-id",
  "product": "creo",
  "companies": [
    {
      "dossier_id": "returned-company-a-dossier-id"
    },
    {
      "dossier_id": "returned-company-b-dossier-id"
    }
  ]
}
```

1. 保存 comparison_id。受理时固定所有企业的产品版本和 assessed_at；不要给输入增加 version_id、force_refresh、排序权重等未声明参数。
2. 用 get_company_comparison({comparison_id}) 读取状态和 result；queued/running 时只说明处理中，result 非空后呈现。比较无独立 status 工具，也没有 cancel_company_comparison 工具。
3. 先概括 ranked 的机会、置信度、有效时机和明确阻碍；保留并列名次，信用代码只稳定展示，不能拿它解释优先级。
4. needs_research 单列企业、原因和待核实问题。资料缺失、changed/unavailable、过期、冲突或方法不兼容不能按低机会硬塞排名。是否进一步研究按用户请求决定；未经授权不批量调用 start_company_research。
5. contacts 是独立联系快照，保留 contact_snapshot_at、complete 和 warnings；未完整读取为未知，不说没有联系人。联系人数量、Owner、可引荐推测不参与产品排名。
6. 展开证据用 get_company_comparison_evidence({comparison_id,credit_code,claim_id?,offset?,limit?})；limit 上限 20，跟随 next_offset。credit_code 必须属于本次比较，claim 必须属于该企业该产品的固定版本；不传外部 version_id 替换它。COMPARISON_EVIDENCE_UNAVAILABLE 就说明固定依据不可读取，不偷偷改用最新版本。

## 更新比较与停止

重读不会重排，也不受随后新增研究影响。用户要求重新比较时，用新 operation_id 新建；可传 previous_comparison_id 对照变化，但产品及企业集合必须相同。变化包含版本、资格、排名、时间、策略或联系快照，不把排名变化一律称企业发生了业务变化。

任务 partial 可以保留固定排名及部分联系条件，按 warnings 和未完整项说明。failed/PROCESS_RESTARTED 不自动重算。COMPARISON_RESULT_TOO_LARGE、队列或用户上限按实际错误报告，不拆分企业或换 ID 偷绕用户范围。仅需看已有比较时只调用 get 和证据工具。

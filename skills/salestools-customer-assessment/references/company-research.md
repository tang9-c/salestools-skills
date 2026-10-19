# 共享企业研究与产品销售场景专题

按需读取。持续企业研究与产品专题共用档案、版本、队列及六个工具；工具仅在研究功能开启后可见。它们与 submit_assessment 正式评估、ask_company 单次同步追问相互独立，不能混用 ID。

## 先读已有成果，再决定是否研究

1. 法定主体未明确时先 get_company_profile；同名、集团或子公司候选须选定。创建/继续/刷新研究依赖服务端已核实且有效的画像；RESEARCH_IDENTITY_REQUIRED 时重新核验，不改名或拼接主体绕过检查。
2. 用 `get_company_research({credit_code})` 或 `{dossier_id}` 读取已有成果，两项标识互斥；可加真实 version_id 固定版本。没有档案或版本不等于企业无机会。
3. 该读取默认只返回档案最新一个版本，product_keys 是本版范围，不是全档案七产品汇总。所需产品未出现时，用 `list_company_research_versions({dossier_id,offset,limit})` 找到覆盖它的最近版本，再带 version_id 回读；跟随 next_offset，limit 上限 50，找到本次需要的版本即可停止。
4. 用户要求只读或只用现有资料时，到此整理结论和缺口。明确要求新研究、补缺口或更新时再创建任务，不因读取返回错误就自动开展付费研究。

## 模式、产品与版本

| 意图 | start_company_research 必要输入 |
| --- | --- |
| 没有成果，首次研究 | mode:"initial"、legal_name、credit_code、operation_id；products、goal、template_id 可选。专题首次研究必须显式 products。 |
| 沿共享档案补缺口、扩产品或切换模板 | mode:"continue"、dossier_id、base_version_id、operation_id；按需 products、goal、template_id。 |
| 检查已有材料时效、更新变化 | mode:"refresh"、dossier_id、base_version_id、operation_id；按需 products、goal、template_id。refresh 是按检查计划更新，不保证重抓所有来源。 |

base_version_id 必须是**档案全局最新版本**。例如最新 V9 研究 CST、最近 Creo 成果为 V8：继续 Creo 时仍传 V9 作基线并显式 products:["creo"]，服务端继承 Creo 的 V8 资料。不要把产品历史版本 V8 直接作为写基线。

通用模板为 company_research；不指定 template_id 的继续/刷新会继承最新模板，不保证回到通用模板。切换模板必须显式 products。通用首次研究省略 products 默认七产品；继续/刷新省略时沿用最新版本范围，因此已知用户只要某产品时始终显式传它。

产品键：Creo→creo，Windchill→windchill，费根堡 QMS→feigenbaum_qms，CATIA→catia，Abaqus→abaqus，CST→cst，SolidWorks→solidworks。围绕七产品及其替代软件，不把竞品当成新的产品键。

## 指定产品专题

使用原 start_company_research，指定 template_id:"product_sales_scenario"。无档案用 initial，已有成果用 continue；需要重核旧资料时用 refresh。不要寻找不存在的 start_product_sales_scenario 工具，也不自动提交正式七产品评估。

例如围绕 Creo 生成结构化探索；示例中的档案、版本和 operation_id 在实际调用前替换为本次真实值：

```json
{
  "mode": "continue",
  "dossier_id": "returned-dossier-id",
  "base_version_id": "returned-latest-version-id",
  "operation_id": "unique-operation-id",
  "products": [
    "creo"
  ],
  "template_id": "product_sales_scenario",
  "goal": "核实Creo机械设计场景与现有软件，探索新购、替换和补充路径"
}
```

完成后通过 get_company_research 读取 template_result.products：场景、软件、阻碍的 claim 引用，以及 new_purchase/replacement/complement 三类路径。state 为 worth_exploring、insufficient 或 contradicted；按结果解释值得验证、依据不足或存在反证，不改写为采购阶段、成交概率或我方产品更优。

近期公共场景可以支持待验证探索，同时 claim 仍是 historical；保留该限定。只有招聘、竞品名称、个人技能或供应商使用，不能证明企业当前部署，也不足以证明需要替换。路径依据变化、无法核验、过期或冲突时保留降级和缺口。

## 状态、证据与恢复

- get_company_research_status 只接受 run_id。queued/running 是处理中；completed/partial 后用返回的 version_id 和 dossier_id 回读成果。partial 仍可有有效事实，要按 coverage、gaps、source_status 解释处理范围与资料局限。
- get_company_research_evidence 接受 version_id，可选 claim_id **或** product，不能同时传两项。分页 offset 默认 0、limit 默认 10/上限 20，跟随 next_offset。只展开关键结论所需证据和依赖，引用固定版本、原文与日期。
- get/list/status/evidence 均只读，不触发模型、来源重查或新版本。已有历史结果不因重读自动变新；新研究也不覆盖旧版本。
- RESEARCH_ALREADY_RUNNING 返回 run_id 时跟踪共享任务，不换 operation_id 重复创建；RESEARCH_ALREADY_EXISTS 时读取已有档案。RESEARCH_VERSION_CONFLICT 时读最新版本重新核对；若仍需继续，按更新后的完整参数建立新 operation_id。
- 失败或取消保留已有成果；无任何版本的空档案不能用 continue。用户明确重试首次研究时仍用 initial 和新 operation_id；原样重放旧 ID 只会返回旧任务。队列/用户上限等待后查询，不循环提交。RESEARCH_VERSION_UNSUPPORTED 时说明不兼容，不自行修改模板或存储绕过校验。
- 用户要求取消时用 cancel_company_research({run_id})，说明取消共享研究会影响依赖它的团队工作；没有明确取消请求不替用户取消。持续研究不是后台订阅，新增定时任务需用户另行提出。

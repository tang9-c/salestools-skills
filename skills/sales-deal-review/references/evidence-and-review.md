# 证据与报告

先查看实际覆盖，再给出业务判断。销售转述和单方填写的阶段需要交叉核对，买方确认以能定位的原话或明确行为支持。将 `evidence.provenance` 为 `ai_review` 的内容视为历史复盘。引用旧 AI 复盘时沿其引用找原始记录。仅有旧复盘结论时注明为既有判断。CRM 备注无法核实作者或来历时，只作为线索。各维度的核验重点、证据强度、趋势和阶段准出参考见[核验框架](frameworks.md)。

## 输入门槛

形成判断前先看覆盖。出现以下情况时，先告诉用户覆盖缺口和可补充的材料，再按「证据不足」给出有限结论，不硬做健康判断：

- 详情或跟进来源为 `denied`、`unavailable`，或窗口内大部分时间不可读；
- 窗口内只有 CRM 字段，没有任何沟通记录、备注或文件；
- 用户提供的文件无法读取或读取范围不明。

缺少记录不等于没有推进，也不等于零延期。

## 报告五部分

1. **健康度总览**。写明客户、商机、金额及币种、阶段、预计成交日、覆盖缺口和预测可信度。
   - 健康度采用绿、黄、红或证据不足。MEDDPICC 状态不换算成 CRM 赢率。
   - 推进势头采用加速、平稳、停滞或未知。依据 `closingDateDelays`、阶段停留、窗口内实质互动和覆盖情况；覆盖不完整时用未知。覆盖充分时可用 14 天无实质推进作为停滞提示。
   - 阶段对齐写出 CRM 阶段、证据支持的阶段、理由和未满足的准出条件。
2. **八维证据表**。每维包含状态、证据强度、趋势、引用和缺口。
   - 状态用 `supported`、`uncertain`、`missing`、`negative` 分别表示有证据、待核实、缺失、明确不利。
   - 强度和趋势按[核验框架](frameworks.md)判断，趋势要写明比较依据。
   - 并列矛盾证据。早先已经确认、本次只是没有新证据时，写「沿用既有确认」，不要标成缺失。
   - 无事实证据时采用证据不足，少数维度有依据时仍须解释整体风险。
3. **核心红旗**。最多三项，按影响排序。每项写成「风险 → 影响 → 观察信号 → 缓解」。重点查单线联系、报价阶段未接触经济决策人、谈判阶段采购流程空白、竞品领先和成交日多次推迟。阶段含义以组织确认为准。
4. **辅导问题**。给 4–5 个用于一对一的可核实问题，同时作为下次拜访准备。
   - 至少一个问合同采购流程、一个问竞争、一个针对最弱维度。
   - 追问谁负责、什么时候完成、买方如何确认。
   - 需要向客户确认的问题标明对象，例如采购负责人或经济决策人。
5. **两周行动**。给三个具体动作，每个写明负责人、期限、交付物和对应缺口，至少一个针对最弱维度。建议行动供经理执行。

最弱维度指状态为 `negative` 或 `missing` 的维度；没有时取强度最低的 `uncertain` 维度。

## 客户端结构

在客户端组织报告，结构如下。断言统一使用 `text`、`kind`、`evidenceIds`：事实用 `fact` 且至少一个有效证据 ID；推断用 `inference` 并引用推断基础；问题与行动使用 `question` 和 `action`，可按需要引用证据。

```json
{
  "overview": {
    "health": "green | yellow | red | insufficient",
    "momentum": "accelerating | steady | stalled | unknown",
    "stageAlignment": {"crmStage": "", "supportedStage": "", "unmetCriteria": [""]},
    "claims": [{"text": "", "kind": "fact", "evidenceIds": [""]}]
  },
  "dimensions": [{
    "key": "M | E | DC | DP | P | I | CH | CO",
    "status": "supported | uncertain | missing | negative",
    "strength": "strong | medium | weak | none",
    "trend": "strengthening | stable | weakening | unknown",
    "claims": [], "gaps": [""]
  }],
  "risks": [{"text": "", "kind": "", "evidenceIds": [], "impact": "", "watchFor": "", "mitigation": ""}],
  "coaching": [{"text": "", "kind": "question", "evidenceIds": [], "audience": ""}],
  "actions": [{"claim": {"text": "", "kind": "action", "evidenceIds": []},
               "owner": "", "dueDate": "YYYY-MM-DD", "deliverable": "", "gap": "M"}]
}
```

八个维度各出现一次。`actions[].gap` 填对应维度的 `key`。`audience` 可省略。交付前按[质量自检](quality-check.md)检查。准备 CRM 回写时，`noteClaims` 仍只提交简短判断和 CRM 证据 ID，不提交以上完整结构。

用户提供多个报告时，只使用当前可见的证据。相同业务判断增加来源只表示证据补充。阶段、金额、赢率或成交日的变化需要对照前后记录及时间。

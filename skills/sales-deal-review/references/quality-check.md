# 质量自检

报告交付前在客户端静默自检。发现问题就修正后再展示，不向用户输出自检结果或质量分。用户要求说明判断依据时，再解释对应条目。

宿主能运行脚本时，把报告和本复盘有效证据 ID 交给 `python3 <skill目录>/scripts/check_report.py`，输入 `{"report": {...}, "evidenceIds": ["..."]}`，可走 stdin 或用 `--file`。脚本只检查结构和可机械判断的规则，返回 `ok` 与 `errors[].code`。语义判断仍按下表由宿主完成。脚本不可运行时按下表人工检查，不声称已执行脚本。

| # | 条目 | 检查内容 | 脚本错误码 |
| --- | --- | --- | --- |
| 1 | 可追溯 | 每个 `fact` 至少有一个本复盘有效证据 ID。`strong` 维度至少引用两条不同证据。「似乎、可能、大概、估计、也许、或许」等措辞只出现在 `inference` 中。引用的原话在证据中确实存在。 | `FACT_WITHOUT_EVIDENCE`、`UNKNOWN_EVIDENCE_ID`、`STRENGTH_UNSUPPORTED`、`HEDGE_IN_FACT` |
| 2 | 全覆盖 | 八个维度各出现一次，不出现「待定」「TBD」「N/A」作为结论。 | `DIMENSION_COVERAGE`、`PLACEHOLDER_TEXT` |
| 3 | 防伪缺口 | 历史复盘或较早记录已由买方证据确认的事项，不能因本次窗口没有新证据而标为缺失或列为缺口。 | 人工 |
| 4 | 强评级有据 | 健康度为绿时，至少五个维度为 `supported` 且强度不低于 `medium`，E 与 CH 不是 `missing` 或 `negative`，阶段准出没有未满足条件。没有任何事实证据时健康度为证据不足。 | `HEALTH_UNSUPPORTED` |
| 5 | 内部一致 | 状态与强度对应：`missing` 对应 `none`，其他状态不用 `none`。红旗、势头与健康度不互相矛盾；覆盖不足时不判绿；只有销售转述时不判绿。 | `STRENGTH_STATUS_MISMATCH`；其余人工 |
| 6 | 行动可执行 | 红旗不超过三项且写明影响、观察信号和缓解；辅导问题 4–5 个；三个行动都写明负责人、有效日期、交付物和对应维度，至少一个针对最弱维度。 | `RISK_LIMIT`、`RISK_INCOMPLETE`、`COACHING_COUNT`、`ACTION_COUNT`、`ACTION_INCOMPLETE`、`WEAKEST_NOT_ADDRESSED` |
| 7 | 阶段对齐 | 写出 CRM 阶段、证据支持的阶段、理由和未满足的准出条件。 | `STAGE_ALIGNMENT_MISSING`；理由人工 |
| 8 | 篇幅 | 每条断言、影响、观察信号、缓解和交付物不超过 80 字。展示时按[展示格式](evidence-and-review.md#展示格式)：事实不重复，维度写中文名，缺失维度合并为一行，红旗每项一行，没有规范外段落和哈希。 | `TEXT_TOO_LONG`；展示人工 |

结构或枚举不符合[客户端结构](evidence-and-review.md#客户端结构)时，脚本返回 `REPORT_INVALID` 并指出路径。

常见问题及修正方式见[正反例](examples.md)。

# 产品参考

路线图按「产品 × 商机类型 × 当前决策环节」生成。厂商资料和公开案例用于确认产品能覆盖的工作流程。下文的岗位、阻碍和比较对象是据此整理的访谈线索。用本商机的纪要、招标要求或客户确认核实后，再写入路线图；对外邮件只使用本次双方谈到的内容。

## 商机类型

| 类型 | 本轮重点 |
| --- | --- |
| 新购 | 确认业务痛点和验证方式，找到能拍板的人。 |
| 替换 | 确认现用软件的具体不满、数据迁移和切换窗口；维持现状是首要竞争对手。 |
| 扩容 | 确认新增用户或模块的使用需求清单和预算归属，以现有使用情况为依据。 |
| 试点 | 确认样件、环境、通过标准和谁认可结果；试点开始前定好通过后的下一步。 |
| 续费 | 确认使用率、未用功能和续费审批人；提前处理降配或流失风险。 |

## 决策环节

需求确认 → 技术验证 → 方案与报价 → 商务与采购 → 签约。当前环节按买方最近的实际行动判断，不按 CRM 阶段字段。

| 环节 | 通用目标承诺 |
| --- | --- |
| 需求确认 | 买方说清问题和目标，并引荐下一位参与者。 |
| 技术验证 | 买方提供样件、数据或环境，并确认通过标准和认可人。 |
| 方案与报价 | 买方确认范围、数量和评审节点。 |
| 商务与采购 | 买方说明采购、法务和付款流程的负责人和周期。 |
| 签约 | 买方确认签约日期和签字人。 |

## 按产品

### Creo

- **场景与角色**　系列产品改型、大装配和关联出图。先找机械设计负责人或产品平台负责人确认变型规则，请 CAD 管理员和主设选样，图纸接收方核对变更是否传到下游。涉及 Creo 与 Windchill 工作区时，再请 PDM 管理员。 [Girbau 案例](https://www.ptc.com/en/case-studies/girbau-engineering-transformation-creo-windchill)
- **阻碍与比较对象**　先分清旧模型只需参照、要继续编辑，还是必须保留可维护的参数关系。问骨架/族表、工程图关联、历史定制和供应商文件版本是否影响迁移。维持 Pro/ENGINEER 或现有 Creo 版本是升级基线；客户允许换型时，可拿 NX 或 SOLIDWORKS 跑同一变型任务。多 CAD 引用、原生编辑和历史特征迁移分别验收。 [Renold 迁移案例](https://www.ptc.com/en/case-studies/renold-transforms-global-collaboration-with-ptc-solutions) · [Creo Unite 文档](https://support.ptc.com/help/creo/creo_pma/r13/usascii/data_exchange/creo_unite/About_PTC_Creo_Unite.html) · [NX CAD](https://www.siemens.com/en-us/technology/nx-cad/)
- **验证与邮件请求**　请设计负责人选一次实际改型，提供装配、关键零件和关联图纸，约定检查模型重建、图纸更新和交接结果。报价前确认需要替换、保留或新增的岗位与模块。

### CATIA

- **场景与角色**　主机厂协同交付、车身与复杂曲面或模具设计。先找项目交付负责人拿客户数据规范，再请曲面或结构设计师选样、主机厂数据接口人确认验收；涉及 CATIA V5 与 3DEXPERIENCE 并存时请 CAD/PLM 管理员。 [Şahince Otomotiv 案例](https://www.3ds.com/insights/customer-stories/sahince-otomotiv-metal-deep-drawing) · [CATIA 数据交换文档](https://3dswym.3dexperience.3ds.com/wiki/catia-user-community/data-exchange-between-catia-v5-and-3dexperience_FB7NO1rhSjqWYcbBueD14A)
- **阻碍与比较对象**　先问接收方是否指定版本、原生文件、装配引用与可编辑性，再问曲面连续性、客户模板及检验规则。沿用 V5、切换 3DEXPERIENCE CATIA、采用 NX 都可能是不同项目的比较基线。接收方允许中性格式时，可评估 STEP 交付并检查返改及丢失的信息。 [达索迁移说明](https://www.3ds.com/support/documentation/resource-library/migrating-dec/catia-v5-3dexperience-powerby-r2026x-using-edat) · [西门子 CAD 互操作](https://www.siemens.com/en-us/products/designcenter/cad-software/cad-interoperability/)
- **验证与邮件请求**　请交付负责人提供脱敏交付规范和一个曾被退回或需要返改的样件，并确认由谁检查交换后的曲面、装配及属性。报价前按项目确认需要的角色和工作环境。

### SolidWorks

- **场景与角色**　非标设备、包装线、大装配和钣金出图。先找机械设计主管和装配主设，拉工艺或车间接图人员核对图纸、BOM 及展开件，旧库由 PDM 管理员核对引用与版本。 [Schur Automation 案例](https://www.solidworks.com/customer-story/schur-automation-engineers-smarter-packaging-lines/)
- **阻碍与比较对象**　查大装配性能、标准件库和配置、工程图及 BOM 联动、钣金展开件交付、共享盘或旧 PDM 的文件引用。用现有 DWG/Excel 流程做基线；对方若评估 Autodesk Inventor，用同一套装配改型检查图纸、BOM 和外部模型引用。软件包、PDM 和实施范围分别核对。 [Inventor AnyCAD 文档](https://help.autodesk.com/cloudhelp/2025/ENU/Inventor-Help/files/GUID-7FACB50F-ED00-419D-8C23-F98283CCD8F8.htm)
- **验证与邮件请求**　请主管选一套近期改过的设备装配，明确干涉检查、工程图与 BOM 的验收人；涉及钣金时加一份实际车间接收的展开件。

### Windchill

- **场景与角色**　从 CAD 与图文档受控延伸到工程变更、eBOM/mBOM 及发放。找管理层发起人确认范围，由研发变更负责人和工艺/BOM 负责人讲清交接，生产核对生效版本，IT 与 ERP/MES 负责人确认接口。 [Girbau 案例](https://www.ptc.com/en/case-studies/girbau-engineering-transformation-creo-windchill) · [Polaris 案例](https://www.ptc.com/en/case-studies/polaris-drives-digital-transformation)
- **阻碍与比较对象**　查物料编码归属、历史版本与审批迁移、变更生效与回传失败处置。只管图文档时比较现有 PDM；做跨部门 BOM 与变更时可比较 Teamcenter，或沿用 PDM 加 ERP 审批。先核对哪套系统拥有 BOM 和发布状态，避免只对比功能清单。 [PTC Windchill 产品说明](https://www.ptc.com/en/products/windchill) · [PTC 公布的 LS Industrial Systems 选型案例](https://www.ptc.com/en/case-studies/ls-industrial-systems)
- **验证与邮件请求**　请研发、工艺、生产及接口负责人用一张脱敏变更单，走查从设计版本、工艺 BOM 到生产收件的全过程。报价前确认首期工厂、迁移对象、接口及验收责任。

### 费根堡 QMS

先找质量总监或工厂质量经理，确认首期要解决哪条质量流程，及由谁对指标负责。业务负责人带实际单据，信息化负责人确认接口。在协创数据公开案例中，来料流程涉及收货任务、PLM 图纸与检验规范，制程流程涉及扫码、审批与生产 BOM。这些交接点可直接用来设计访谈。 [费根堡协创数据案例](https://www.feigenbaum.ai/resource/successfulcase/digital-transformation-of-sharetronic-quality/)

| 业务切入点 | 优先找谁 | 阻碍与验证材料 |
| --- | --- | --- |
| 供应商质量与来料检验（IQC） | 供应商质量工程师（SQE）、IQC 主管、仓储收货和 ERP 负责人。供应商考评或整改涉及采购时再拉采购。 | 用同一物料的一批收货记录走查物料编码、供应商批次、抽样规则、图纸版本、验收判定与 ERP 过账。现场确认来料不合格品如何隔离、如何通知供应商、谁有权放行。 |
| 制程质量与统计过程控制（SPC） | 制程质量工程师（PQE）、巡检员或班组长、工艺及 MES/量测设备负责人。 | 选一条线和一个关键尺寸，用历史测量序列检查采集频率、规格与控制限、告警派单、处置和复验。先确认量具与工位数据能否对应工单、产品和批次。 |
| 客诉与不合格闭环（8D、CAPA） | 客户质量（CQE）或售后质量负责客诉，生产或 SQE 承接整改，质量负责人验证效果。批次追溯需要 MES/ERP 人员参与。 | 用一单脱敏客诉，从出货批次定位工单和相关来料，再跟踪临时遏制、根因、责任人、期限和有效性验证。核实跨部门任务是否有真实签收，以及原客户模板是否需要保留。 |
| 新品质量策划或体系审核 | 汽车零部件场景找 APQP 项目质量、产品/工艺工程师及负责 PPAP 提交的人；审核场景找体系负责人及整改部门。 | 新品场景选一个料号核对 FMEA、控制计划和 PPAP 证据版本，确认图纸变更后由谁更新。审核场景用一次内审不符合项检查整改证据和关闭权限。 |

模块依据见 [费根堡供应商质量](https://www.feigenbaum.ai/products-list/supplier-quality/)、[制程质量](https://www.feigenbaum.ai/products-list/process-quality/)、[问题管理](https://www.feigenbaum.ai/products-list/car-management/)与[汽车零部件方案](https://www.feigenbaum.ai/solution/solutions-auto-parts-industry/)。

- **比较对象**　单点来料检验，先和现有 ERP 质检比较，例如 SAP S/4HANA QM 的检验批和使用决策。单点制程采集，先走查现有 MES 质检、设备采集与 SPC 报表。跨供应商和客诉整改，再比较 Siemens Opcenter Quality 的供应商投诉流程，或客户现有的 Excel、邮件、OA 审批。按本次范围对比谁负责采集、放行、追溯和整改签核，确认是补充现有系统还是替换相关模块。 [SAP 质量管理功能](https://learning.sap.com/courses/applying-sap-s-4hana-quality-management/identifying-the-sap-s-4hana-quality-management-functions_cfc42f85-b1d7-4858-bd8f-eecec7d90d27) · [Siemens 供应商投诉管理](https://resources.sw.siemens.com/en-US/fact-sheet-automate-supplier-based-complaint-processes/)
- **验证与邮件请求**　按买方当前优先流程选一张单或一批数据。来料可写“能否选最近一批需要复判的物料，请 IQC、仓储和 ERP 负责人一起走查，从收货到判定和过账？”客诉可改为请 CQE 提供一单有重复发生记录的客诉，并邀请整改责任人与验证人。报价前确认上线工厂与模块、主数据归属、接口和首期验收指标。

### Abaqus

- **场景与角色**　材料非线性、接触、大变形或瞬态动力学。找结构仿真负责人和建模工程师定义工况，试验/材料实验室提供曲线与边界，设计负责人确认结果如何用于设计决定。遇到批量求解再请 HPC 或 CAE 许可管理员。 [HCL Abaqus 案例](https://3dswym.3dexperience.3ds.com/post/simulia-community/customer-story-hcl-technologies_4t3FOSJnQ5y8CCY6EkIM7w)
- **阻碍与比较对象**　核实材料曲线、接触与加载边界、网格敏感性、收敛和计算耗时；已有脚本或材料子程序时，把复用工时计入评估。常规静力可先比现有 Ansys Mechanical，冲击或碰撞等显式场景可比 LS-DYNA。约定同样输入、结果判定与算力口径，实测偏差和求解耗时分别比较。 [Ansys Mechanical](https://ansys.synopsys.com/products/structures/ansys-mechanical) · [Ansys LS-DYNA](https://ansys.synopsys.com/products/structures/ansys-ls-dyna)
- **验证与邮件请求**　请仿真和试验双方选一套已有试验的典型工况，确认材料输入、载荷边界、对比曲线或失效判据及允许偏差；再按模型规模、并发与求解方式确认配置。

### CST

- **场景与角色**　天线与射频器件、整机 EMC、高速互连。天线案例先找天线/RF 工程师与测试负责人；整机 EMC 拉硬件、结构与实验室；高速互连找信号完整性工程师与板级测试人员。 [The Antenna Company 案例](https://www.3ds.com/insights/customer-stories/antenna-company-antenna-design) · [Convergentia 案例](https://www.3ds.com/insights/customer-stories/convergentia)
- **阻碍与比较对象**　先查介电参数、PCB 接地、匹配网络、端口和测量夹具，模型与实物设置有差异时先对齐。射频全波场景可用现有 Ansys HFSS 做同口径比较；如当前依赖打样实测，也记录打样周期与测试基线。比较同频段、同端口参考面下的 S 参数或方向图，再记录运行时间及内存。EMC 场景以客户确认的测试条件和发射指标为准。 [CST 测量与仿真技术资料](https://blog.3ds.com/brands/simulia/cst-lab-improving-design-measurement-simulation/) · [Ansys HFSS](https://ansys.synopsys.com/products/electronics/ansys-hfss)
- **验证与邮件请求**　请射频和测试负责人选一个样件，附频段、指标、同一设置下的测量数据与夹具说明，明确谁核对偏差。报价前确认求解场景、模型规模和并发需求。

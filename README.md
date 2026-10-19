# Salestools Skills

企业研究与客户开发、联系人管理两个 Skill 的公开分发仓库。服务端代码独立维护；安装 Skill 不授予 MCP 服务或企业数据的访问权限。

## 一起安装

使用支持的 Skills CLI，一次选中两个 Skill（不要只安装其中一个）：

```sh
npx skills add tang9-c/salestools-skills \
  --skill salestools-customer-assessment salestools-contact-management
```

选择实际使用的宿主和安装范围。安装后两个目录必须同级；企业研究的脚本会调用联系人管理的共享校验实现。手动安装时下载同一 Release 的完整 ZIP，将 `skills/` 下两个目录一起放到宿主的 Skill 目录，保留 `references/` 与 `scripts/`。

CLI 用法见 [vercel-labs/skills](https://github.com/vercel-labs/skills)。不同宿主支持情况以其实际功能为准；不支持执行脚本的宿主不能声称已执行参数和结果校验。

## 执行依赖与 MCP 连接

校验脚本需要 Python 3.10+ 和 jsonschema 4.x。可在独立环境安装；宿主执行校验时使用该环境的 Python：

```sh
python3 -m venv /path/to/salestools-skill-venv
/path/to/salestools-skill-venv/bin/python -m pip install \
  -r /path/to/installed-skills/salestools-contact-management/scripts/requirements.txt
```

请向管理员申请个人 MCP 地址和 Token，在宿主的 MCP 设置中配置。Token 不写入本仓库、Skill 文档或共享安装包，不共用管理员 Token。工具目录和功能开关以实际连接为准。

## 使用范围

- 企业研究：持续研究、指定产品销售专题、首次拜访准备、单产品企业比较及正式评估。
- 联系人管理：共享库与关系图谱、Zoho/网页发现、资料导入和有证据的维护。
- 两者衔接：执行 request/result/handoff 校验，保留身份、证据归属、历史时间和访问限制。

脚本只检查输入和返回，不自行发送网络请求或重试写入。来源引文和个人经历不能直接证明企业部署软件或存在采购意向。

## 版本与更新

两个 Skill 始终一起发布和更新。Release 提供完整 ZIP 与 SHA-256 校验文件；`distribution.json` 记录来源提交和每个发布文件的 SHA-256。更新时重复上述安装并选中两个 Skill，或替换为同一 Release 的两个完整目录，不混用版本。

当前分发内容可公开阅读，不包含服务端实现、凭据、真实联系人或客户研究结果。公开可读不等于授予额外开源许可；未经另行许可，不授权转售或再许可。

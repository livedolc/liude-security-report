# 留德安全汇报

这是一个用于每日归档“留德安全汇报”页面的公开开源项目。

数据来源页面格式：

```text
https://dolc.biz/security/sh_YYYYMMDD.html
```

例如 `2026-05-31` 对应：

```text
https://dolc.biz/security/sh_20260531.html
```

## 自动更新

仓库包含 GitHub Actions 工作流，会在每天欧洲/柏林时间早上自动运行：

- 生成当天 URL
- 下载当天 HTML
- 保存到 `reports/sh_YYYYMMDD.html`
- 更新 `index.html`
- 如有变化，自动提交到仓库

也可以手动触发工作流。

## 本地运行

```bash
python3 scripts/update_report.py
```

指定日期：

```bash
python3 scripts/update_report.py --date 2026-05-31
```

只生成索引，不下载新页面：

```bash
python3 scripts/update_report.py --index-only
```

## AI 自动处理

如果你后续要让 AI 对页面内容做摘要、分类或风险评级，建议把 AI 处理逻辑接到 `scripts/update_report.py` 下载完成之后，再把生成的 Markdown 或 JSON 一起提交。

为了避免把密钥写入公开仓库，API Key 应放在 GitHub Actions Secrets 中，例如：

```text
OPENAI_API_KEY
```

## 开源许可

代码部分使用 MIT License。第三方网页内容的版权和使用条件归原网站所有。

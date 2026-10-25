# LDAI_DotImgEngineAgentSkill

`ld-dotimgengine-online` 是以中文为主的角色立绘、参考图编辑、风格与光影渲染、多视图和 PNG 交付技能。以一份明确的当前参考和用户认可记录控制迭代，减少改图时脸部、服装和配件被重新设计的问题。

当前版本：**0.3.0**。技能入口：[SKILL.md](skills/ld-dotimgengine-online/SKILL.md)。在原有保真生图与 3D 资产局部修复基础上，增加扁平图透明分层及重组。外观、分层技术检查、绑定和运行时验证分别验收。

## 使用

将完整的 `skills/ld-dotimgengine-online/` 目录交给支持本地技能的 Agent 宿主，按该宿主的安装方式接入；只复制 `SKILL.md` 会丢失模板和脚本。仓库发布不等于本机已安装，也不会自动更新其他宿主。

示例请求：

```text
使用 ld-dotimgengine-online。以我最后认可的完整正面为主参考，只改变指定视角和光影；先列明当前参考、冻结项和三个组件的角色自身左右位置。保留原始正面，逐张检查并交付独立 PNG。
```

需要一个已授权、能实际接收参考图的图像生成或编辑服务。技能不绑定供应商，不携带模型、密钥、角色原图或自动调用付费服务的权限。PNG 辅助脚本使用 Python 3.10+ 和现有的 Pillow；缺少依赖时报告，不自行安装。

## 内容

- [创作与多视图流程](skills/ld-dotimgengine-online/references/workflow.md)：参考优先级、冻结区域、已获用户接受的方法。
- [公开工具编排](skills/ld-dotimgengine-online/references/toolchain.md)：读取像素、显式传图、异步等待、保存与附件交付。
- [提示词模板](skills/ld-dotimgengine-online/references/prompt-templates.md)与[参考清单模板](skills/ld-dotimgengine-online/references/reference-manifest.template.json)。
- [验收与脚本示例](skills/ld-dotimgengine-online/references/acceptance.md)、[失败案例](skills/ld-dotimgengine-online/references/failure-cases.md)、[迭代约定](skills/ld-dotimgengine-online/references/iteration.md)。

- [3D 修复与参考核对](skills/ld-dotimgengine-online/references/3d-repair-workflow.md)：参考作用范围、贴图与几何分诊、融合曲面与服装层次、局部保护、重导验收及绑定测试边界。

- [透明分层与重组](skills/ld-dotimgengine-online/references/transparent-layer-workflow.md)：共同画布、原像素与隐藏区域重建、多地标校准、透明边缘、RGBA 检查及按遮挡层序复合。

## 验证

在仓库根目录运行：

```sh
python -B -m unittest discover -s tests -v
python -B tools/check_package.py
python -B skills/ld-dotimgengine-online/scripts/png_tools.py --help
python -B skills/ld-dotimgengine-online/scripts/rgba_layers.py --help
```

测试在临时目录生成几何图形，覆盖尺寸/哈希、原生尺寸保护区域差异、保护像素合成、错误输入和不覆盖已有文件。仓库不包含角色资产。脚本测试不能证明生成器的视觉保真度，最终仍须逐张目视验收。

当前方法曾得到用户的视觉接受；生成器仍可能改变眼睛内部或胸饰细节。没有真实 3D 网格时，输出称为 **3D 风格二维图像**；提示词无法保证像素不变，4096 长边重采样也不是原生 4K 生成。

验证记录见 [VALIDATION.md](VALIDATION.md)。维护见 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CHANGELOG.md](CHANGELOG.md)。版权及许可状态见 [COPYRIGHT.md](COPYRIGHT.md)；本仓库尚未选定法律许可证。

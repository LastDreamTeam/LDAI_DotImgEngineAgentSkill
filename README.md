# LDAI_Dot3DBuildAgentSkill

从角色立绘做到可编辑的 3D 模型，也可以只交付一组参考图，或只修已认可模型的一处问题。当前技能是 [`ld-dot3dbuild-online` 1.1.0](skills/ld-dot3dbuild-online/SKILL.md)，仓库网址沿用旧名 DotImgEngine。

| 手头有什么 | 下一步做什么 | 怎样算完成 |
| --- | --- | --- |
| 一张角色立绘 | [准备建模参考图](skills/ld-dot3dbuild-online/references/meshy-character-views.md) | 保留一张非写实正侧背三视图和四张独立的写实材质感 3D 风格正／左／右／背视图，核对非对称细节的朝向 |
| 一个形状或材质不对的模型 | [恢复认可版本](skills/ld-dot3dbuild-online/references/accepted-baseline-recovery.md)，再[局部修复](skills/ld-dot3dbuild-online/references/3d-repair-workflow.md) | 同机位复查修正部位，同时检查须保留的外形 |
| 已完成的角色或配饰 | [试穿与动作复查](skills/ld-dot3dbuild-online/references/repair-skinning-and-wearables.md)，再[导出交付](skills/ld-dot3dbuild-online/references/delivery-and-playback-evidence.md) | 新进程能重新打开或导入交付文件，动作效果能由实际录屏复查 |

静态道具可跳过绑骨。各阶段的输入、退出条件与失败后的处理见[完整工作流](skills/ld-dot3dbuild-online/SKILL.md)。

## 安装和迁移

将完整 skills/ld-dot3dbuild-online 目录按 Agent 宿主的技能安装方式接入，不只复制 SKILL.md。原 skills/ld-dotimgengine-online 保留为旧版兼容快照，新工作使用 ld-dot3dbuild-online。仓库URL目前仍沿用旧名；技能显示名已改为 LDAI_Dot3DBuildAgentSkill。

这份技能不授予额外工具、账户、预算或发布权限，不自动安装依赖或操作用户项目。静态资产无需强制绑骨；已有认可模型仅修改受影响区域。

## English — choose a starting point

Use the [current skill](skills/ld-dot3dbuild-online/SKILL.md) to prepare consistent character views, repair an existing model, or deliver editable 3D files and playback evidence. Install the whole `skills/ld-dot3dbuild-online` directory. For a model you already like, start with [baseline recovery](skills/ld-dot3dbuild-online/references/accepted-baseline-recovery.md) and record which parts to preserve.

## 验证

从仓库根目录运行两项检查。

```sh
python -B -m unittest discover -s tests -v
python -B tools/check_package.py
```

保留原图像与透明分层脚本接口。测试使用合成图片，不证明视觉、蒙皮或游戏实装通过。新增3D流程已做文档场景核对，未在本次维护中重新制作或运行任何真实模型。

完整流程与参考文档见新技能入口；版本记录见 [CHANGELOG.md](CHANGELOG.md)，验证边界见 [VALIDATION.md](VALIDATION.md)，维护见 [CONTRIBUTING.md](CONTRIBUTING.md)。版权和许可仍按 [COPYRIGHT.md](COPYRIGHT.md)，不新增法律许可。


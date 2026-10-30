# LDAI_Dot3DBuildAgentSkill

当前版本 **1.0.1**，新技能入口 [ld-dot3dbuild-online](skills/ld-dot3dbuild-online/SKILL.md)。

从立绘、参考图和四视图，经 AI 或程序化建模、几何材质修复、按需绑骨与配饰试穿、动作回归，直到可编辑源、导出、真实录屏和持久交付。每阶段明确输入、出口检查和失败回退，不把生图与修模分成孤立任务。

## 安装和迁移

将完整 skills/ld-dot3dbuild-online 目录按 Agent 宿主的技能安装方式接入，不只复制 SKILL.md。原 skills/ld-dotimgengine-online 保留为旧版兼容快照，新工作使用 ld-dot3dbuild-online。仓库URL目前仍沿用旧名；技能显示名已改为 LDAI_Dot3DBuildAgentSkill。

这份技能不授予额外工具、账户、预算或发布权限，不自动安装依赖或操作用户项目。静态资产无需强制绑骨；已有认可模型仅修改受影响区域。

## 验证

python -B -m unittest discover -s tests -v

python -B tools/check_package.py

保留原图像与透明分层脚本接口。测试使用合成图片，不证明视觉、蒙皮或游戏实装通过。新增3D流程已做文档场景核对，未在本次维护中重新制作或运行任何真实模型。

完整流程与参考文档见新技能入口；版本记录见 [CHANGELOG.md](CHANGELOG.md)，验证边界见 [VALIDATION.md](VALIDATION.md)，维护见 [CONTRIBUTING.md](CONTRIBUTING.md)。版权和许可仍按 [COPYRIGHT.md](COPYRIGHT.md)，不新增法律许可。

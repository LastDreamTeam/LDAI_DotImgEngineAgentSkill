# 验收与 PNG 辅助脚本

## 每张图的人工检查

- 当前参考正确，角色身份和已认可脸未被通用风格替换；看全图，也在原生尺寸看脸。
- 逐项对照脸型、眼睛圆度、睫毛、虹膜、瞳孔、高光、眉毛；胸饰形状和细线不能只看缩略图。
- 轮廓、比例、姿态、人物高度和头脚完整；案例要求的苗条比例、白膝紧身衣覆盖都还在。
- 服装侧背结构与主正面相容，无新装甲或符号；配件分解区已有纳入。
- 三个组件逐件对照角色自身左右/前后、锚点、线缆和可见性；合理遮挡有记录，没有穿透或简单镜像。
- 材质、主光、投影和 AO 连贯，正面确有体积感；边缘无多边形切块、背景漏色、条带和羽化晕圈。
- 原始正面和生成原输出未覆盖；每个视图为可完整解码的独立 PNG。
- 交付明确实际原生尺寸、衍生处理、剩余漂移和认可状态。助手认为通过不等于用户认可。

## 依赖与命令

从完整技能目录运行以下命令；需要已存在的 Python 3.10+ 和 Pillow。缺依赖时报告，不安装。示例文件名均为占位；先复制 JSON 模板到私有工作区并填入真实信息，不能把模板的示例认可状态当成事实。

```sh
# 完整解码、PNG 格式、尺寸、模式、透明通道与 ICC 摘要；记录文件 SHA-256
python -B scripts/png_tools.py inspect private/front-original.png

# 可选：断言真实尺寸与已记录文件哈希（替换为实际数值）
python -B scripts/png_tools.py inspect private/front-original.png --expect-size 1024 1536

# 白色=保护原像素；必须是同尺寸、不含灰阶的 L 模式二值 PNG 蒙版
python -B scripts/png_tools.py compare private/front-original.png private/candidate.png --mask private/protect.png

# 白色区域确定性取原图，其他区域取候选，另存新文件
python -B scripts/png_tools.py composite private/front-original.png private/candidate.png private/protect.png private/composited-r002.png
python -B scripts/png_tools.py compare private/front-original.png private/composited-r002.png --mask private/protect.png
```

`inspect --expect-sha256` 接受完整的 64 位 SHA-256。命令输出 JSON，检查通过退出 0；格式、尺寸、哈希、保护像素不符合或写入冲突退出 2，缺依赖退出 3。`compare` 默认逐通道零容差，白色蒙版选中的每个 RGBA 像素都必须相等；`--tolerance N` 仅用于用户明确同意的容差检查，不能据此宣称像素严格一致。未传蒙版时比较整图；空保护蒙版拒绝通过，避免零像素“验证”。

脚本拒绝不对齐尺寸，不自动裁切/缩放，不覆盖任何已有输出（包括源图）。合成示例是**二值像素选择**，没有阴影生成、边界配准或柔和羽化能力。候选必须先在相同原生坐标下对齐。先用扩大保护范围覆盖重要边缘，再把光影过渡安排在可改区域内，查看接缝；保留了区域像素不代表视觉无接缝。

## 数值结果的边界

文件哈希相同可证明文件字节相同；重新编码 PNG 的文件哈希可能不同但解码像素相同。`compare` 比较解码后的 8 位 RGB/RGBA（RGB 按不透明 RGBA 解释），不会对 ICC 做颜色转换；严格外观比较还要核对模式、色彩配置和显示条件。脚本拒绝调色板、灰阶或高位深的图像比较/合成，避免静默降低精度；`inspect` 可报告这些 PNG 的信息。

跨视角、不同尺寸或不同坐标的脸不能直接用此脚本证明一致。不要先把两图缩小到同尺寸再声称保护通过。真正硬像素冻结与该区域的光影变化不能同时成立；明确哪些区域只冻结设计，哪些区域冻结像素。

如果上采样至 4096 长边，交付说明写“原生 X×Y，重采样交付 A×B”，不能写原生 4K。没有实际网格、材质和摄像机，就不能写真实同模型多角度渲染。图像模型的“正交”提示也不证明数学正交。

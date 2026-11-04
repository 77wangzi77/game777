# Blender 场景管线约定

> 用户确认（2026-11-03）：**场景用 Blender 构建**  
> 本机：`C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`  
> 对齐：四层封闭关 · `四层空间流线与灯光制作清单.md`

## 单位与轴向

| 项 | 约定 |
|----|------|
| 单位 | 1 Blender 单位 = 1 米 |
| 导出 Unity | FBX；Scale 1；Forward -Z；Up Y（按 Unity 导入预设再验） |
| 命名 | 与清单一致：`ENV_L0x_*` / `PROP_L0x_*` / `LIT_L0x_*` / `AN_*` |

## 目录

```
/workspace/VRgame/blender/
  scripts/          # 生成/更新灰模的 Python
  blockout/         # .blend 灰模（同步到本机可开）
```

本机工作副本：`VRgame_blender/`（由场景岗推送）

## 里程碑

- S0：`VRgame_L01_L04_Blockout.blend` 四层灰模 + 锚点空物体
- S1+：按层拆分细化，仍保持 Collection 名与 ENV 前缀一致

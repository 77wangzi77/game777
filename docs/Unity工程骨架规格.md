# Unity 工程骨架规格（程序员岗 · 草案）

> 范围：PCVR · Unity · 古剑奇谭风格剧情关卡  
> 状态：文档就绪；**待 GitHub 空库 URL 后落仓**  
> 汇报：→ VRgame·制作统筹

## 1. 目标

空库到手后可一次性初始化：可编译的 Unity 工程 + OpenXR/XRI 最小交互 + 关卡加载入口，供策划/场景/UI 按约定目录投递资产。

## 2. 建议工程目录（仓库根）

```
VRgame/
  README.md
  .gitignore                 # Unity 官方模板 + Library/Temp/Obj/Builds
  ProjectSettings/
  Packages/manifest.json
  Assets/
    _Project/
      Scripts/
        Core/                # 启动、场景加载、GameState
        XR/                  # 输入绑定、传送/抓取封装
        Level/               # 关卡逻辑、触发器、任务节点钩子
        UI/                  # 世界空间 UI 桥接（视觉由 UI 美术出）
      Scenes/
        Boot.unity           # XR Rig 入口
        Level_01.unity       # Vertical slice 占位
      Prefabs/
        XR/
        Interactables/
        Level/
      ScriptableObjects/     # 关卡配置、对话/任务表引用
      Art/                   # 场景组投递（只读约定，不改他人规范）
      UI/                    # UI 美术投递
    ThirdParty/              # 第三方插件（只增不改核心）
  Builds/                    # 本地构建输出（gitignore）
  Docs/                      # 可选：从 /workspace/VRgame/docs 镜像关键说明
```

## 3. 包与 XR（与 docs/技术选型.md 对齐）

| 项 | 选择 | 说明 |
|----|------|------|
| 渲染 | URP（建议） | PCVR 画质可控；待首包验证 |
| XR | OpenXR Plugin | 跨头显 |
| 交互 | XR Interaction Toolkit | 抓取 / 射线 / 传送 |
| 输入 | 手柄优先 | Action-based；手势二期 |
| 最低档（待补） | GPU/头显名单 | 制作统筹或用户拍板后写入 |

`Packages/manifest.json` 初始化时钉死一套已验证版本号（落仓时写入，避免飘版）。

## 4. 启动与关卡逻辑最小集

1. **Boot**：生成/复用 XR Origin，加载输入 Action Map，进 `Level_01`
2. **LevelGate**：触发器进入 → 抛事件（供策划任务流挂接）
3. **Interactable 约定**：抓取 / 使用 / 对话点 三类 Prefab 槽位
4. **移动**：传送为主 + 有限滑步（舒适度见玩法一页纸）
5. **构建**：Windows 独立玩家 + OpenXR；首包只保证 Editor Play 与 PCVR 冒烟

## 5. 程序员岗近期产出顺序（不设死线）

| 序 | 产出 | 依赖 |
|----|------|------|
| A | 本规格 + 技术风险表 | 无 |
| B | 空库 README / .gitignore / 目录占位 | **GitHub URL** |
| C | Boot + XR Origin + 传送样例场景 | B |
| D | LevelGate + 三类 Interactable 槽 | C；策划给验收一句 |
| E | 构建脚本与已知问题清单 | C |

## 6. 硬边界

- 只服务 `/workspace/VRgame` 与用户指定的本项目 GitHub 仓
- 不跨写其他已立项项目；重大改派先问用户

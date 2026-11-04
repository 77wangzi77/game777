# VRgame · 对话与分支逻辑流程图（首版）

> 风格：古剑奇谭气质 · PCVR 世界锚对话框 + 射线选选项  
> 对应界面：UI-02 对话框 / UI-03 分支选项

## 主流程

```mermaid
flowchart TD
  A[进入关卡 / 触发对话点] --> B{是否有前置任务条件?}
  B -->|否| C[打开对话框 UI-02]
  B -->|是且未满足| D[短提示：条件未达成]
  D --> Z[关闭提示 · 继续探索]
  B -->|是且已满足| C

  C --> E[显示角色名 + 正文]
  E --> F{本节点类型}
  F -->|纯旁白/独白| G[扳机 / 继续]
  G --> H{还有下一句?}
  H -->|是| E
  H -->|否| I[关闭对话框]
  I --> J[推进关卡状态 / 解锁交互]

  F -->|NPC 对话无选项| G
  F -->|分支选择| K[展开选项列表 UI-03<br/>2–3 项]
  K --> L[手柄射线悬停高亮]
  L --> M[扳机确认选项]
  M --> N{选项结果}
  N -->|推进主线| E
  N -->|进入支线节点| E
  N -->|结束对话| I
  N -->|触发解谜/轻战斗| O[关对话 · 切玩法节点]
  O --> P[玩法完成回调]
  P --> E

  J --> Q{关卡目标完成?}
  Q -->|否| R[探索 / 下一对话点]
  R --> A
  Q -->|是| S[过场或下一关入口]
```

## 单句对话状态机（给程序）

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Opening: 触发对话
  Opening --> ShowingLine: 淡入完成
  ShowingLine --> WaitingContinue: 打字结束或瞬时全文
  WaitingContinue --> ShowingLine: 继续且有下一句
  WaitingContinue --> ShowingChoices: 本句后需选项
  WaitingContinue --> Closing: 对话结束
  ShowingChoices --> Resolving: 确认选项
  Resolving --> ShowingLine: 跳转新节点
  Resolving --> Closing: 选项结束对话
  Closing --> Idle: 淡出完成
```

## 文案与 UI 约束（跟流程图绑定）

| 项 | 建议上限 |
|----|----------|
| 单句正文 | ≤ 40 字（VR 可读） |
| 选项条数 | 2–3 |
| 单选项文案 | ≤ 12 字 |
| 角色名 | ≤ 6 字 |

## 文件

本图：`/workspace/VRgame/docs/UI对话分支流程图.md`

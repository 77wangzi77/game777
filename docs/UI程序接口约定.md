# UI ↔ 程序接口约定（试玩冲刺）

> 来源：Unity3D程序 2026-11-03 · 状态 draft

## 世界空间

- Canvas 挂点：`AN_Look_UI_*`
- 观看距离：约 **1.2–1.8 m**
- 字数上限：等策划对话表

## 事件名（UI 需响应 / 触发视觉）

| 事件 | UI 侧用途 |
|------|-----------|
| `Arrive` | 到达点提示／短标刷新 |
| `Anomaly.Bell` | 异常铃提示 |
| `Dialogue.NodeReached` | 开对话框／选项 |
| `Item.Inspected` | 检视／证据 UI |
| `Npc.MuteTrust` | 哑巴信任相关提示 |
| `Level.WatchDrum` | 观鼓节点标题／提示 |
| `Level.Outro` | 关末／结算过渡 |

## 任务总表相关

程序已更新：`T015` / `T021` / `T031` / `T044`（见 `docs/计划/四周任务总表.csv`，若已落盘）。

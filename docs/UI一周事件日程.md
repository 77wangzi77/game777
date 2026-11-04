# UI · 一周试玩 · 事件安排明细

> 游戏：无悔之剑／《残简三声》驿站 VS · 世界锚 `AN_Look_UI_*` · 1.2–1.8m  
> 字数：主句≤48 · 选项≤16×≤3（策划 D3 冻结）

## 事件 → UI 行为（程序 EventBus）

| 事件 | 触发时机（试玩） | UI 显示 | 关闭条件 | 挂点 |
|------|------------------|---------|----------|------|
| `Arrive` | 玩家传送进区／到任务点 | 任务短标刷新一句；可选短提示「已到达」≤1.5s | 自动淡出或下一 Arrive 覆盖 | 腕托或 `AN_Look_UI_task` |
| `Anomaly.Bell` | 异常铃响 | 短提示「铃声」+ 可选方向弱标 | 2s 或玩家看向来源 | `AN_Look_UI_hint` |
| `Dialogue.NodeReached` | 对话节点到达 | 开对话框（角色名+主句）；若有枝开 2–3 选项 | 继续打完／选项确认／关节点 | `AN_Look_UI_dlg_*` |
| `Item.Inspected` | 检视线索／证据 | 证据检视框（名+简述）；可收进证据栏 ICON | 扳机确认或移开 | `AN_Look_UI_item` 或跟物 |
| `Npc.MuteTrust` | 哑巴信任变化 | 短状态提示（信任↑／↓） | 1.5–2s | 腕托短标 |
| `Level.WatchDrum` | 观鼓节点 | 标题条「观鼓」+ 任务短标 | 节点结束 | `AN_Look_UI_title` |
| `Level.Outro` | 关末 | 黑场／标题条 → 结算 ST 文案位（策划文案） | 确认或超时进菜单 | 世界锚全宽弱面板 |

另（菜单／存档，程序菜单事件）：

| 交互 | UI |
|------|-----|
| 开主菜单 | 四键：进入游戏／保存／选项／退出游戏 |
| 进入游戏 | YES/NO 确认 → YES 加载图 → 进场景；NO 退出 |
| 保存成功 | 非阻断「已保存」提示 |
| 选项 | 舒适度：字号／距离／利手／坐姿 |

## 日表（事件相关交付）

| 日 | UI 产出 | 对接事件 |
|----|---------|----------|
| D1 | 主菜单+YES/NO+加载图位 | 菜单／进入 |
| D2 | 对话框+选项线框挂 `AN_Look_UI_dlg_*` | `Dialogue.NodeReached` |
| D3 | 证据检视框+交互提示 ICON | `Item.Inspected`／提示类 |
| D4 | 任务短标（腕托）+暂停舒适度+存档提示 | `Arrive`／存档 |
| D5 | 接线：上表事件全部可显隐 | 全表冒烟 |
| D6 | ICON/IMG 分类落盘、命名进总表 draft | — |
| D7 | 头显可读性走查；修遮挡／字号 | QA |

## 不做

完整战斗 HUD、技能栏精装、LLM 字幕特效、四层关 UI。

## 对齐主表（2026-11-03）

以 `docs/计划/一周试玩_事件安排明细.md` 为准。UI 增订：

| 事件 | UI |
|------|-----|
| `Dialogue.ChoicePicked` | **UI Publish**（选项确认） |
| `Quest.Advanced` | 任务短标更新 |
| `Evidence.Gained` | 证据入手短提示 |
| `Save.Requested`/`Save.Done` | 「已保存」 |
| `Combat.SkipAvailable` | 可跳过按钮（若有） |
| `Threat.Resolve` | 唬退成败文案占位 |

锚点优先：`AN_Look_UI_dialogue` / `menu` / `choice`（场景日表）；与 `AN_Look_UI_dlg_*` 同义时跟总表 redirects。

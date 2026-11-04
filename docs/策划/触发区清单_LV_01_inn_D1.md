# 触发区清单 · `LV_01_inn`（D1 锁版）

> 关卡：驿站夜《残简三声》七块灰模  
> 版本：2026-11-03（Asia/Shanghai）· D1 末交场景，供 **D5–D6** 挂名/自测  
> 命名锁：空间 id = `ENV_Inn_*`（**勿** `ENV_L01_*` / `ENV_01_*`）  
> 事件源：`docs/计划/一周试玩_事件安排明细.md` §2–§4

| 空间 id | 中文 | 关键 AN_*（埋点名） | 触发事件 | 任务/证据锚 | D5–D6 场景动作 |
|---------|------|---------------------|----------|-------------|----------------|
| `ENV_Inn_Porch` | 外廊 | `AN_Teleport_spawn` · `AN_Look_UI_menu` · `AN_Look_UI_dialogue` · `AN_Trigger_bell` | `Arrive` · `Anomaly.Bell` · 入关旁白 | QM0 | 风铃 PROP；入关传送落点可见；菜单锚 |
| `ENV_Inn_Hall` | 堂 | `AN_Look_host` · `AN_Look_guest` · `AN_Look_UI_dialogue` · `AN_Look_UI_choice` · `AN_Teleport_hall` | `Dialogue.*`（掌柜/旅客）· 对质 · `Level.WatchDrum`→抉择 | QM1 / QM3 / QM4 | 双对话锚；选项 UI 锚；堂中传送 |
| `ENV_Inn_Wing` | 侧廊 | `AN_Teleport_wing` · `AN_Trigger_prop_redherring` · `AN_Trigger_prop_mud` | `Item.Inspected`（红鲱鱼/泥印等） | QE* 辅 | 线索 PROP 半遮挡；碰撞可及 |
| `ENV_Inn_Upper` | 上房（可锁） | `AN_Teleport_upper` · `AN_Trigger_prop_scrap` · `AN_Look_lock` | `Item.Inspected` → QE3 | QE3 | 残页 PROP；锁盒占位（钥匙来自灶房） |
| `ENV_Inn_Yard` | 后院 | `AN_Teleport_yard` · `AN_Trigger_prop_box` | `Item.Inspected` / 解谜一次 → QE4 | QE4 | 伪匣 PROP；解谜交互一次即可 |
| `ENV_Inn_Kitchen` | 灶房 | `AN_Teleport_kitchen` · `AN_Look_mute` · `AN_Trigger_prop_note` | `Npc.MuteTrust` · 字条 → QE5 | QC_m / QE5 | 哑仆锚；字条/钥匙 PROP |
| `ENV_Inn_Bamboo` | 竹林口 | `AN_Teleport_exit` · `AN_Trigger_outro` | `Level.Outro(flag)` | QM5 | 离关壳；OutroTrigger 体积；expose 走动可通 |

## 挂名约定（场景 D5–D6）

1. 空物体 / Collection 名 = 上表 **空间 id** 或 **AN_*** 全名（与总表 draft 一致）。  
2. 体积触发用 `AN_Trigger_*`；UI 世界锚用 `AN_Look_UI_*`（高度约 1.2–1.8 m）。  
3. 传送落点一律 `AN_Teleport_*` 且灰模可见圆盘（D4 抛光）。  
4. 旧名 `ENV_L01_*` / `ENV_01_*` → 读 `docs/资源/redirects.csv`，Blender 侧直接改成 `ENV_Inn_*`。  
5. D6 交付：`LV_01_inn_blockout_D6.fbx` + AN 坐标 CSV；expose 路径自测可走。

## 最小事件冒烟（跟程序对表）

| # | 玩家动作 | 期望 Publish |
|---|----------|--------------|
| 1 | 落 `AN_Teleport_spawn` | `Arrive(ENV_Inn_Porch)` |
| 2 | 触风铃 | `Anomaly.Bell` |
| 3 | 进堂交互圈 | `Quest.Advanced(QM0→QM1)` 可开 `DLG_01_host` |
| 4 | 检视残页/匣/字条 | `Item.Inspected` → QE3/4/5 |
| 5 | 到竹林口 | `Level.Outro(flag)` |

路径：`/workspace/VRgame/docs/策划/触发区清单_LV_01_inn_D1.md`

# VRgame 可配置表骨架

> 岗位：数值策划 · 目录：`docs/数值/config/`  
> 版本：v1-skeleton · 平台：PCVR · Unity  
> 范围：只写本项目 `/workspace/VRgame/`

## 1. 表清单

| 文件 | 表名 | 内容 | 示例行数 |
|------|------|------|----------|
| `combat_numeric.json` | 战斗数值 | 玩家成长、武器、技能数值、敌方预算、关卡经济、TTK 模型、GP/SP/MP、伤害公式 | 玩家档×3 + 武器×1 + 技能数值×3 + 敌×3 + 经济×1 |
| `character.json` | 角色表 | 玩家/NPC/敌人引用角色档案 | 5 |
| `skill.json` | 技能表 | 技能表现+权威数值键（SK_*） | 5 |
| `level.json` | 关卡表 | VS + L1–L4（高山/石桥/岩浆/洞府） | 5 |
| `ui_art.json` | UI美术表 | 界面 ID / 资源键 / 舒适度档 | 5 |
| `prop.json` | 物件表 | 场景/交互道具 PROP_* | 5 |

## 2. 通用约定

每张表顶层含：

- `schema`：`VRgame.Config.<Name>`
- `version`：当前 `v1-skeleton`
- `_meta`：字段说明、前后端归属、`sourceOfTruth`、ID 风格

行数据：多数表用 `rows[]`；`combat_numeric` 沿用 v1 分区字段（`playerBaseByLevel` / `enemyBudget` 等），便于直接对齐导入。

### ID 风格（与策划一致）

| 前缀 | 用途 | 例 |
|------|------|----|
| `CHAR_` | 角色 | `CHAR_swordsman` |
| `WPN_` | 武器 | `WPN_shuangyue_wuhen` |
| `SK_` | 技能 | `SK_slash` |
| `DMG_` | 伤害公式 | `DMG_melee_light` |
| `N_` / `E_` / `B_` | 杂兵/精英/Boss | `N_bandit`, `B_host` |
| `LV_` | 关卡 | `LV_inn_night`, `LV_L01_mountain` |
| `ENV_` | 环境块（关卡引用，不进 prop 主键） | `ENV_L01_Mountain` |
| `PROP_` | 物件 | `PROP_TeleportPad` |
| `UI-##` / `UI_` | 界面 ID / 资源键 | `UI-02`, `UI_DialogBox` |
| `LIT_` | 灯光预设 | `LIT_L01_Mountain_SkyCold` |
| `SP_` | 出生点 | `SP_birth` |
| `V_` / `F_` | 胜/负条件 | `V_BOSS`, `F_DEAD` |

## 3. 前后端归属

| 表 | 前端（客户端导入/表现） | 后端（权威结算/推算） |
|----|-------------------------|------------------------|
| combat_numeric | 成长、武器白字、技能 mul/CD 展示、公式、GP/SP/MP 规则、balanceTargets | `ttkModel`、`enemyBudget`、`levelEconomy`、与前端同构的权威战斗值 |
| character | 显示名、立绘键、技能装载、动画集 | characterId、enemyRef、成长引用 |
| skill | 名称、动画/VFX/SFX、UI 图标绑定、轨迹表现 | costs/CD/charge、damage 公式与倍率、判定体 |
| level | 显示名、环境根、灯光、出生表现、物件列表 | 限时、胜负、重生、任务/Boss、经济引用 |
| ui_art | **仅前端**：资源键、锚点、舒适度档、色板 | — |
| prop | Prefab、LOD、交互类型、关卡标签 | 交互 flag、线索/任务旗（若有） |

冲突规则：

1. 技能 **mp/cd/mul/hitCount** 以 `combat_numeric.skillNumeric` 为准（对齐 `数值配置_*_v1.json`）。
2. 敌方 HP/ATK/TTK 以 `combat_numeric.enemyBudget` 为准。
3. 关卡经济以 `combat_numeric.levelEconomy` 为准；`level.json` 用 `economyRef` 挂接。
4. 完整技能表现树仍可从 `docs/策划/战斗技能配置_示例.json` 展开；本 `skill.json` 为可配置主表骨架。

## 4. 与现有 v1 关系

| 现有文件 | 关系 |
|----------|------|
| `docs/数值/数值配置_前端_v1.json` | combat_numeric 前端字段的完整源；骨架为可配置子集+示例 |
| `docs/数值/数值配置_后端_v1.json` | combat_numeric 后端/TTK/权威预算完整源 |
| `docs/数值/数值平衡_v1.md` | ARPG 锚与 TTK 说明；`balanceTargets` 摘要自该文 |
| `docs/策划/数值配置_表示例.json` | v0 底表；已被 v1 取代，config 不再依赖 |
| `docs/策划/战斗技能配置_示例.json` | skill 行内容来源 |
| `docs/策划/关卡设计.md` / `剧情关卡结构_VS.md` | level 胜负与 VS 行 |
| `docs/关卡概念/四关场景模型清单.md` | L1–L4 与 prop 命名 |
| `docs/UI界面清单_首版.md` / `UI舒适度规范.md` | ui_art 行 |

演进建议：程序导入优先读 `config/*.json`；数值调参仍可回写完整 `数值配置_*_v1.json`，再同步进 `combat_numeric.json`。

## 5. 关卡索引（level.json）

| levelId | 名 | 层 |
|---------|----|----|
| `LV_inn_night` | 残简三声（VS） | 0 |
| `LV_L01_mountain` | 高山 | 1 |
| `LV_L02_bridge` | 石桥 | 2 |
| `LV_L03_magma` | 岩浆 | 3 |
| `LV_L04_grotto` | 洞府 | 4 |

## 6. 修订

| 日期（Asia/Shanghai） | 变更 |
|----------------------|------|
| 2026-11-03 | 首版可配置表骨架落盘（六表 + 本说明） |

# NPC 技能与动作动画（关卡概念原画单位）

> 范围：仅关卡概念已出原画的战斗单位（鬼怪 / 半甲鬼怪 / 牛头怪 / 蛇形大BOSS）  
> 对话 NPC（掌柜 / 旅客 / 哑仆）**不进**本表战斗技能  
> 对接：`NPC_鬼怪_移动影子说明.md`、`战斗系统.md`、`战斗技能配置结构.md`、`战斗_NPC与BOSS.md`、`剧情动画设计.md`、`命名规范.md`  
> 叙事：秦朝山海经 · 勇士斩妖；鬼怪≈怨影/猙影附体杂兵；牛头≈关卡节点精英；蛇形≈章 Boss（化蛇/巴蛇意象可换皮）  
> 状态：草案 · 数值 value 待数值岗填；种子 id 总表均为 **draft**

---

## 1. 范围与 id 对照

| id | cn_name | 层级 | 原画 | 叙事对齐 | 备注 |
|----|---------|------|------|----------|------|
| `N_ghost` | 鬼怪 | 杂兵 | `NPC_鬼怪_*` + 移动影子说明 | 怨影 / 猙影附体 | **对应旧 `N_shade`** → redirects |
| `N_ghost_armor` | 半甲鬼怪 | 杂兵变体 | `NPC_鬼怪_半甲_*` | 蒙狰残甲附影 | 略硬、略慢 |
| `E_minotaur` | 牛头怪 | 精英 | `NPC_牛头怪_*` | 关卡门卫 / 节点预习 | 大斧+链 |
| `B_serpent` | 蛇形大BOSS | 章 Boss | `大BOSS_蛇形怪物_*` | 化蛇或巴蛇舞台 | **新 id**；默认可挂章2–3换皮；与 `B_bamboo`/`B_shrine` 并列，不互相覆盖 |

不在本表：`DLG_01_host` / `DLG_01_guest` 等对话单位。

---

## 2. 单位卡片

### 2.1 `N_ghost` 鬼怪

| 项 | 约定 |
|----|------|
| 定位 | 教「影子预警 + 扑杀闪避」的近战杂兵；怕安魂/光类钩（与旧怨影一致） |
| 体态 | 半透明漂浮女形；下摆雾化无实脚；利爪；冷青灰 |
| 血量档 | 相对玩家 Lv1：**中**（锚点约旧怨影 55 HP 量级，数值填） |
| 仇恨距离 | Alert **8m**；脱战 leash **14m** |
| 移动 | 滑翔三段：起浮 → 前倾滑行 → 扑击前倾；**平滑位移，忌瞬闪** |
| 影子 | 地面实影；滞后身体 **0.1–0.2s**；扑击时影拉长（ShadowStretch） |
| 层光 | L01/L02 冷光拉长影；L03 底光影上爬壁；L04 暖侧影短而浓 |
| VR 舒适 | **不贴脸冲**；最短停扑距 ≥1.2m；影子=可读预兆 |

### 2.2 `N_ghost_armor` 半甲鬼怪

| 项 | 约定 |
|----|------|
| 定位 | 同族变体；教「硬壳破绽」；可与裸影混编 |
| 体态 | 半甲金边 / 破甲残片；漂浮同族 |
| 血量档 | 相对 Lv1：**中高**（约 N_ghost ×1.35）；防减略高 |
| 仇恨距离 | 同鬼怪 8m / 14m |
| 差异 | 扑杀前摇 +0.05–0.1s；爪伤略低、有一次「甲片格挡反应」 |
| VR 舒适 | 同不贴脸；甲片反光可作额外预警 |

### 2.3 `E_minotaur` 牛头怪

| 项 | 约定 |
|----|------|
| 定位 | 精英节点；预习「抬腿冲撞 / 大开合斧线」 |
| 体态 | 牛首人身、断角或全角、半甲破旧、双足蹄铁、巨斧、胸链 |
| 血量档 | 相对章推荐 Lv：**精英档**（约玩家同级 HP×3–4） |
| 仇恨距离 | Alert **12m**；leash **20m** |
| VR 舒适 | 冲撞给 **侧向传送逃点**；斧扫禁止贴脸 180° 甩头；可读前摇 ≥0.35s |

### 2.4 `B_serpent` 蛇形大BOSS

| 项 | 约定 |
|----|------|
| 定位 | 章高潮 Boss；盘绕舞台控制 + 昂首咬 + 甩尾 AOE |
| 体态 | 无角大蛇；红鬣；金腹甲；洞窟/岩浆底光可同调 |
| 挂章建议 | **默认章2–3 可换皮**（章2≈化蛇竹/石；章3≈岩浆/祠下）；章4巴蛇可用同骨架换材质。与 `B_bamboo`（接骨人）/`B_shrine`（祠下无名）**身份不同**，勿直接改名覆盖 |
| 血量档 | 相对章推荐 Lv：**Boss 档**（约 280–360 量级，数值填） |
| 阶段 | Intro → P1 → 阈值Cut → P2（可选 P3）→ Finisher |
| 仇恨 | 舞台全场；脱战回巢盘绕点 |
| VR 舒适 | 甩尾/盘压 **预警 ≥0.35s**；AOE 必给 `AN_Teleport_*` 逃点；禁强制连续旋转；转阶段可坐姿看 |

---

## 3. 动作动画清单（AnimClip 建议名）

命名风格：`ANIM_{unit}_{action}`；参数用 Animator float/bool。

### 3.1 鬼怪族（`N_ghost` / `N_ghost_armor` 共用套，半甲可复用 + `_armor` 覆盖）

| Clip / Param | 用途 | 备注 |
|--------------|------|------|
| `ANIM_ghost_idle` | 待机漂浮 | 下摆雾循环 |
| `ANIM_ghost_alert` | 警觉 | 头微抬、影收紧 |
| `ANIM_ghost_move_rise` | 移动段1 起浮 | 三段滑翔① |
| `ANIM_ghost_move_glide` | 移动段2 前倾滑行 | ② |
| `ANIM_ghost_move_lunge` | 移动段3 / 扑击衔接 | ③；接攻击 |
| `ANIM_ghost_atk_claw` | 爪击 | 单段 |
| `ANIM_ghost_atk_claw2` | 双爪连 | 段间可格挡点 |
| `ANIM_ghost_atk_pounce` | 扑杀 | **必开 ShadowStretch** |
| `ANIM_ghost_hit` | 受击 | 硬直 0.35–0.5s |
| `ANIM_ghost_stun` | 破绽/体力空 | |
| `ANIM_ghost_death` | 死亡 | 绿灰散尽；可接 KO |
| `ANIM_ghost_intro` | 入场 | 影落墙→实体（BI 用） |
| **Param `ShadowLag`** | float 0.1–0.2 | 影跟随延迟秒 |
| **Param `ShadowStretch`** | float 1–2.2 | 扑击时影纵向拉伸倍率 |
| `ANIM_ghost_armor_block` | 仅半甲 | 甲片格挡反应 |

### 3.2 牛头怪 `E_minotaur`

| Clip | 用途 | 备注 |
|------|------|------|
| `ANIM_mino_idle` | 待机 | 斧拄地或扛肩 |
| `ANIM_mino_alert` | 警觉 | 蹄顿、鼻息 |
| `ANIM_mino_move` | 走近 | 重步；可三态 blend |
| `ANIM_mino_atk_axe_h` | 横斩 | 大开合 |
| `ANIM_mino_atk_axe_v` | 砸劈 | |
| `ANIM_mino_charge_windup` | **冲撞预备抬腿** | 必播 ≥0.4s |
| `ANIM_mino_charge_loop` | 冲刺中 | |
| `ANIM_mino_charge_end` | 冲撞结束/撞墙 | |
| `ANIM_mino_atk_chain` | 链扫/掷链 | |
| `ANIM_mino_hit` / `_stun` / `_death` | 受击/硬直/死 | |
| `ANIM_mino_intro` | BI 入场 | 蹄踏石桥/门 |

### 3.3 蛇形 `B_serpent`

| Clip | 用途 | 备注 |
|------|------|------|
| `ANIM_serpent_idle_coil` | **盘绕**待机 | |
| `ANIM_serpent_alert_rise` | **昂首**警觉 | |
| `ANIM_serpent_move_slither` | 游走换位 | 平滑，忌瞬移 |
| `ANIM_serpent_atk_bite` | 咬击 | 昂首前摇 |
| `ANIM_serpent_atk_tail` | **甩尾** | **预警 ≥0.35s**（尾颤+地光） |
| `ANIM_serpent_atk_coil_crush` | 盘压 | selfAoE |
| `ANIM_serpent_atk_spit` | 毒涎抛射 | parabola |
| `ANIM_serpent_atk_wave` | 躯体 Sin 横扫 | sin |
| `ANIM_serpent_hit` / `_stun` / `_death` | | 死亡可接 KO |
| `ANIM_serpent_intro` | BI | 盘出石缝/岩浆 |
| `ANIM_serpent_phase` | 转阶段 | 不可伤 |

---

## 4. 攻击方式表

### 4.1 `N_ghost`

| 招式 | skillId | shape | 前摇 / 生效 / 后摇 (s) | 可读预兆 | 伤害档 | 可格挡 | 可闪 | 破绽窗 |
|------|---------|-------|------------------------|----------|--------|--------|------|--------|
| 利爪 | `SK_ghost_claw` | meleeBox | 0.25 / 0.12 / 0.35 | 袖展+影前探 | 低 | ✓ | ✓ | 后摇 0.35 |
| 双爪 | `SK_ghost_claw2` | meleeBox | 0.2 / 0.1×2 / 0.4 | 双臂拉开 | 中低×2 | ✓（段间） | ✓ | 第二段后 0.4 |
| 影扑 | `SK_ghost_pounce` | meleeBox（位移盒） | 0.35 / 0.15 / 0.5 | **影拉长+滞后**；身稍后 | 中 | ✗（建议） | ✓（侧闪） | 落空 0.55 |

### 4.2 `N_ghost_armor`

| 招式 | skillId | shape | 前摇 / 生效 / 后摇 | 可读预兆 | 伤害档 | 可格挡 | 可闪 | 破绽窗 |
|------|---------|-------|--------------------|----------|--------|--------|------|--------|
| 甲爪 | `SK_ghost_armor_claw` | meleeBox | 0.3 / 0.12 / 0.4 | 甲片反光+影 | 低 | ✓ | ✓ | 0.4 |
| 沉扑 | `SK_ghost_armor_pounce` | meleeBox | 0.4 / 0.18 / 0.55 | 影拉长更久 | 中 | ✗ | ✓ | 落空 0.6 |
| 甲振 | `SK_ghost_armor_pulse` | selfAoE | 0.3 / 0.1 / 0.45 | 甲缘金光一闪 | 低（短硬直） | ✗ | ✓ 后撤 | 0.45 |

### 4.3 `E_minotaur`

| 招式 | skillId | shape | 前摇 / 生效 / 后摇 | 可读预兆 | 伤害档 | 可格挡 | 可闪 | 破绽窗 |
|------|---------|-------|--------------------|----------|--------|--------|------|--------|
| 斧横 | `SK_mino_axe_h` | meleeBox / 短 line | 0.4 / 0.15 / 0.5 | 肩沉、斧贴地预摆 | 中高 | ✓（耗 SP 高） | ✓ | 0.5 |
| 斧砸 | `SK_mino_axe_v` | meleeBox | 0.45 / 0.12 / 0.55 | 举斧遮顶 | 高 | △（完美弹反） | ✓ 侧 | 砸地 0.55 |
| 抬腿冲 | `SK_mino_charge` | line | **抬腿 0.4+** / 冲 0.6 / 0.4 | **抬腿+蹄铁火花** | 高 | ✗ | ✓ 传送侧 | 撞停 0.7 |
| 断链扫 | `SK_mino_chain` | sin 或 line | 0.35 / 飞行 / 0.3 | 左手链崩碎 | 中 | ✓ | ✓ | 出手后 0.3 |

### 4.4 `B_serpent`

| 招式 | skillId | shape | 前摇 / 生效 / 后摇 | 可读预兆 | 伤害档 | 可格挡 | 可闪 | 破绽窗 |
|------|---------|-------|--------------------|----------|--------|--------|------|--------|
| 昂咬 | `SK_serpent_bite` | meleeBox / 短 line | 0.4 / 0.15 / 0.45 | 红鬣炸开、瞳亮 | 高 | △ | ✓ | 收颈 0.45 |
| 甩尾 | `SK_serpent_tail` | selfAoE（扇/环） | **≥0.35 尾颤** / 0.2 / 0.5 | 尾尖颤+地面弧光 | 高 | ✗ | ✓ 逃点 | 0.5 |
| 盘压 | `SK_serpent_coil` | selfAoE | 0.5 / 0.3 / 0.6 | 身圈收紧 | 中高+压< | ✗ | ✓ 圈外 | 散开 0.6 |
| 毒涎 | `SK_serpent_spit` | parabola | 0.35 / 落地爆 / 0.4 | 喉囊鼓、锁定点 | 中 | ✗ | ✓ | 吐后 0.4 |
| 波躯 | `SK_serpent_wave` | sin | 0.4 / 轨迹 / 0.35 | 躯体左右预摆 | 中 | △ | ✓ | 波尽 0.35 |

---

## 5. 技能配置草案行

字段对齐 `战斗技能配置结构.md`（敌方：`costs.mp/sp` 默认 0，除非机制需要；value 由数值填）。

| skillId | ownerUnit | skillType | shape | lockType | unbreakable | chargeTime | mp | sp | cooldown | notes |
|---------|-----------|-----------|-------|----------|-------------|------------|----|----|----------|-------|
| SK_ghost_claw | N_ghost | BasicAttack | meleeBox | none | false | 0 | 0 | 0 | 0.8 | 利爪；影前探 |
| SK_ghost_claw2 | N_ghost | ActiveSkill | meleeBox | none | false | 0 | 0 | 0 | 2.5 | 双爪；段间格挡点 |
| SK_ghost_pounce | N_ghost | ActiveSkill | meleeBox | none | false | 0 | 0 | 0 | 4.0 | ShadowStretch；不贴脸收距 |
| SK_ghost_armor_claw | N_ghost_armor | BasicAttack | meleeBox | none | false | 0 | 0 | 0 | 1.0 | 半甲爪 |
| SK_ghost_armor_pounce | N_ghost_armor | ActiveSkill | meleeBox | none | false | 0 | 0 | 0 | 5.0 | 沉扑；前摇更长 |
| SK_ghost_armor_pulse | N_ghost_armor | ActiveSkill | selfAoE | none | false | 0 | 0 | 0 | 6.0 | 甲振短硬直；radius≈1.5m |
| SK_mino_axe_h | E_minotaur | BasicAttack | meleeBox | none | false | 0 | 0 | 0 | 1.2 | 横斩；可挂短 line |
| SK_mino_axe_v | E_minotaur | ActiveSkill | meleeBox | none | false | 0 | 0 | 0 | 3.5 | 砸劈 |
| SK_mino_charge | E_minotaur | ActiveSkill | line | none | false | 0 | 0 | 0 | 8.0 | **抬腿 windup≥0.4**；需逃点 |
| SK_mino_chain | E_minotaur | ActiveSkill | sin | none | false | 0 | 0 | 0 | 7.0 | 链扫；可改 line |
| SK_serpent_bite | B_serpent | BasicAttack | meleeBox | none | false | 0 | 0 | 0 | 2.0 | 昂咬 |
| SK_serpent_tail | B_serpent | ActiveSkill | selfAoE | none | false | 0 | 0 | 0 | 6.0 | 甩尾预警≥0.35s |
| SK_serpent_coil | B_serpent | ActiveSkill | selfAoE | none | false | 0 | 0 | 0 | 10.0 | 盘压；P2+ |
| SK_serpent_spit | B_serpent | ActiveSkill | parabola | single | true | 0 | 0 | 0 | 7.0 | 锁定落点；敌方不耗玩家 MP |
| SK_serpent_wave | B_serpent | ActiveSkill | sin | none | false | 0 | 0 | 0 | 9.0 | 躯波；P2 |

伤害公式建议占位：`DMG_ghost_melee` / `DMG_mino_heavy` / `DMG_serpent_boss`（总表 draft，数值填）。

---

## 6. 遭遇 ENC

| encounterId | 组合 | 舞台建议 | 目的 |
|-------------|------|----------|------|
| `ENC_ghost_1` | N_ghost×2（或 ×1+半甲×0） | L01/L02 冷光廊 | 教影子预警与侧闪 |
| `ENC_ghost_armor_mix` | N_ghost×1 + N_ghost_armor×1 | L02 桥侧 | 混编节奏（可选） |
| `ENC_minotaur_gate` | E_minotaur×1 | L02 石桥门 / 关卡闸 | 精英节点；冲撞逃点 |
| `ENC_serpent_boss` | B_serpent×1 | 章2竹石或章3岩浆窟（换皮） | 章 Boss；多逃点 |

刷怪锚：场景布 `AN_spawn_ghost_*` / `AN_spawn_mino_gate` / `AN_spawn_serpent`（见总表 draft）。

---

## 7. 剧情动画接口（BI / KO）

| 演出 id | 类型 | 触发 | 对接单位 / ENC | 结束后 |
|---------|------|------|----------------|--------|
| `BI_ghost_pack` | BI | 首次鬼怪遭遇体积 | ENC_ghost_1 | AI/伤害盒激活 |
| `KO_ghost` | KO | 击杀指定鬼怪或清波 | N_ghost* | 字幕「除魔·影」可选 |
| `BI_minotaur_gate` | BI | 精英门战 | ENC_minotaur_gate | 可伤帧 |
| `KO_minotaur` | KO | 击杀牛头 | E_minotaur | 开门 / flag |
| `BI_serpent` | BI | Boss 开战 | ENC_serpent_boss | Intro 不可伤→P1 |
| `KO_serpent` | KO | Boss 击杀 | B_serpent | Finisher / 章旗 |

程序：`Cutscene.Play` → `Cutscene.Ended` → 战斗可伤；与 `剧情动画设计.md` 事件表一致。章1 既有 `BI_01_yard` / `KO_01_zheng` 可 **复用演出骨架** 换绑定到 `N_ghost`（redirects/策划备注），不必强删旧 id。

---

## 8. 邻岗分工

| 岗 | 动作 |
|----|------|
| **数值** | 填 HP/攻防/倍率 value；公式行 `DMG_*`；只读 locked id |
| **动画** | 挂上表 AnimClip；鬼怪必调 ShadowLag / ShadowStretch |
| **程序** | SO/JSON 技能行；Hitbox/弹道；`IdRedirect`（含 N_shade→N_ghost）；BI/KO 绑定 |
| **场景** | `AN_spawn_*`、Boss 逃点 `AN_Teleport_*`；层光配合影 |
| **策划** | 总表追加 draft；升 locked 待用户拍板；本文件维护 |

---

## 9. 验收（本批）

1. 鬼怪三段滑翔可见；影滞后 0.1–0.2s；扑杀影拉长且不贴脸  
2. 牛头冲撞必见抬腿 ≥0.4s，且有侧向逃点  
3. 蛇甩尾预警 ≥0.35s；盘压/甩尾有传送点  
4. 四单位技能均可落入 `shape` 枚举；配置字段齐全  
5. 总表 draft 行与 redirects `N_shade→N_ghost` 已登记  

---

## 10. 待确认

- `B_serpent` 首挂 **章2 化蛇** 还是 **章3 岩浆**（默认 2–3 可换皮）  
- 章1 `KO_01_zheng` 是否直接改绑 `N_ghost` 或并存  
- 半甲「甲振」是否保留硬直（舒适度）  

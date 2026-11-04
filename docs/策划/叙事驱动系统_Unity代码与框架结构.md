# 叙事驱动系统 · Unity 代码与框架结构

> 岗位：VRGAME叙事AI · 对接 Unity3D程序员  
> 范围：PCVR · Unity · OpenXR/XRI · L01《残简三声》  
> 对齐：`Unity工程骨架规格.md` · `叙事特异值驱动_技术方案.md` · `叙事驱动系统_框架与实现方案.md` · `任务流.md` · `对话节点.md`  
> 修订：2026-11-03（Asia/Shanghai）  
> 说明：细到可建脚本空壳；不提供完整可编译工程；不写 API Key 明文  
> 汇报 → VRgame Unity程序 / 相关统筹

---

## 0. 文档关系

| 文档 | 角色 |
|------|------|
| `叙事驱动系统_框架与实现方案.md` | 总册：模块、LLM-first、数据表、分期、验收 |
| `叙事特异值驱动_技术方案.md` | 细则：SV 表、模式规则、感知×Affect、节拍 |
| **本文** | Unity 目录树、类/接口/SO、挂接点、模型三路线 |

---

## 1. 框架结构图（ASCII）

```
Boot.unity
  └─ GameSystems (DontDestroy)
       ├─ GameStateStore
       ├─ EventBus
       ├─ NarrativeRuntime
       │    ├─ SpecialValueCollector
       │    ├─ AffectStore
       │    ├─ PerceptionGrader
       │    ├─ ModeEvaluator        # 硬门禁优先
       │    ├─ BehaviorArbiter
       │    ├─ BeatDirector
       │    ├─ PresentationRouter
       │    ├─ NarrativeValidator
       │    └─ ILLMNarrativeClient
       │         ├─ ApiLlmNarrativeClient
       │         ├─ AgentOrchestratorClient
       │         └─ LocalLlmNarrativeClient
       ├─ LlmConfigSO
       └─ SaveService
Level_01
  ├─ LevelGate / Interactables / DialogueTrigger → EventBus
  ├─ XR Origin (XRI) → Feel / See 钩子
  └─ UI 世界空间 → Speak / See 表现
```

数据流（事件驱动，非每帧 LLM）：  
`事件 → Collector → [LLM 建议] → Validator → Affect/Percept → Mode/Behavior → Presentation`

感知状态是 Mode/Behavior 的**一级输入**。

---

## 2. 建议目录树

```
Assets/_Project/Scripts/
  Core/     BootLoader.cs  GameStateStore.cs  EventBus.cs  SaveService.cs  GameStateKeys.cs
  XR/       XrRigFacade.cs  TeleportComfortBridge.cs  HapticsBridge.cs
  Level/    LevelGate.cs  InteractableUse.cs  InteractableGrab.cs  DialogueTrigger.cs
            WatchDrumTimer.cs  OutroTrigger.cs
  UI/       DialoguePanelView.cs  EvidenceToastView.cs  WatchClockView.cs
            ChoicePanelView.cs  FocusLightController.cs  GuideGlowController.cs
  Narrative/
    NarrativeRuntime.cs  SpecialValueCollector.cs  AffectStore.cs  PerceptionGrader.cs
    ModeEvaluator.cs  BehaviorArbiter.cs  BeatDirector.cs  PresentationRouter.cs
    NarrativeValidator.cs  NarrativeEvents.cs
    Models/   SpecialValueId.cs NarrativeMode.cs PerceptionChannel.cs PerceptState.cs
              AffectId.cs LlmRequestModels.cs
    Llm/      ILLMNarrativeClient.cs ApiLlmNarrativeClient.cs AgentOrchestratorClient.cs
              LocalLlmNarrativeClient.cs LlmCallScheduler.cs LlmPromptBuilder.cs
    Data/     NarrativeTableLoader.cs
Assets/_Project/ScriptableObjects/Narrative/
  SpecialValueDef.cs  ModeTransitionRuleSO.cs  AffectDefSO.cs  PerceptRuleSO.cs
  BeatDefSO.cs  NarrativeCopySlotSO.cs  LlmConfigSO.cs  NarrativeLevelConfigSO.cs
```

---

## 3. 核心枚举与模型

```csharp
public enum NarrativeMode { Arrival, CaseBrief, Investigate, Confront, Choice, Outro }
public enum PerceptionChannel { Hear, Speak, See, Taste, Feel }
public enum PerceptQualia {
  Muffled, NormalHear, Sharp,
  Silent, CalmSpeak, Urgent,
  Dim, NormalSee, Focused, Tunnel,
  Flat, NormalTaste, Keen,
  Numb, NeutralFeel, Tense, Pressure
}
public enum AffectId { Score, WinLose, Death, Fear, Joy, Suspect, Trust }
public enum LlmProviderKind { CloudApi, AgentOrchestrator, LocalPrivate }
```

| AffectId | L01 含义 | 禁止误解 |
|----------|----------|----------|
| Score | 线索/证据可信度积分（对齐 evidence_count） | 非战斗得分 HUD |
| WinLose | 对质/抉择态势 -1/0/1 | 非 PvP |
| Death | 叙事死亡压迫（none 坏钩）0–1 | 非血条玩法 |
| Fear/Joy | 节奏与感知 | 不对玩家显式弹出数值 |
| Suspect/Trust | 映射 host_suspect / trust_mute | 不拆原 Critical 键 |

---

## 4. 关键类职责与方法签名

### GameStateStore / EventBus
- Get/Set Flag|Int|String|Float；OnChanged；SnapshotForSave
- Publish/Subscribe/Unsubscribe\<T\>

### NarrativeRuntime
```csharp
void Initialize(NarrativeLevelConfigSO config, ILLMNarrativeClient llm, LlmConfigSO llmCfg);
void OnGameplayEvent(GameplayEvent e); // 唯一入口
NarrativeMode CurrentMode { get; }
PerceptSnapshot CurrentPercept { get; }
bool CanShowExposeOption { get; }
```

单次事件顺序：Collector → 可选 LLM 异步 → Validator → Affect/Percept → ModeEvaluator（硬门禁）→ BehaviorArbiter → PresentationRouter。

### 子系统
```csharp
// SpecialValueCollector
IReadOnlyList<SpecialValueDef> Evaluate(GameplayEvent e, GameStateStore state);
void ApplyWrites(IEnumerable<SpecialValueDef> hits, GameStateStore state);

// AffectStore
float Get(AffectId id);
void ApplyDelta(AffectId id, float delta, string reason);
void RecalcFromEvidence(GameStateStore state);

// PerceptionGrader
PerceptSnapshot Grade(AffectStore affect, GameStateStore state, NarrativeMode mode);

// ModeEvaluator — LLM 不可推翻硬规则
ModeTransition? Evaluate(PerceptSnapshot percept, GameStateStore state, NarrativeMode current, IEnumerable<string> raisedSv);

// BehaviorArbiter
DialogueGateResult RefreshGates(GameStateStore state, NarrativeMode mode);
NpcBehaviorHints ForNpc(string npcId, PerceptSnapshot percept, GameStateStore state);

// NarrativeValidator
bool CanExpose(GameStateStore state); // (QE1∧QE2)∧(QE3∨QE4)∧QE5 ∧ confront_done ∧ !skipped
bool IsAllowedFlag(string flag);
LlmNarrativeResponse Sanitize(LlmNarrativeResponse raw, GameStateStore state);
```

---

## 5. SO / JSON 与类对应

| 数据表 | SO | 主要字段 | 消费者 |
|--------|----|----------|--------|
| SV | SpecialValueDef | id,nameZh,type,source,triggerExpr,writes[],channelPrimary,affectTags[],ttl,consumes | Collector |
| Mode规则 | ModeTransitionRuleSO | ruleId,conditionExpr,toMode,forced,feedbackSlots[] | ModeEvaluator |
| Affect | AffectDefSO | affectId,min,max,defaultValue,persist,note | AffectStore |
| Percept规则 | PerceptRuleSO | whenAffect,channel,toQualia,priority | PerceptionGrader |
| Beat | BeatDefSO | beatId,spaceId,svIds[],modeJump,durationSec | BeatDirector |
| 文案槽 | NarrativeCopySlotSO | slotId,bind,textZh,synesthesia | Presentation/LLM |
| LLM配置 | LlmConfigSO | providerKind,baseUrl,model,timeoutMs,apiKeyEnvVar,enableOnEvent,fallbackToRules,agentSteps[] | Llm层 |
| 关卡包 | NarrativeLevelConfigSO | levelId,表引用 | NarrativeRuntime |

---

## 6. OpenXR/XRI/Level/对话挂接

| 来源 | 组件 | 事件 | 用途 |
|------|------|------|------|
| 入场传送 | LevelGate | Arrive | N1 / SV_bell |
| 风铃 | InteractableUse | Anomaly.Bell | Hear |
| NPC | DialogueTrigger | Dialogue.NodeReached | Critical/Pivot |
| 残页/匣 | InteractableUse | Item.Inspected | QE3/QE4 |
| 哑仆 | Grab+Use | Npc.MuteTrust | trust_mute |
| 更鼓 | WatchDrumTimer | Level.WatchDrum | 强制 Choice / 30s窗 |
| 竹林口 | OutroTrigger | Level.Outro | flag 过场 |
| 震动/舒适 | HapticsBridge / TeleportComfortBridge | 订 PerceptChanged | Feel |
| 对话UI/光 | DialoguePanel / Focus/Guide | 订 Gate/Mode | Speak/See |

对话条件保持：has_QE*、trust_mute、guest_turned、host_suspect。

---

## 7. LLM 调用：时机 / 线程 / 降级

- **事件触发**，禁止每帧。触发例：★句结束、证据入手、矛盾对、更鼓 warn、进 Choice 前。
- `LlmCallScheduler.RequestAsync`：超时默认 1500–2500ms；失败 Publish LlmFailed → fallbackToRules。
- 主线程只应用 Validator 后的结果；网络在异步任务。
- 缓存键：(mode, qmHash, qeMask, lastSv)，短 TTL。

| LLM 可建议 | 本地强制 |
|------------|----------|
| SV 候选、五通道、旁白语气、加压、文案槽 | expose 门、flag 枚举、时限强制 Choice、禁止新结局、存档键 |

---

## 8. 模型接入三路线

### 接口
```csharp
public interface ILLMNarrativeClient {
  LlmProviderKind Kind { get; }
  bool IsAvailable { get; }
  Task<LlmNarrativeResponse> CompleteAsync(LlmNarrativeRequest request, CancellationToken ct);
}
```

| 路线 | 实现类 | 延迟 | 成本 | 隐私 | 离线 |
|------|--------|------|------|------|------|
| 云端 API | ApiLlmNarrativeClient | 中 | 按量 | 摘要出域 | 否 |
| 智能体编排 | AgentOrchestratorClient（多步：抽SV→感知→决策→文案） | 较高 | 较高 | 同API | 视工具 |
| 私有化本地 | LocalLlmNarrativeClient（Ollama/vLLM/llama.cpp 等） | 视硬件 | 电/机 | 高 | 是 |

`LlmConfigSO.apiKeyEnvVar` 只存环境变量名（如 VRGAME_LLM_API_KEY），**禁止**明文进仓库。  
默认：PCVR 原型用 CloudApi + 规则门禁；无网演示 LocalPrivate 或纯规则；量产偏私有化。

工厂：`Initialize` 按 providerKind 创建对应 Client。

---

## 9. JSON Schema（DTO）

### Request v1
```json
{
  "schema": "vrgame.narrative.llm.request.v1",
  "levelId": "L01",
  "mode": "Investigate",
  "beatId": "N4",
  "gameState": {
    "has_QE1": true, "has_QE2": true, "has_QE3": false, "has_QE4": true, "has_QE5": false,
    "host_suspect": 1, "trust_mute": true, "guest_turned": false,
    "chapter1_flag": "", "confront_done": false, "confront_skipped": false
  },
  "affect": { "score": 0.4, "fear": 0.3, "joy": 0.1, "death": 0.0, "winLose": 0, "suspect": 0.4, "trust": 0.5 },
  "percept": { "hear": "NormalHear", "speak": "CalmSpeak", "see": "NormalSee", "taste": "Flat", "feel": "NeutralFeel", "pressure": 1 },
  "raisedSpecialValues": ["SV_contradiction_pair"],
  "lastEvent": { "type": "Dialogue.NodeReached", "npcId": "N_guest", "nodeId": "G1" },
  "allowedModes": ["Investigate", "Confront", "Choice"],
  "allowedFlags": ["chase", "guard", "expose", "none"],
  "copySlotIds": ["NB_contradiction", "UX_evidence"],
  "constraints": ["no_new_ending", "no_combat_score_hud", "expose_requires_validator"]
}
```

### Response v1（必须 Sanitize）
```json
{
  "schema": "vrgame.narrative.llm.response.v1",
  "specialValueCandidates": [{ "id": "SV_contradiction_pair", "confidence": 0.92 }],
  "affectDeltas": [{ "id": "fear", "delta": 0.1 }, { "id": "score", "delta": 0.15 }],
  "perceptSuggest": { "hear": "Sharp", "speak": "Urgent", "see": "Tunnel", "taste": "Keen", "feel": "Tense", "pressure": 2 },
  "modeSuggest": { "to": "Confront", "forced": false, "reason": "contradiction_pair" },
  "behaviorSuggest": { "npcId": "N_host", "style": "guarded", "optionMaxChars": 12 },
  "copySlotPick": ["NB_contradiction"],
  "narrationDraft": "两个人，两个时辰——总有一个在演。"
}
```

---

## 10. 五通道表现落点

| 通道 | 桥接 | 表现 |
|------|------|------|
| Hear | Audio 路由 | 风铃、更鼓、旁白 |
| Speak | DialoguePanelView | 选项长短；★不可跳 |
| See | FocusLight / GuideGlow | 高亮、焦点光；慎用剧烈 FOV |
| Taste | 文案槽 synesthesia=true | 联觉替代（墨腥/酒苦） |
| Feel | Haptics / TeleportComfort | 短震；Fear↑降瞬移刺激 |

---

## 11. 建空壳顺序

1. GameStateKeys + GameStateStore + EventBus  
2. 枚举/DTO + NarrativeValidator.CanExpose  
3. SO 空壳 + L01 NarrativeLevelConfigSO  
4. ModeEvaluator 硬规则（无 LLM）  
5. ILLMNarrativeClient + Api Stub  
6. PerceptionGrader + PresentationRouter  
7. Agent / Local 实现可切换  

---

## 12. 文末

| 项 | 内容 |
|----|------|
| 路径 | `/workspace/VRgame/docs/策划/叙事驱动系统_Unity代码与框架结构.md` |
| 修订 | 2026-11-03 · LLM 三路线 + 类树 |
| 汇报 | → Unity程序 / 相关统筹 |

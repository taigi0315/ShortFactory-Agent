# Multi‑Agent Video Generator — Design & Implementation Plan

*Last updated: Sept 16, 2025*

## 1) Project goals

* Turn a **topic** into a **polished, narrated short video** with images/animation per scene.
* Upgrade current system (heavily relying on `full_script_writer`) into **true autonomous agents** with clear roles, contracts, and validation loops.
* Make outputs **production‑ready**: consistent story voice, rich scene details, grounded facts, valid prompts, and TTS/image parameters.

---

## 2) Agent roster & responsibilities

### A) Full Script Writer (FSW)

**Mission:** Draft the whole story and high‑level pacing. Decide on scene count, type, and macro flags like `needs_animation`, `transition_to_next`, and `scene_importance`.

**Inputs:**

* `topic`
* `length_preference` (e.g., 60–90s)
* `style_profile` (tone, target audience)
* optional `knowledge_refs` (links, citations to ground facts)

**Outputs:** (JSON)

* `title`, `logline`, `overall_style`, `main_character`, `cosplay_instructions`
* `story_summary` (120–180 words)
* `scenes[]`: `scene_number`, `scene_type`, `beats[]`, `needs_animation`, `transition_to_next`, `scene_importance`, `learning_objectives[]`

> FSW **does not** specify low‑level prompts or TTS; it leaves that to Scene Script Writer.

---

### B) Scene Script Writer (SSW)

**Mission:** Take each FSW scene beat and **expand** it into a production‑ready scene package: narration, dialogue, visual storyboard, sound/TTS settings, and **image prompts** with exact specifications.

**Inputs:**

* Single `scene` object from FSW
* `global_context` (characters, style, constraints, glossary)
* `educational_enhancement_guidelines` (hooks, metaphors, objectives)

**Outputs:** (JSON; one per scene)

* `scene_number`
* `narration_script` (spoken lines split into timed chunks with pauses)
* `dialogue[]` (speaker, line, optional on‑screen text)
* `visuals[]` (ordered storyboard frames):

  * `frame_id`, `shot_type` (wide/medium/close), `camera_motion` (pan/tilt/zoom), `character_pose`, `expression`, `background`, `foreground_props`, `lighting`, `color_mood`
  * `image_prompt` (positive), `negative_prompt`, `model_hints` (style keywords), `aspect_ratio`, `seed`, `guidance_scale`
* `tts` (engine, voice, language, `elevenlabs_settings`: stability/similarity/style/speed/loudness)
* `sfx_cues[]` (cue, at\_ms, duration\_ms)
* `on_screen_text[]` (text, at\_ms, duration\_ms, style)
* `timing`: `total_ms`, per‑line timings
* `continuity`: `in_from` (previous transition), `out_to` (next transition), `callback_tags` (for running gags/visual motifs)
* `safety_checks`: results of validators (see §5)

**Behavior:**

* Performs **ELABORATION** (adds hooks, facts, metaphors) without contradicting FSW.
* Normalizes typos and terminology (e.g., "dachshaund" → "dachshund").

---

### C) Image Create Agent (ICA)

**Mission:** Generate or request images that exactly match SSW frames. Returns asset URIs and metadata.

**Inputs:**

* From SSW `visuals[]` including prompts, negative prompts, seeds, style, aspect ratio, and character sheets.

**Outputs:** (JSON)

* `frame_id`
* `image_uri`
* `thumbnail_uri`
* `prompt_used`, `negative_prompt_used`
* `model` (e.g., Stable Diffusion XL, FLUX, Midjourney API), `sampler`, `cfg`, `steps`, `seed`, `safety_result`

**Behavior:**

* **Echoes back** final prompt with resolved variables.
* Performs **prompt sanitation** (no PII/NSFW), and **style lock** (keeps character consistent).

---

### D) Orchestrator / Planner

**Mission:** State machine controlling the pipeline (see §3). Performs retries, validation, and fallbacks.

**Outputs:** Build report: timing, model usage, failures, diffs between requested and produced assets.

---

## 3) System architecture & data flow

```
User Topic → FSW → SSW (for each scene) → ICA (for each frame) → TTS → Video Assembler → QC → Final MP4
```

* **Contracts**: Each handoff uses **strict JSON Schemas** (see §4). The Orchestrator enforces schemas and runs validators before advancing.
* **Idempotency**: Each scene/frame has deterministic `seed` unless randomized explicitly.
* **Caching**: Cache SSW outputs by `(title, scene_number, version)` and ICA assets by `(frame_id, prompt_hash)`.

---

## 4) Data contracts (JSON Schema)

### 4.1 Full Script Writer — `FullScript.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "FullScript",
  "type": "object",
  "required": ["title", "overall_style", "story_summary", "scenes"],
  "properties": {
    "title": {"type": "string", "minLength": 5},
    "logline": {"type": "string"},
    "overall_style": {"type": "string"},
    "main_character": {"type": "string"},
    "cosplay_instructions": {"type": "string"},
    "story_summary": {"type": "string", "minLength": 60},
    "scenes": {
      "type": "array",
      "minItems": 3,
      "items": {
        "type": "object",
        "required": ["scene_number", "scene_type", "beats", "needs_animation", "transition_to_next", "scene_importance"],
        "properties": {
          "scene_number": {"type": "integer", "minimum": 1},
          "scene_type": {"type": "string", "enum": ["hook","explanation","story","analysis","revelation","summary","credits"]},
          "beats": {"type": "array", "items": {"type": "string"}},
          "learning_objectives": {"type": "array", "items": {"type": "string"}},
          "needs_animation": {"type": "boolean"},
          "transition_to_next": {"type": "string", "enum": ["cut","fade","wipe","morph"]},
          "scene_importance": {"type": "integer", "minimum": 1, "maximum": 5}
        }
      }
    }
  }
}
```

### 4.2 Scene Script Writer — `ScenePackage.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ScenePackage",
  "type": "object",
  "required": ["scene_number","narration_script","visuals","tts","timing","continuity"],
  "properties": {
    "scene_number": {"type": "integer"},
    "narration_script": {
      "type": "array",
      "items": {"type": "object", "required": ["line","at_ms"],
        "properties": {"line": {"type": "string"}, "at_ms": {"type": "integer"}, "pause_ms": {"type": "integer"}}}
    },
    "dialogue": {"type": "array", "items": {"type": "object", "properties": {"speaker": {"type": "string"}, "line": {"type": "string"}}}},
    "visuals": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["frame_id","shot_type","image_prompt","aspect_ratio"],
        "properties": {
          "frame_id": {"type": "string"},
          "shot_type": {"type": "string", "enum": ["wide","medium","close","macro"]},
          "camera_motion": {"type": "string"},
          "character_pose": {"type": "string"},
          "expression": {"type": "string"},
          "background": {"type": "string"},
          "foreground_props": {"type": "string"},
          "lighting": {"type": "string"},
          "color_mood": {"type": "string"},
          "image_prompt": {"type": "string", "minLength": 40},
          "negative_prompt": {"type": "string"},
          "model_hints": {"type": "array", "items": {"type": "string"}},
          "aspect_ratio": {"type": "string", "enum": ["16:9","9:16","1:1","4:5"]},
          "seed": {"type": "integer"},
          "guidance_scale": {"type": "number"}
        }
      }
    },
    "tts": {
      "type": "object",
      "required": ["engine","voice","elevenlabs_settings"],
      "properties": {
        "engine": {"type": "string", "enum": ["elevenlabs"]},
        "voice": {"type": "string"},
        "language": {"type": "string", "default": "en-US"},
        "elevenlabs_settings": {
          "type": "object",
          "properties": {"stability": {"type": "number"}, "similarity_boost": {"type": "number"}, "style": {"type": "number"}, "speed": {"type": "number"}, "loudness": {"type": "number"}}
        }
      }
    },
    "sfx_cues": {"type": "array", "items": {"type": "object", "properties": {"cue": {"type": "string"}, "at_ms": {"type": "integer"}, "duration_ms": {"type": "integer"}}}},
    "on_screen_text": {"type": "array", "items": {"type": "object", "properties": {"text": {"type": "string"}, "at_ms": {"type": "integer"}, "duration_ms": {"type": "integer"}, "style": {"type": "string"}}}},
    "timing": {"type": "object", "properties": {"total_ms": {"type": "integer"}}},
    "continuity": {"type": "object", "properties": {"in_from": {"type": "string"}, "out_to": {"type": "string"}, "callback_tags": {"type": "array", "items": {"type": "string"}}}},
    "safety_checks": {"type": "array", "items": {"type": "string"}}
  }
}
```

### 4.3 Image Create Agent — `ImageAsset.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ImageAsset",
  "type": "object",
  "required": ["frame_id","image_uri","prompt_used","model"],
  "properties": {
    "frame_id": {"type": "string"},
    "image_uri": {"type": "string"},
    "thumbnail_uri": {"type": "string"},
    "prompt_used": {"type": "string"},
    "negative_prompt_used": {"type": "string"},
    "model": {"type": "string"},
    "sampler": {"type": "string"},
    "cfg": {"type": "number"},
    "steps": {"type": "integer"},
    "seed": {"type": "integer"},
    "safety_result": {"type": "string"}
  }
}
```

---

## 5) Validation & guardrails

### Static validators (pre‑run)

* **Schema validation** for each agent output (Ajv in Node or `jsonschema` in Python).
* **Spelling & terminology** normalization (e.g., breed names, gene names like **FGF4**).
* **Voice settings**: Ensure ElevenLabs values within \[0,1] and speed within \[0.7, 1.3].
* **Prompt checks**: Non‑empty positive prompt; optional negative prompt; max length; no disallowed content.

### Semantic checks (LLM‑assisted)

* **Continuity**: character, outfit, props persistent across frames (e.g., hunting horn).
* **Educational density**: does narration hit learning objectives?
* **Fact grounding**: flag claims that need citations (e.g., FGF4 retrogene) and mark for human review.

### Runtime checks (post‑generation)

* **Image‑text match** score (CLIP similarity) above threshold.
* **Timing**: speech duration vs. visual duration (use TTS duration estimator).

---

## 6) Prompting templates

### 6.1 Scene Script Writer (LLM) — Template

```
SYSTEM: You are the Scene Script Writer. Expand each scene into production‑ready assets. Respect the JSON schema. Do not repeat previous scenes. Fix typos. Keep tone: {overall_style}. Character: {character}. Outfit: {cosplay}.

USER INPUT:
{scene_from_fsw_json}

GUIDELINES:
- Hook first line with a curiosity gap.
- Use visual metaphors: {metaphors}.
- Add concrete facts and keep them accurate.
- Emit ONLY a valid JSON matching ScenePackage.json.
```

### 6.2 Image Create Agent — Template

```
SYSTEM: You are the Image Create Agent. For each visual frame, convert SSW visual spec to a final prompt. Keep character consistent across frames.

USER INPUT:
{visuals_array_from_ssw}

RESPONSE: Array of ImageAsset objects. Do not invent frames.
```

---

## 7) Worked example — Your Scene 1 (improved SSW output)

**Input (FSW scene 1 gist):** Hook about dachshund silhouette; needs\_animation; fade transition.

**SSW Output (excerpt; valid to schema):**

```json
{
  "scene_number": 1,
  "narration_script": [
    {"line": "Why would a dog be built like a hotdog on tiny stilts?", "at_ms": 0, "pause_ms": 200},
    {"line": "Meet the dachshund — a long body, keen nose, and purpose‑built short legs.", "at_ms": 1400},
    {"line": "By the end of this video, you'll know the genetic twist and hunting history behind that shape.", "at_ms": 3600}
  ],
  "dialogue": [],
  "visuals": [
    {
      "frame_id": "1A",
      "shot_type": "wide",
      "camera_motion": "slow push‑in",
      "character_pose": "pointing at chalkboard",
      "expression": "curious",
      "background": "classroom with stylized chalkboard sketch of a dachshund silhouette",
      "foreground_props": "tiny hunting horn on desk, magnifying glass",
      "lighting": "soft key, chalk dust motes",
      "color_mood": "warm browns and forest greens",
      "image_prompt": "cute blob‑like mascot named Huh dressed as a 17th‑century German forester, tiny hunting horn, magnifying glass; chalkboard drawing of a dachshund silhouette with long body and short legs; cozy educational set; soft cinematic lighting; whimsical, heartwarming artstyle; clean linework; high detail",
      "negative_prompt": "realistic gore, text artifacts, watermark, extra limbs",
      "model_hints": ["illustration", "studio‑quality", "consistent character"],
      "aspect_ratio": "16:9",
      "seed": 123456,
      "guidance_scale": 7.5
    }
  ],
  "tts": {
    "engine": "elevenlabs",
    "voice": "friendly‑narrator",
    "language": "en-US",
    "elevenlabs_settings": {"stability": 0.35, "similarity_boost": 0.8, "style": 0.85, "speed": 1.08, "loudness": 0.2}
  },
  "sfx_cues": [{"cue": "soft chalk scratch", "at_ms": 1200, "duration_ms": 800}],
  "on_screen_text": [{"text": "Why so short?", "at_ms": 200, "duration_ms": 1600, "style": "chalk hand‑lettering"}],
  "timing": {"total_ms": 5200},
  "continuity": {"in_from": "cut", "out_to": "fade", "callback_tags": ["hunting horn", "chalkboard"]},
  "safety_checks": ["schema_ok", "style_within_bounds"]
}
```

---

## 8) Critique of current `script.json`

* **Typos/consistency:** "dachshaund" → "dachshund" across title/subject.
* **Field duplication:** `dialogue` is used as narration; separate `narration_script` vs `dialogue`.
* **Image prompts:** Currently just echo text; replace with **visual spec** + crafted prompt + **negative prompt** + **style hints** + **aspect ratio**.
* **Timing:** No per‑line timings; add `total_ms` and `at_ms` to enable music beats and transitions.
* **Education signals:** Great intent; move guidelines into SSW template rather than raw scene JSON.
* **Flags:** Keep `needs_animation` & `transition_to_next`, add `scene_importance` (1–5) and `callback_tags`.

---

## 9) Orchestrator state machine (pseudocode)

```python
for scene in full_script.scenes:
    ssw = run_llm(scene_ssw_prompt(scene, global_context))
    assert validate(ssw, ScenePackageSchema)
    qc = run_semantic_checks(ssw)
    if not qc.ok:
        ssw = auto_revise(ssw, qc.feedback)
    frames = []
    for v in ssw["visuals"]:
        asset = generate_image(v)
        frames.append(asset)
    tts_audio = synthesize(ssw["narration_script"], ssw["tts"])    
    assemble_video(ssw, frames, tts_audio)
```

---

## 10) Implementation notes

* **Programming language:** Typescript (Node) or Python. Use Ajv (`ajv@v8`) or `jsonschema` for validation.
* **Determinism:** Allow `seed` override via CLI for reproducible renders.
* **Character consistency:** Maintain a **character card** (small image + text traits) and include as few‑shot image conditioning when supported.
* **Asset store:** Save per `project_id/scene/frame`. Embed metadata JSON next to PNG.
* **Assembler:** FFmpeg timeline composed from `timing` and `sfx_cues`. Use TTS duration prediction to adjust cuts.

---

## 11) Testing & evaluation

* **Unit tests:** schema compliance, prompt sanitation, timing sum ≈ total\_ms.
* **Golden scenes:** Store 3–5 approved SSW outputs and diff future runs.
* **Human review checklist:** hooks present? facts grounded? continuity props? brand‑safe?

---

## 12) Migration plan from current code

1. Keep current FSW but **simplify** it to high‑level beats; remove low‑level fields (TTS, image\_prompt).
2. Add SSW agent using the template in §6.1 and Schema §4.2.
3. Add ICA wrapper to your image API with Schema §4.3.
4. Implement orchestrator validation gates (Schema → Semantic → Safety) before generating assets.
5. Convert your existing `script.json` to **FullScript.json**, then generate scenes via SSW.

---

## 13) Deliverables for the coding agent

* JSON Schemas: `FullScript.json`, `ScenePackage.json`, `ImageAsset.json`.
* Prompt files: `ssw_prompt.txt`, `ica_prompt.txt`.
* Orchestrator with CLI: `generate --topic "Why are dachshunds short" --style friendly --ar 16:9`.
* Sample inputs/outputs (see §7).
* Validator suite + CI job.

---

## 14) Next up (you can assign)

* [ ] Convert your existing sample `script.json` → `FullScript.json` using the schema.
* [ ] Implement SSW prompt + function call.
* [ ] Implement ICA adapter (Stable Diffusion / Flux / Midjourney API).
* [ ] Build FFmpeg assembler from `timing` + `sfx_cues`.
* [ ] Add a quick web preview to scrub through scenes.

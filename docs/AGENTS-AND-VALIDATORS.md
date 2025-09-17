# Agents and Validators - Detailed Guide

*New Multi-Agent Architecture - September 17, 2025*

## 🤖 Agent Ecosystem Overview

The new architecture implements a **true multi-agent system** where each agent has a specific, well-defined role in the video production pipeline. This document explains how each component works and how they interact.

---

## 🎬 Core Agents

### 1. Full Script Writer (FSW)
**File**: `src/agents/full_script_writer_agent.py`
**Role**: **Story Architect** - Creates high-level narrative structure

#### What it does:
- Analyzes the input topic and creates a compelling story framework
- Determines optimal scene count (3-8 scenes) based on topic complexity
- Defines scene types, order, and narrative flow
- Sets learning objectives for each scene
- Assigns importance levels (1-5) and animation requirements
- Plans transitions between scenes

#### What it does NOT do:
- Detailed narration scripts
- Specific image prompts
- TTS/voice settings
- Character poses or expressions
- Low-level production details

#### Key Dependencies:
- **Story Focus Engine**: Refines story focus and engagement
- **Story Validator**: Validates feasibility and complexity
- **Shared Context Manager**: Maintains consistency

#### Input/Output:
```
INPUT: topic, length_preference, style_profile, target_audience
OUTPUT: FullScript.json (title, logline, story_summary, scenes[])
```

---

### 2. Scene Script Writer (SSW)
**File**: `src/agents/scene_script_writer_agent.py`
**Role**: **Production Designer** - Transforms beats into production-ready packages

#### What it does:
- Takes high-level scene beats from FSW
- Expands them into detailed, timed narration scripts
- Creates comprehensive visual storyboards (3-8 frames per scene)
- Designs specific image prompts with technical specifications
- Configures TTS settings and voice parameters
- Plans sound effects and on-screen text elements
- Manages scene continuity and visual consistency
- Performs educational content enhancement

#### Key Features:
- **ELABORATION**: Adds rich details, facts, and compelling narratives
- **HOOKING**: Includes attention-grabbing elements and curiosity gaps
- **TIMING**: Precise millisecond timing for narration and effects
- **VISUAL DETAIL**: Shot types, camera motion, lighting, color mood
- **CONTINUITY**: Callback tags and visual motifs across scenes

#### Key Dependencies:
- **Educational Enhancer**: Adds educational depth and metaphors
- **Image Style Selector**: Chooses optimal visual styles
- **Shared Context Manager**: Maintains character and style consistency

#### Input/Output:
```
INPUT: scene_data (from FSW), global_context, previous_scenes
OUTPUT: ScenePackage.json (narration_script, visuals[], tts, timing, continuity)
```

---

### 3. Image Create Agent (ICA)
**File**: `src/agents/image_create_agent.py`
**Role**: **Visual Artist** - Generates images matching exact specifications

#### What it does:
- Processes visual frame specifications from SSW
- Enhances prompts with character consistency elements
- Performs prompt sanitation and safety checks
- Generates images using AI models (or mock images in cost-saving mode)
- Creates comprehensive metadata for each asset
- Manages file organization and thumbnails

#### Key Features:
- **Character Consistency**: Uses Huh character reference for consistent appearance
- **Prompt Enhancement**: Adds style keywords and quality modifiers
- **Safety Validation**: Content safety and appropriateness checks
- **Metadata Tracking**: Generation parameters, timing, file info
- **Cost Control**: Mock image mode for development/testing

#### Key Dependencies:
- **Session Manager**: File storage and organization
- **Huh Character Reference**: Maintains visual consistency

#### Input/Output:
```
INPUT: scene_package.visuals[] (frame specs, prompts, settings)
OUTPUT: ImageAsset[].json (image_uri, metadata, generation_info)
```

---

### 4. Voice Generate Agent (VGA)
**File**: `src/agents/voice_generate_agent.py`
**Role**: **Voice Artist** - Generates high-quality TTS audio files

#### What it does:
- Extracts narration text from Scene Script Writer packages
- Applies scene-specific ElevenLabs TTS settings
- Generates MP3 audio files using ElevenLabs API
- Manages voice file storage with ordered naming
- Creates comprehensive voice asset metadata

#### Key Features:
- **ElevenLabs Integration**: Professional TTS with voice customization
- **Scene-Specific Settings**: Each scene can have different TTS parameters
- **Default Voice Fallback**: Uses free Adam voice if custom voice unavailable
- **Metadata Tracking**: Generation parameters, file size, timing
- **Error Handling**: Detailed API response logging and fallback mechanisms

#### Key Dependencies:
- **Session Manager**: Voice file storage organization
- **ElevenLabs API**: External TTS service integration

#### Input/Output:
```
INPUT: ScenePackage[].json (narration_script, elevenlabs_settings)
OUTPUT: voice_assets.json (voice_file, metadata, generation_info)
```

---

### 5. Orchestrator Agent
**File**: `src/agents/orchestrator_agent.py`
**Role**: **Pipeline Manager** - Controls entire workflow and quality

#### What it does:
- Manages the complete video production pipeline
- Coordinates agent interactions and data flow
- Performs JSON schema validation at each stage
- Handles errors, retries, and fallback mechanisms
- Tracks timing, model usage, and performance metrics
- Generates comprehensive build reports
- Manages session lifecycle and file organization

#### Key Features:
- **State Machine**: Controls pipeline progression through stages
- **Validation Gates**: Schema validation before each stage advancement
- **Error Handling**: Graceful failure handling with detailed error tracking
- **Performance Monitoring**: Timing analysis and resource usage tracking
- **Build Reporting**: Comprehensive reports with success/failure metrics

#### Key Dependencies:
- **All Other Agents**: Orchestrates FSW → SSW → ICA pipeline
- **Session Manager**: Session creation and file management
- **JSON Schemas**: Validation and structure enforcement

#### Input/Output:
```
INPUT: topic, preferences, options
OUTPUT: Complete video package + build_report.json
```

---

## 🔍 Validation System

### Schema Validation
**Purpose**: Ensures structural compliance with JSON contracts

#### What it validates:
- **FullScript.json**: Story structure, scene planning, required fields
- **ScenePackage.json**: Production packages, timing, visual specs
- **ImageAsset.json**: Image metadata, generation parameters

#### How it works:
- Uses `jsonschema` library for strict validation
- Validates at each pipeline stage
- Currently set to WARNING mode (proceeds on failure)
- Tracks validation results in build reports

### Story Validator
**File**: `src/core/story_validator.py`
**Purpose**: Evaluates story quality and educational value

#### What it validates:
- **Feasibility**: How realistic the story execution is
- **Complexity**: Educational complexity level
- **Educational Value**: Learning potential and engagement
- **Target Audience Appropriateness**: Age and interest alignment

#### Validation Levels:
- **Feasibility**: `not_feasible`, `challenging`, `feasible`, `easy`
- **Complexity**: `simple`, `moderate`, `complex`, `expert`

### Educational Enhancer
**File**: `src/core/educational_enhancer.py`
**Purpose**: Adds educational depth and engagement elements

#### What it enhances:
- **Data Points**: Specific facts, statistics, examples
- **Key Concepts**: Core learning elements
- **Visual Metaphors**: Analogies and comparisons
- **Learning Objectives**: Clear educational goals
- **Assessment Criteria**: Quality measures

#### Enhancement Metrics:
- **Educational Density**: Content richness score (0.0-1.0)
- **Complexity Score**: Difficulty level assessment (0.0-1.0)
- **Element Count**: Number of enhanced elements added

---

## 🔗 How Components Connect

### 1. Story Focus Engine
**File**: `src/core/story_focus_engine.py`
**Connection**: FSW → Story Focus Engine

**Purpose**: Refines broad topics into focused, engaging narratives
**Patterns**: origin_story, turning_point, misconception, controversy, etc.
**Output**: Focused story with engagement and specificity scores

### 2. Shared Context Manager
**File**: `src/core/shared_context.py`
**Connection**: FSW → SSW → ICA (shared state)

**Purpose**: Maintains consistency across all agents
**Manages**: Character state, visual style, narrative context, technical constraints
**Updates**: After each scene generation to maintain continuity

### 3. Session Manager
**File**: `src/core/session_manager.py`
**Connection**: Orchestrator → All file operations

**Purpose**: Manages session lifecycle and file organization
**Features**: Date-prefixed session IDs (YYYYMMDD-UUID), structured directories
**Manages**: Scripts, images, metadata, prompts, build reports

### 4. Image Style Selector
**File**: `src/core/image_style_selector.py`
**Connection**: SSW → Image Style Selection

**Purpose**: Chooses optimal visual styles for each scene type
**Styles**: infographic, cinematic, comic, educational, etc.
**Selection**: Based on scene type, content, and educational goals

---

## 🎯 Pipeline Flow Summary

```
1. User provides topic
   ↓
2. Orchestrator creates session (YYYYMMDD-UUID)
   ↓
3. FSW creates story structure (FullScript.json)
   ↓ (Schema Validation)
4. SSW expands each scene (ScenePackage.json × N)
   ↓ (Schema Validation)
5. ICA generates images for all frames (ImageAsset.json)
   ↓ (Schema Validation)
6. VGA generates voice files for all scenes (voice_assets.json)
   ↓ (Schema Validation)
7. Orchestrator assembles final package + build report
   ↓
8. Complete video production package ready
```

## 📈 Quality Assurance

### Multi-Layer Validation:
1. **Schema Validation**: Structure and data type compliance
2. **Content Validation**: Educational value and story quality
3. **Safety Validation**: Content appropriateness and safety
4. **Continuity Validation**: Visual and narrative consistency
5. **Technical Validation**: TTS settings, timing, prompt quality

### Error Handling:
- **Graceful Degradation**: System continues with warnings on non-critical failures
- **Retry Mechanisms**: Automatic retries with exponential backoff
- **Fallback Systems**: Mock data when AI generation fails
- **Comprehensive Logging**: Full prompt/response tracking for debugging

---

## 🚀 Performance Characteristics

### Typical Session Results:
- **5 scenes** with rich narrative structure
- **20-25 images** (4-5 frames per scene average)
- **Production-ready packages** with timing and TTS
- **Complete metadata** for assembly and editing
- **Comprehensive logging** for analysis and improvement

### Generation Time:
- **FSW**: ~25 seconds (story planning)
- **SSW**: ~300 seconds (detailed scene expansion)
- **ICA**: <1 second (cost-saving mode) / ~60 seconds (AI mode)
- **VGA**: ~65 seconds (voice generation for 5 scenes)
- **Total**: ~6-7 minutes for complete video package

# Script to Image/Video Flow - How It Works

## Overview

This document explains how the Script Writer Agent output is converted into images and videos. The flow shows the data transformation from script to final video assets.

## Data Flow Diagram

```
Script Writer Agent Output (VideoScript)
                    ↓
            Scene-by-Scene Processing
                    ↓
    ┌─────────────────────────────────────────┐
    │           Image Generation              │
    │  • image_create_prompt → Image          │
    │  • image_style → Visual Style           │
    │  • character consistency                │
    └─────────────────────────────────────────┘
                    ↓
    ┌─────────────────────────────────────────┐
    │           Audio Generation              │
    │  • dialogue → Voice Narration           │
    │  • voice_tone → Emotional Delivery      │
    │  • elevenlabs_settings → Voice Quality  │
    └─────────────────────────────────────────┘
                    ↓
    ┌─────────────────────────────────────────┐
    │           Video Generation              │
    │  • needs_animation → Static/Animated    │
    │  • video_prompt → Animation Details     │
    │  • transition_to_next → Scene Transitions│
    └─────────────────────────────────────────┘
                    ↓
            Final Video Assembly
```

## Detailed Flow Explanation

### 1. Script Writer Agent Output

The Script Writer Agent produces a `VideoScript` object with this structure:

```python
VideoScript {
    title: "Understanding Photosynthesis: A Complete Guide",
    main_character_description: "A friendly, knowledgeable character...",
    overall_style: "educational",
    scenes: [
        Scene {
            scene_number: 1,
            scene_type: "hook",
            dialogue: "Did you know that photosynthesis...",
            voice_tone: "excited",
            elevenlabs_settings: {...},
            image_style: "single_character",
            image_create_prompt: "Our fixed character with an excited expression...",
            needs_animation: true,
            video_prompt: "Character starts with a curious expression...",
            transition_to_next: "fade",
            hook_technique: "shocking_fact"
        },
        // ... more scenes
    ]
}
```

### 2. Image Generation Process

For each scene, the Image Generation Agent processes:

#### Input Data:
- `image_create_prompt`: Detailed description for image generation
- `image_style`: Visual style type (single_character, diagram_explanation, etc.)
- `main_character_description`: Character consistency reference
- `scene_type`: Context for appropriate visual treatment

#### Processing:
```python
# Example for Scene 1
image_prompt = scene.image_create_prompt
# "Our fixed character with an excited expression, pointing at the camera with wide eyes..."

image_style = scene.image_style
# "single_character"

character_ref = script.main_character_description
# "A friendly, knowledgeable character with expressive features..."

# Generate image using AI image generation service
generated_image = image_generator.generate(
    prompt=image_prompt,
    style=image_style,
    character_consistency=character_ref
)
```

#### Output:
- High-quality image file (PNG/JPG)
- Image metadata (resolution, style, character consistency)
- Character consistency validation

### 3. Audio Generation Process

For each scene, the Audio Generation Agent processes:

#### Input Data:
- `dialogue`: Text to be spoken
- `voice_tone`: Emotional delivery style
- `elevenlabs_settings`: Voice quality parameters

#### Processing:
```python
# Example for Scene 1
dialogue_text = scene.dialogue
# "Did you know that photosynthesis is more fascinating than you think?"

voice_tone = scene.voice_tone
# "excited"

voice_settings = scene.elevenlabs_settings
# {
#     "stability": 0.3,
#     "similarity_boost": 0.8,
#     "style": 0.8,
#     "speed": 1.1,
#     "loudness": 0.2
# }

# Generate audio using text-to-speech service
generated_audio = audio_generator.generate(
    text=dialogue_text,
    voice_tone=voice_tone,
    settings=voice_settings
)
```

#### Output:
- Audio file (MP3/WAV)
- Audio metadata (duration, quality, voice characteristics)
- Synchronization timing data

### 4. Video Generation Process

For each scene, the Video Generation Agent processes:

#### Input Data:
- Generated image from Image Agent
- Generated audio from Audio Agent
- `needs_animation`: Whether to animate or keep static
- `video_prompt`: Animation details (if needed)
- `transition_to_next`: How to transition to next scene

#### Processing:
```python
# Example for Scene 1
scene_image = generated_images[scene.scene_number - 1]
scene_audio = generated_audio[scene.scene_number - 1]

if scene.needs_animation:
    animation_prompt = scene.video_prompt
    # "Character starts with a curious expression, then points excitedly..."
    
    # Generate animated video
    scene_video = video_generator.create_animated_scene(
        base_image=scene_image,
        audio=scene_audio,
        animation_prompt=animation_prompt,
        duration=audio_duration
    )
else:
    # Create static video (image + audio)
    scene_video = video_generator.create_static_scene(
        image=scene_image,
        audio=scene_audio,
        duration=audio_duration
    )

# Add transition effect
if scene.transition_to_next != "none":
    scene_video = video_generator.add_transition(
        video=scene_video,
        transition_type=scene.transition_to_next
    )
```

#### Output:
- Video segment file (MP4)
- Video metadata (duration, resolution, effects)
- Transition effects applied

### 5. Final Video Assembly

The Video Assembly process combines all scene videos:

```python
# Combine all scene videos in order
final_video = video_assembler.combine_scenes(
    scenes=scene_videos,
    transitions=transition_effects,
    title=script.title,
    credits=script.overall_style
)

# Apply final processing
final_video = video_processor.optimize(
    video=final_video,
    target_resolution="1920x1080",
    target_fps=30,
    compression="high_quality"
)
```

## Key Data Transformations

### 1. Text → Image
```
"Our fixed character with an excited expression, pointing at the camera with wide eyes, wearing a curious expression. The background shows subtle photosynthesis related elements floating gently. Clean, modern cartoon style with vibrant colors."
                    ↓
[AI Image Generation Service]
                    ↓
High-quality PNG image (1024x1024) with consistent character
```

### 2. Text → Audio
```
"Did you know that photosynthesis is more fascinating than you think?"
                    ↓
[Text-to-Speech Service with voice_tone="excited"]
                    ↓
MP3 audio file (5.2 seconds) with excited voice delivery
```

### 3. Image + Audio → Video
```
Static Image + Audio Track
                    ↓
[Video Generation Service]
                    ↓
MP4 video segment (5.2 seconds) with synchronized audio
```

### 4. Animation Enhancement
```
Static Image + Animation Prompt
"Character starts with a curious expression, then points excitedly at the camera as floating elements appear around them"
                    ↓
[Animation Generation Service]
                    ↓
Animated MP4 video segment with character movement and effects
```

## Character Consistency

The system maintains character consistency through:

1. **Reference Description**: `main_character_description` from script
2. **Style Consistency**: Same visual style across all scenes
3. **Pose Variations**: Different poses but same character design
4. **Quality Validation**: Automated checks for character consistency

## Quality Assurance

Each step includes quality validation:

- **Image Quality**: Resolution, clarity, character consistency
- **Audio Quality**: Voice clarity, emotional delivery, timing
- **Video Quality**: Smooth animation, proper transitions, synchronization
- **Overall Quality**: Cohesive visual style, engaging content

## Example: Complete Flow for One Scene

### Input (from Script Writer Agent):
```json
{
  "scene_number": 1,
  "scene_type": "hook",
  "dialogue": "Did you know that photosynthesis is more fascinating than you think?",
  "voice_tone": "excited",
  "image_style": "single_character",
  "image_create_prompt": "Our fixed character with an excited expression, pointing at the camera with wide eyes...",
  "needs_animation": true,
  "video_prompt": "Character starts with a curious expression, then points excitedly at the camera as floating elements appear around them",
  "transition_to_next": "fade"
}
```

### Output (Final Video Segment):
- **Image**: 1024x1024 PNG of excited character pointing at camera
- **Audio**: 5.2-second MP3 with excited voice delivery
- **Video**: 5.2-second MP4 with character animation and floating elements
- **Transition**: Fade effect to next scene

This flow ensures that every element from the script is properly converted into high-quality visual and audio assets that work together to create an engaging educational video.

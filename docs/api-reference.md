# API Reference - ShortFactory Agent

## Overview

This document provides comprehensive API reference for all agents in the ShortFactory system. Each agent exposes specific endpoints and data structures for integration.

## Base URL

```
Production: https://api.shortfactory.com/v1
Development: http://localhost:8000/v1
```

## Authentication

All API requests require authentication using API keys:

```http
Authorization: Bearer YOUR_API_KEY
```

## Common Response Format

All API responses follow this structure:

```json
{
  "success": boolean,
  "data": object | null,
  "error": {
    "code": string,
    "message": string,
    "details": object
  } | null,
  "metadata": {
    "request_id": string,
    "timestamp": string,
    "processing_time": number
  }
}
```

## Script Writer Agent API

### Generate Video Script

**Endpoint**: `POST /script/generate`

**Description**: Generate a complete video script from a given subject.

**Request Body**:
```json
{
  "subject": "string (required)",
  "language": "string (required)",
  "max_video_scenes": "integer (required, 5-8 recommended)",
  "style_preferences": {
    "overall_style": "string (optional)",
    "target_audience": "string (optional)",
    "complexity_level": "string (optional)"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "script_id": "string",
    "title": "string",
    "main_character_description": "string",
    "overall_style": "string",
    "scenes": [
      {
        "scene_index": 0,
        "scene_type": "hook",
        "image_style": "single_character",
        "image_create_prompt": "string",
        "dialogue": "string",
        "voice_tone": "excited",
        "needs_animation": true,
        "video_prompt": "string",
        "transition_type": "fade",
        "hook_technique": "shocking_fact"
      }
    ],
    "estimated_duration": "number",
    "created_at": "string"
  }
}
```

**Error Codes**:
- `INVALID_SUBJECT`: Subject is empty or invalid
- `INVALID_LANGUAGE`: Language not supported
- `SCENE_COUNT_EXCEEDED`: Too many scenes requested
- `GENERATION_FAILED`: Script generation failed

### Get Script Status

**Endpoint**: `GET /script/{script_id}/status`

**Description**: Check the status of a script generation request.

**Response**:
```json
{
  "success": true,
  "data": {
    "script_id": "string",
    "status": "processing|completed|failed",
    "progress": "number (0-100)",
    "estimated_completion": "string"
  }
}
```

## Image Generation Agent API

### Generate Images

**Endpoint**: `POST /image/generate`

**Description**: Generate images for video scenes based on script.

**Request Body**:
```json
{
  "script_id": "string (required)",
  "scenes": [
    {
      "scene_index": 0,
      "image_create_prompt": "string",
      "image_style": "single_character",
      "character_reference": "string"
    }
  ],
  "quality_settings": {
    "resolution": "string (optional, default: 1024x1024)",
    "style_consistency": "boolean (optional, default: true)",
    "generation_quality": "string (optional, default: standard)"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "generation_id": "string",
    "images": [
      {
        "scene_index": 0,
        "image_url": "string",
        "image_metadata": {
          "style": "single_character",
          "character_consistency": true,
          "resolution": "1024x1024",
          "format": "png",
          "file_size": 1024000
        }
      }
    ],
    "total_images": 5,
    "generated_at": "string"
  }
}
```

### Get Image Generation Status

**Endpoint**: `GET /image/{generation_id}/status`

**Description**: Check the status of image generation.

**Response**:
```json
{
  "success": true,
  "data": {
    "generation_id": "string",
    "status": "processing|completed|failed",
    "progress": "number (0-100)",
    "completed_images": "number",
    "total_images": "number"
  }
}
```

## Audio Generation Agent API

### Generate Audio

**Endpoint**: `POST /audio/generate`

**Description**: Generate voice narration and audio for video scenes.

**Request Body**:
```json
{
  "script_id": "string (required)",
  "scenes": [
    {
      "scene_index": 0,
      "dialogue": "string",
      "voice_tone": "excited",
      "language": "string"
    }
  ],
  "audio_settings": {
    "voice_id": "string (optional)",
    "speed": "number (optional, default: 1.0)",
    "pitch": "number (optional, default: 1.0)",
    "volume": "number (optional, default: 1.0)",
    "background_music": "boolean (optional, default: false)"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "generation_id": "string",
    "audio_files": [
      {
        "scene_index": 0,
        "audio_url": "string",
        "audio_metadata": {
          "duration": 5.2,
          "format": "mp3",
          "sample_rate": 44100,
          "channels": 2,
          "voice_tone": "excited",
          "file_size": 512000
        }
      }
    ],
    "total_duration": 30.5,
    "generated_at": "string"
  }
}
```

### Get Audio Generation Status

**Endpoint**: `GET /audio/{generation_id}/status`

**Description**: Check the status of audio generation.

**Response**:
```json
{
  "success": true,
  "data": {
    "generation_id": "string",
    "status": "processing|completed|failed",
    "progress": "number (0-100)",
    "completed_scenes": "number",
    "total_scenes": "number"
  }
}
```

## Video Generation Agent API

### Generate Video

**Endpoint**: `POST /video/generate`

**Description**: Create final video from images, audio, and script.

**Request Body**:
```json
{
  "script_id": "string (required)",
  "image_generation_id": "string (required)",
  "audio_generation_id": "string (required)",
  "video_settings": {
    "resolution": "string (optional, default: 1920x1080)",
    "fps": "number (optional, default: 30)",
    "format": "string (optional, default: mp4)",
    "quality": "string (optional, default: high)",
    "transitions": "boolean (optional, default: true)",
    "subtitles": "boolean (optional, default: false)"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "video_id": "string",
    "video_url": "string",
    "video_metadata": {
      "duration": 45.2,
      "resolution": "1920x1080",
      "fps": 30,
      "format": "mp4",
      "file_size": 15728640,
      "quality_score": 8.5
    },
    "generated_at": "string"
  }
}
```

### Get Video Generation Status

**Endpoint**: `GET /video/{video_id}/status`

**Description**: Check the status of video generation.

**Response**:
```json
{
  "success": true,
  "data": {
    "video_id": "string",
    "status": "processing|completed|failed",
    "progress": "number (0-100)",
    "current_step": "string",
    "estimated_completion": "string"
  }
}
```

## Orchestration API

### Create Complete Video

**Endpoint**: `POST /orchestration/create-video`

**Description**: Create a complete video using all agents in sequence.

**Request Body**:
```json
{
  "subject": "string (required)",
  "language": "string (required)",
  "max_video_scenes": "number (required)",
  "preferences": {
    "overall_style": "string (optional)",
    "target_audience": "string (optional)",
    "quality_level": "string (optional, default: standard)"
  },
  "callback_url": "string (optional)"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "job_id": "string",
    "status": "queued",
    "estimated_completion": "string",
    "callback_url": "string"
  }
}
```

### Get Job Status

**Endpoint**: `GET /orchestration/{job_id}/status`

**Description**: Check the status of a complete video generation job.

**Response**:
```json
{
  "success": true,
  "data": {
    "job_id": "string",
    "status": "queued|processing|completed|failed",
    "progress": "number (0-100)",
    "current_agent": "string",
    "completed_steps": [
      "script_generation",
      "image_generation"
    ],
    "video_url": "string (if completed)",
    "error_message": "string (if failed)"
  }
}
```

## Webhook Events

### Job Completion Webhook

When a job completes (successfully or with failure), a webhook is sent to the provided callback URL:

```json
{
  "event": "job.completed",
  "job_id": "string",
  "status": "success|failure",
  "data": {
    "video_url": "string (if successful)",
    "error_message": "string (if failed)",
    "processing_time": "number",
    "quality_score": "number (if successful)"
  },
  "timestamp": "string"
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing API key
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_SUBJECT",
    "message": "Subject cannot be empty",
    "details": {
      "field": "subject",
      "value": "",
      "constraints": ["required", "min_length: 1"]
    }
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z",
    "processing_time": 0.001
  }
}
```

## Rate Limits

- **Free Tier**: 10 requests per hour
- **Basic Tier**: 100 requests per hour
- **Pro Tier**: 1000 requests per hour
- **Enterprise**: Custom limits

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## SDKs and Libraries

### Python SDK

```python
from shortfactory import ShortFactoryClient

client = ShortFactoryClient(api_key="your-api-key")

# Generate complete video
result = client.create_video(
    subject="How photosynthesis works",
    language="English",
    max_video_scenes=6
)

print(f"Video URL: {result.video_url}")
```

### JavaScript SDK

```javascript
import { ShortFactoryClient } from '@shortfactory/sdk';

const client = new ShortFactoryClient('your-api-key');

// Generate complete video
const result = await client.createVideo({
  subject: 'How photosynthesis works',
  language: 'English',
  maxVideoScenes: 6
});

console.log(`Video URL: ${result.videoUrl}`);
```

## Testing

### Test Environment

Use the test environment for development and testing:

```bash
curl -X POST https://api-test.shortfactory.com/v1/script/generate \
  -H "Authorization: Bearer YOUR_TEST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test subject",
    "language": "English",
    "max_video_scenes": 5
  }'
```

### Postman Collection

A complete Postman collection is available for testing all endpoints:

[Download Postman Collection](https://api.shortfactory.com/docs/postman-collection.json)

## Support

For API support and questions:

- **Documentation**: https://docs.shortfactory.com
- **Support Email**: api-support@shortfactory.com
- **Status Page**: https://status.shortfactory.com
- **GitHub Issues**: https://github.com/shortfactory/api-issues

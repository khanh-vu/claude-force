# Building a Fully Autonomous n8n Video Automation Workflow

This comprehensive guide provides a complete blueprint for creating an autonomous system that detects trending videos, generates original AI video content using Google's Veo 3.1, and automatically posts to YouTube, Facebook, and TikTok.

## 1. System Architecture Overview

The workflow operates in six core phases executed sequentially through n8n:

**Trend Detection** → **Content Analysis** → **AI Video Generation** → **Quality Control** → **Multi-Platform Publishing** → **Monitoring**

### Core Technology Stack
- **Automation Platform**: n8n (self-hosted or cloud)
- **AI Video Generation**: Google Veo 3.1 on Vertex AI
- **Trend Detection**: YouTube Data API v3, Apify (TikTok), third-party aggregators
- **Publishing**: Platform-specific APIs (YouTube, Facebook Graph API, TikTok Content Posting API)
- **Storage**: Google Cloud Storage for video files
- **Scheduling**: n8n Cron triggers for autonomous operation

---

## 2. Trend Detection System

### 2.1 YouTube Trending Detection

**Primary Endpoint**: `videos.list` with `chart=mostPopular`

**Implementation in n8n**:

```javascript
// HTTP Request Node Configuration
Method: GET
URL: https://www.googleapis.com/youtube/v3/videos
Authentication: None (API Key in parameters)

Parameters:
{
  "part": "snippet,statistics",
  "chart": "mostPopular",
  "regionCode": "US",
  "videoCategoryId": "22",
  "maxResults": "50",
  "key": "{{$credentials.youtubeApiKey}}"
}
```

**Key Metrics to Extract**:
- `viewCount`: Total views
- `likeCount`: Engagement indicator
- `commentCount`: Discussion level
- Calculate engagement rate: `(likes + comments) / views × 100`

**Rate Limits**: 10,000 units/day (1 unit per call)
**Recommended Polling**: Every 30-60 minutes

### 2.2 TikTok Trending Detection

TikTok has restrictive official APIs. **Best approach**: Apify scraping service.

**Apify Actor Integration** (n8n HTTP Request):

```javascript
// HTTP Request Node
Method: POST
URL: https://api.apify.com/v2/acts/novi~tiktok-trend-api/runs
Authentication: Bearer Token

Headers:
{
  "Content-Type": "application/json"
}

Body:
{
  "country": "US",
  "maxResults": 100
}

// Wait for completion, then fetch results
GET https://api.apify.com/v2/acts/novi~tiktok-trend-api/runs/{runId}/dataset/items
```

**Cost**: ~$49-99/month for Apify subscription
**Alternative**: TikTok Research API (requires academic approval)

### 2.3 Facebook Trending

Facebook has **no public trending API**. Workarounds:

**Option A**: Monitor high-engagement pages using Graph API
```javascript
GET https://graph.facebook.com/v20.0/{page-id}/videos
  ?fields=id,title,description,views,created_time
  &access_token={page_access_token}
```

**Option B**: Use social listening platforms
- Brandwatch ($$$)
- Phyllo Social Listening API
- Focus resources on YouTube + TikTok instead

### 2.4 Engagement Filtering Logic

**n8n Function Node** for trend scoring:

```javascript
// Calculate trend score for each video
const items = $input.all();

const scoredVideos = items.map(item => {
  const views = parseInt(item.json.viewCount) || 0;
  const likes = parseInt(item.json.likeCount) || 0;
  const comments = parseInt(item.json.commentCount) || 0;

  // Engagement rate
  const engagementRate = views > 0 ? ((likes + comments) / views) * 100 : 0;

  // Trend score (weighted formula)
  const trendScore = (views * 0.3) + (likes * 5) + (comments * 10) + (engagementRate * 1000);

  return {
    ...item.json,
    engagementRate,
    trendScore
  };
});

// Sort by trend score descending
scoredVideos.sort((a, b) => b.trendScore - a.trendScore);

// Return top 10
return scoredVideos.slice(0, 10).map(video => ({ json: video }));
```

### 2.5 Topic Extraction with NLP

**n8n Code Node** (Python with spaCy):

```python
import spacy
from collections import Counter

# Load English model
nlp = spacy.load("en_core_web_sm")

items = _input.all()
extracted_topics = []

for item in items:
    title = item['json']['title']
    description = item['json'].get('description', '')

    # Combine text
    text = f"{title}. {description}"

    # Process with spaCy
    doc = nlp(text)

    # Extract named entities and noun chunks
    entities = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PERSON', 'PRODUCT', 'EVENT']]
    keywords = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]

    # Extract hashtags (simple regex)
    import re
    hashtags = re.findall(r'#(\w+)', text)

    extracted_topics.append({
        'json': {
            'videoId': item['json']['id'],
            'title': title,
            'entities': entities,
            'keywords': keywords[:10],  # Top 10
            'hashtags': hashtags,
            'coreTheme': keywords[0] if keywords else 'general'
        }
    })

return extracted_topics
```

**Required Setup**:
1. Enable Python in n8n Code Node
2. Install dependencies: `spacy`, `en_core_web_sm`
3. Alternative: Use HTTP request to external NLP service (Hugging Face API)

---

## 3. AI Video Generation with Veo 3.1

### 3.1 Google Cloud Setup

**Prerequisites**:
1. Google Cloud Project with billing enabled
2. Enable Vertex AI API: `gcloud services enable aiplatform.googleapis.com`
3. Create service account with `roles/aiplatform.user`
4. Create Cloud Storage bucket for video output
5. Generate service account key JSON

**n8n Credentials Configuration**:
- Store service account JSON in n8n Credentials Manager
- Or use access token (expires hourly): `gcloud auth print-access-token`

### 3.2 Veo 3.1 API Integration

**n8n HTTP Request Node** for video generation:

```javascript
// Node 1: Initiate Video Generation
Method: POST
URL: https://us-central1-aiplatform.googleapis.com/v1/projects/{{$json.projectId}}/locations/us-central1/publishers/google/models/veo-3.1-generate-preview:predictLongRunning

Authentication:
- Type: Generic Credential Type
- Auth Type: OAuth2
- Or: Bearer Token with `gcloud auth print-access-token`

Headers:
{
  "Content-Type": "application/json"
}

Body:
{
  "instances": [{
    "prompt": "{{$json.generatedPrompt}}"
  }],
  "parameters": {
    "durationSeconds": 8,
    "aspectRatio": "{{$json.targetPlatform === 'tiktok' ? '9:16' : '16:9'}}",
    "resolution": "1080p",
    "generateAudio": true,
    "sampleCount": 1,
    "storageUri": "gs://your-bucket/videos/",
    "negativePrompt": "blur, distortion, watermark, low quality, text overlay"
  }
}
```

### 3.3 Veo 3.1 Cost Optimization

**Pricing**:
- **Veo 3.1 Standard**: $0.40/second with audio
- **Veo 3.1 Fast**: $0.15/second with audio (62.5% cheaper)
- **8-second video**: $3.20 (standard) or $1.20 (fast)

**Optimization Strategy**:
```javascript
// Decision Logic in n8n Function Node
const priorityScore = $json.trendScore;
const budget = 'medium'; // Config variable

let model = 'veo-3.1-fast-generate-preview'; // Default to fast

// Use standard model for high-priority trends
if (priorityScore > 100000 && budget === 'high') {
  model = 'veo-3.1-generate-preview';
}

return {
  json: {
    ...$json,
    selectedModel: model,
    estimatedCost: model.includes('fast') ? 1.20 : 3.20
  }
};
```

### 3.4 Polling for Completion

**n8n HTTP Request Node** (in loop):

```javascript
// Node 2: Check Operation Status
Method: POST
URL: https://us-central1-aiplatform.googleapis.com/v1/projects/{{$json.projectId}}/locations/us-central1/publishers/google/models/veo-3.1-generate-preview:fetchPredictOperation

Body:
{
  "operationName": "{{$json.operationName}}"
}

// Check response
// If done === false, wait 30 seconds and retry
// If done === true, extract video GCS URI
```

**Complete Polling Logic** with n8n Wait + Loop:

```
[Generate Video] → [Wait 30s] → [Check Status] → [IF done=false] → Loop back to Wait
                                                → [IF done=true] → [Download Video]
```

### 3.5 Prompt Engineering for Uniqueness

**Transformation Layer** (n8n Function Node):

```javascript
// Transform trending topic into unique prompt
const trendData = $json;

// Extract core theme without copying specifics
const coreTheme = trendData.coreTheme;
const originalTitle = trendData.title;

// Generate unique prompt with constraints
const uniquePrompt = `
Create an abstract visual representation of ${coreTheme}.
Use geometric shapes and motion graphics, NOT real people or specific objects.
Camera movement: Slow orbital rotation around central composition.
Color palette: Vibrant gradient from deep purple to electric cyan.
Lighting: High-key with soft shadows, modern tech aesthetic.
Style: Clean minimalist motion design, professional quality.
Duration focus: Emphasize smooth transitions and flowing movement.
Audio: Upbeat instrumental, no vocals.
AVOID: Any text, logos, watermarks, or realistic photography.
CONSTRAINT: This must look completely different from typical ${coreTheme} videos - focus on abstract representation.
`.trim();

return {
  json: {
    ...trendData,
    generatedPrompt: uniquePrompt,
    transformationNote: 'Abstract visual metaphor - no direct replication'
  }
};
```

**Key Prompt Principles**:
1. **Abstract over literal**: Use metaphors, not direct representations
2. **Unique constraints**: Specify what to avoid (common trending visual patterns)
3. **Style specificity**: Define exact camera, lighting, color (makes output distinctive)
4. **Negative prompts**: Block common elements that would create similarity

### 3.6 Alternative: Runway ML Integration

If Veo 3.1 has limitations:

```javascript
// Runway Gen-3 API
Method: POST
URL: https://api.runwayml.com/v1/generate

Headers:
{
  "Authorization": "Bearer {{$credentials.runwayApiKey}}",
  "Content-Type": "application/json"
}

Body:
{
  "prompt": "{{$json.generatedPrompt}}",
  "model": "gen3a_turbo",
  "duration": 10,
  "aspect_ratio": "16:9"
}

// Cost: ~$0.75/second
// Benefit: Longer videos (10+ seconds), more camera controls
```

---

## 4. Content Transformation Strategy

### 4.1 Three-Layer Transformation Framework

**Implementation in n8n Function Node**:

```javascript
// Layer 1: Topic Translation
function translateTopic(originalTopic) {
  // Map specific topics to general concepts
  const topicMap = {
    'morning routine': 'daily optimization strategies',
    'productivity hack': 'efficiency principles',
    'weight loss journey': 'sustainable health practices',
    'crypto trading': 'financial risk management'
  };
  return topicMap[originalTopic.toLowerCase()] || 'general lifestyle improvement';
}

// Layer 2: Format Modification
function modifyFormat(originalFormat) {
  const formats = ['abstract animation', 'motion graphics explainer', 'visual metaphor', 'geometric representation'];
  return formats[Math.floor(Math.random() * formats.length)];
}

// Layer 3: Style Transformation
function transformStyle(trendData) {
  return {
    visualStyle: 'minimalist geometric',
    colorPalette: 'custom gradient (purple-cyan)',
    cameraMovement: 'orbital rotation',
    pacing: 'slow and contemplative',
    audioStyle: 'ambient electronic'
  };
}

// Apply all layers
const transformed = {
  originalTheme: $json.coreTheme,
  translatedTopic: translateTopic($json.coreTheme),
  targetFormat: modifyFormat($json.videoFormat),
  styleGuide: transformStyle($json),
  uniquenessScore: 0.95  // High differentiation
};

return { json: transformed };
```

### 4.2 Copyright-Safe Approach

**Validation Checklist** (n8n manual review or external API):

```javascript
// Copyright Safety Check
const safetyChecks = {
  noSpecificPeople: true,  // No identifiable individuals
  noProtectedMusic: true,  // Only generated audio
  noBrandLogos: true,      // No trademarked elements
  noDirectQuotes: true,    // No copied dialogue
  transformationDepth: 3,  // All three layers applied
  originalityScore: 95     // Plagiarism check result
};

// Only proceed if all checks pass
if (Object.values(safetyChecks).every(check => check === true || check >= 3)) {
  return { json: { approved: true, ...safetyChecks } };
} else {
  return { json: { approved: false, reason: 'Insufficient transformation' } };
}
```

### 4.3 Originality Verification

**Integration with Originality.ai**:

```javascript
// HTTP Request to plagiarism checker
Method: POST
URL: https://api.originality.ai/api/v1/scan/ai

Headers:
{
  "X-OAI-API-KEY": "{{$credentials.originalityApiKey}}",
  "Content-Type": "application/json"
}

Body:
{
  "content": "{{$json.videoScript}}",
  "aiModelVersion": "3.0",
  "storeScan": "false"
}

// Response includes:
// - AI detection score
// - Plagiarism percentage
// - Pass if plagiarism < 5%
```

---

## 5. n8n Workflow Architecture

### 5.1 Core Workflow Structure

**Master Workflow** (scheduled execution):

```
┌─────────────────────────────────────────────────────────────┐
│ CRON TRIGGER (Every 6 hours)                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [1] FETCH TRENDING VIDEOS                                   │
│ ├─ YouTube API (mostPopular)                                │
│ ├─ Apify TikTok Scraper                                     │
│ └─ Merge Results                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [2] CALCULATE TREND SCORES                                  │
│ └─ Function Node: engagement rate + velocity scoring        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [3] EXTRACT TOPICS (NLP)                                    │
│ └─ Code Node (Python/spaCy) or HTTP to Hugging Face        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [4] FILTER & DEDUPLICATE                                    │
│ ├─ Remove previously processed topics (DB lookup)           │
│ └─ Select top 3-5 trends                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [5] TRANSFORM TOPICS                                        │
│ └─ Apply 3-layer transformation framework                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [6] GENERATE AI PROMPTS                                     │
│ └─ Function Node: Create Veo 3.1 prompts with uniqueness   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [7] GENERATE VIDEOS (Veo 3.1)                              │
│ ├─ HTTP Request: Initiate generation                        │
│ ├─ Wait 30s loop                                            │
│ ├─ Poll operation status                                    │
│ └─ Extract video GCS URI                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [8] DOWNLOAD VIDEO FROM GCS                                 │
│ └─ HTTP Request: Download MP4 from Cloud Storage           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [9] QUALITY CONTROL                                         │
│ ├─ Check video file size and format                         │
│ ├─ Optional: Plagiarism check on metadata                   │
│ └─ Manual approval gate (optional)                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [10] PLATFORM-SPECIFIC FORMATTING                           │
│ ├─ IF YouTube: Keep 16:9, add metadata                      │
│ ├─ IF TikTok: Crop to 9:16 (ffmpeg)                        │
│ └─ IF Instagram: Crop to 9:16, max 90s                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [11] PUBLISH TO PLATFORMS                                   │
│ ├─ YouTube: videos.insert (OAuth 2.0)                       │
│ ├─ TikTok: Content Posting API (3-phase upload)            │
│ └─ Facebook/IG: Graph API (chunked upload)                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ [12] LOG RESULTS                                            │
│ ├─ Store in database (video ID, platform, timestamp)        │
│ ├─ Send success notification (Slack/email)                  │
│ └─ Update processed topics list                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Key n8n Nodes Configuration

**Cron Trigger Node**:
```
Mode: Every X hours
Expression: 0 */6 * * * (every 6 hours)
```

**HTTP Request Nodes**:
- Authentication: Store API keys in n8n Credentials
- Error handling: Set "Continue On Fail" = true
- Retry on fail: 3 attempts with 5s delay

**Function Nodes**:
- JavaScript for data transformation
- Access input: `$input.all()` or `$json`
- Return format: `{ json: {data} }`

**Code Nodes** (for Python/NLP):
- Language: Python
- Enable external libraries in n8n settings
- Install dependencies: `pip install spacy`

**Wait Node** (for Veo polling):
```
Wait: 30 seconds
Resume on: After time expires
```

**Loop Logic** (IF Node + Loop Back):
```
IF Node:
  Condition: {{$json.done}} === false
  True: Connect back to Wait Node
  False: Continue to Download
```

### 5.3 Error Handling Strategy

**Error Workflow** (separate workflow triggered by webhooks):

```javascript
// Main workflow: Set error trigger
// In each critical node:
Settings → On Error: Call Error Workflow

// Error Workflow structure:
[Webhook Trigger]
  → [Parse Error]
  → [Log to Database]
  → [Send Alert (Slack/Email)]
  → [Attempt Recovery if possible]
```

**Retry Logic Example**:

```javascript
// Function Node: Retry wrapper
const maxRetries = 3;
const retryCount = $json.retryCount || 0;

if ($json.error && retryCount < maxRetries) {
  return {
    json: {
      ...$json,
      retryCount: retryCount + 1,
      shouldRetry: true
    }
  };
} else if (retryCount >= maxRetries) {
  // Trigger error workflow
  return {
    json: {
      error: 'Max retries exceeded',
      originalData: $json
    }
  };
}
```

### 5.4 Monitoring & Logging

**Database Logging** (PostgreSQL/MySQL node):

```sql
-- Store execution logs
INSERT INTO video_generations (
  trend_topic,
  video_url,
  platform,
  status,
  veo_cost,
  created_at
) VALUES (
  '{{$json.coreTheme}}',
  '{{$json.gcsUri}}',
  '{{$json.platform}}',
  'success',
  {{$json.estimatedCost}},
  NOW()
);
```

**Slack Notifications**:

```javascript
// Slack Node configuration
Method: POST
URL: https://slack.com/api/chat.postMessage

Body:
{
  "channel": "#automation-alerts",
  "text": "✅ Video generated and published",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*New Video Published*\nTrend: {{$json.coreTheme}}\nPlatform: {{$json.platform}}\nCost: ${{$json.estimatedCost}}"
      }
    }
  ]
}
```

---

## 6. Multi-Platform Publishing

### 6.1 YouTube Upload Implementation

**n8n HTTP Request Node** (resumable upload):

```javascript
// Step 1: Metadata insertion
Method: POST
URL: https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status

Authentication: OAuth2 (configure in n8n credentials)

Headers:
{
  "Content-Type": "application/json",
  "X-Upload-Content-Type": "video/mp4"
}

Body:
{
  "snippet": {
    "title": "{{$json.generatedTitle}}",
    "description": "{{$json.description}}\n\n⚠️ This video was created using AI technology (Google Veo 3.1)",
    "tags": {{$json.hashtags}},
    "categoryId": "22"
  },
  "status": {
    "privacyStatus": "public",
    "selfDeclaredMadeForKids": false
  }
}

// Response includes 'Location' header with upload URL
// Step 2: Upload video binary to that URL
```

**YouTube Disclosure Compliance**:
```javascript
// MUST disclose AI-generated content
// Add to description AND use YouTube's disclosure toggle
// During upload via API, include in description
// Manually enable "Altered or synthetic content" toggle in YouTube Studio
```

### 6.2 TikTok Upload Implementation

**Three-Phase Process**:

**Phase 1: Query Creator Info** (mandatory):
```javascript
Method: POST
URL: https://open.tiktokapis.com/v2/post/publish/creator_info/query/

Headers:
{
  "Authorization": "Bearer {{$credentials.tiktokAccessToken}}",
  "Content-Type": "application/json"
}

// Returns: max_video_duration, privacy_level_options
```

**Phase 2: Initialize Upload**:
```javascript
Method: POST
URL: https://open.tiktokapis.com/v2/post/publish/video/init/

Body:
{
  "post_info": {
    "title": "{{$json.caption}} #ai #trending",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "disable_duet": false,
    "disable_comment": false,
    "disable_stitch": false,
    "brand_content_toggle": false,
    "is_aigc": true  // AI-generated content label
  },
  "source_info": {
    "source": "FILE_UPLOAD",
    "video_size": {{$json.fileSize}},
    "chunk_size": 10000000,
    "total_chunk_count": {{$json.chunkCount}}
  }
}

// Response: publish_id, upload_url
```

**Phase 3: Upload Video**:
```javascript
Method: PUT
URL: {{$json.uploadUrl}}  // From Phase 2 response

Headers:
{
  "Content-Type": "video/mp4",
  "Content-Length": "{{$json.fileSize}}",
  "Content-Range": "bytes 0-{{$json.fileSize-1}}/{{$json.fileSize}}"
}

Body: Binary video data
```

**Phase 4: Check Status**:
```javascript
Method: POST
URL: https://open.tiktokapis.com/v2/post/publish/status/fetch/

Body:
{
  "publish_id": "{{$json.publishId}}"
}

// Poll until status = "PUBLISH_COMPLETE"
```

**TikTok Rate Limits**:
- 6 requests per minute per user token
- ~15 posts per creator per 24 hours
- Implement delays between posts

### 6.3 Facebook/Instagram Upload

**Instagram Reels** (two-step process):

**Step 1: Create Media Container**:
```javascript
Method: POST
URL: https://graph.instagram.com/v20.0/{{$json.igUserId}}/media

Body:
{
  "media_type": "REELS",
  "video_url": "{{$json.publicVideoUrl}}",  // Must be publicly accessible
  "caption": "{{$json.caption}} #ai #trending",
  "access_token": "{{$credentials.instagramAccessToken}}"
}

// Response: creation_id
```

**Step 2: Publish Container**:
```javascript
Method: POST
URL: https://graph.instagram.com/v20.0/{{$json.igUserId}}/media_publish

Body:
{
  "creation_id": "{{$json.creationId}}",
  "access_token": "{{$credentials.instagramAccessToken}}"
}

// Response: published post_id
```

**Facebook Page Video**:

```javascript
// Three-phase chunked upload (similar to TikTok)
// Phase 1: Start
POST https://graph-video.facebook.com/{{$json.pageId}}/videos
  ?upload_phase=start
  &file_size={{$json.fileSize}}
  &access_token={{$credentials.pageAccessToken}}

// Phase 2: Transfer (chunks)
POST https://graph-video.facebook.com/{{$json.pageId}}/videos
  ?upload_phase=transfer
  &start_offset={{$json.offset}}
  &upload_session_id={{$json.sessionId}}
  &access_token={{$credentials.pageAccessToken}}
  -F video_file_chunk=@chunk.mp4

// Phase 3: Finish
POST https://graph-video.facebook.com/{{$json.pageId}}/videos
  ?upload_phase=finish
  &upload_session_id={{$json.sessionId}}
  &title={{$json.title}}
  &description="Created with AI"
  &access_token={{$credentials.pageAccessToken}}
```

### 6.4 Video Format Conversion

**ffmpeg Integration** (n8n Execute Command node):

```bash
# Convert to TikTok format (9:16)
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k -ar 48000 \
  -r 30 -t 60 \
  -movflags +faststart \
  output_tiktok.mp4

# YouTube format (16:9, keep as-is usually)
ffmpeg -i input.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k -ar 48000 \
  -vf scale=1920:1080 \
  -movflags +faststart \
  output_youtube.mp4

# Instagram Reels (9:16, max 90s)
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -t 90 \
  -movflags +faststart \
  output_instagram.mp4
```

**n8n Execute Command Node**:
```
Command: ffmpeg
Arguments: [See above commands as array]
```

---

## 7. Complete Workflow Blueprint

### 7.1 Workflow Variables & Configuration

**Environment Variables** (set in n8n settings):

```javascript
YOUTUBE_API_KEY=your_key
GOOGLE_PROJECT_ID=your_project
GOOGLE_CLOUD_BUCKET=your-bucket
APIFY_API_TOKEN=your_token
TIKTOK_CLIENT_KEY=your_key
TIKTOK_CLIENT_SECRET=your_secret
FACEBOOK_APP_ID=your_app_id
INSTAGRAM_USER_ID=your_ig_user_id
OPENAI_API_KEY=your_key  // For caption generation
```

**Workflow Settings**:
```javascript
const CONFIG = {
  pollInterval: 360,  // 6 hours between trend checks
  maxVideosPerRun: 3,  // Generate 3 videos per execution
  veoModel: 'veo-3.1-fast-generate-preview',  // Cost optimization
  targetPlatforms: ['youtube', 'tiktok', 'instagram'],
  budgetPerVideo: 1.20,  // Using fast model
  monthlyBudget: 200,  // ~166 videos per month
  enableManualReview: false,  // Set true for quality control
  minEngagementRate: 2.0,  // 2% minimum to process trend
  minViews: 100000  // 100K views minimum
};
```

### 7.2 Complete n8n JSON Workflow

**Simplified workflow export** (partial, showing structure):

```json
{
  "name": "Autonomous Video Generation Pipeline",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": "0 */6 * * *"
      }
    },
    {
      "name": "Fetch YouTube Trending",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://www.googleapis.com/youtube/v3/videos",
        "qs": {
          "part": "snippet,statistics",
          "chart": "mostPopular",
          "maxResults": 50
        }
      }
    },
    {
      "name": "Calculate Trend Scores",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// See section 2.4"
      }
    },
    {
      "name": "Generate Veo Prompt",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// See section 3.5"
      }
    },
    {
      "name": "Call Veo 3.1 API",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://us-central1-aiplatform.googleapis.com/v1/..."
      }
    },
    {
      "name": "Wait for Video",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 30
      }
    },
    {
      "name": "Upload to YouTube",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://www.googleapis.com/upload/youtube/v3/videos"
      }
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [[{"node": "Fetch YouTube Trending"}]]
    }
    // ... etc
  }
}
```

**Full workflow**: Too large to include here. Key principles:
1. Sequential execution with clear data flow
2. Error handling at each critical step
3. Logging at start/end of major phases
4. Conditional branches for multi-platform publishing

### 7.3 Deployment Checklist

**Pre-Deployment**:
- [ ] n8n instance running (self-hosted or cloud)
- [ ] All API credentials configured
- [ ] Google Cloud project setup complete
- [ ] Cloud Storage bucket created
- [ ] Test Veo 3.1 generation manually
- [ ] Test each platform upload individually
- [ ] Database configured for logging
- [ ] Monitoring tools connected

**Testing Phase**:
- [ ] Run workflow manually with single trend
- [ ] Verify video generation quality
- [ ] Test all platform uploads
- [ ] Validate AI disclosure labels appear
- [ ] Check cost tracking accuracy
- [ ] Test error handling (force failures)
- [ ] Verify notifications work

**Production Launch**:
- [ ] Enable cron schedule
- [ ] Set budget alerts (Google Cloud + platforms)
- [ ] Monitor first 24 hours closely
- [ ] Review generated content quality
- [ ] Check engagement metrics
- [ ] Adjust trend scoring if needed
- [ ] Fine-tune prompts based on output

### 7.4 Maintenance Strategy

**Daily**:
- Check workflow execution logs
- Review generated video quality
- Monitor API costs

**Weekly**:
- Analyze engagement metrics per platform
- Adjust trend scoring thresholds
- Update prompt templates based on performance
- Review and remove low-performing content

**Monthly**:
- Cost analysis and budget optimization
- Prompt engineering refinements
- API quota reviews
- Platform policy updates check

---

## 8. Advanced Optimizations

### 8.1 Batch Processing

**Parallel Video Generation**:

```javascript
// Split trends into batches
// Generate 3 videos simultaneously (respect Veo rate limits)

const trends = $input.all();
const batchSize = 3;

// Process in parallel using n8n SplitInBatches node
// Configure: Batch Size = 3, Keep Input Data = Yes

// Then use Wait node + parallel HTTP requests
```

**Cost Optimization**:
```javascript
// Adaptive model selection
function selectModel(trendScore, timeOfDay) {
  // Use fast model during high-volume periods
  if (trendScore < 50000 || timeOfDay > 18) {
    return 'veo-3.1-fast-generate-preview';
  }
  // Reserve standard model for prime content
  return 'veo-3.1-generate-preview';
}
```

### 8.2 Quality Gating

**Manual Review Node** (optional):

```javascript
// Pause workflow for human approval
{
  "name": "Approval Gate",
  "type": "n8n-nodes-base.wait",
  "parameters": {
    "resume": "webhook",
    "options": {
      "webhookSuffix": "approve/{{$json.videoId}}"
    }
  }
}

// Send notification with video preview + approve/reject buttons
// Continue only after manual approval
```

### 8.3 A/B Testing

**Caption Variations**:

```javascript
// Generate multiple captions with OpenAI
// Test which performs better

const captionVariants = [
  '{{$json.coreTheme}} explained simply 🧠',
  'The truth about {{$json.coreTheme}} 👀',
  'Why {{$json.coreTheme}} is trending right now 🔥'
];

// Rotate between variants
// Track performance in database
// Optimize based on engagement data
```

---

## 9. Compliance & Safety

### 9.1 Mandatory Disclosures

**Platform-Specific Requirements**:

| Platform | Requirement | Implementation |
|----------|-------------|----------------|
| YouTube | Enable "Altered or synthetic content" toggle | Add to description + manual toggle in Studio |
| TikTok | Set `is_aigc: true` in API call | Included in post_info parameter |
| Instagram | Add caption mention | Include "Created with AI" in caption |
| Facebook | C2PA metadata auto-detection | Ensure Veo output retains metadata |

**Template Disclosure Text**:
```
⚠️ AI-Generated Content Disclosure:
This video was created using Google Veo 3.1 AI technology.
Content is inspired by trending topics but represents an original creation.
```

### 9.2 Copyright Safety Measures

**Pre-Publication Checklist**:
```javascript
const copyrightChecks = {
  noRealPeople: true,  // Veo prompts avoid identifiable people
  noProtectedMusic: true,  // Use only Veo-generated audio
  noBrands: true,  // Negative prompts exclude logos
  transformationVerified: true,  // 3-layer check passed
  originalityScore: 95  // <5% similarity to any source
};

// Only publish if all checks pass
```

### 9.3 Platform Policies Compliance

**Automation Best Practices**:
- Use official APIs only (no scraping for posting)
- Respect rate limits strictly
- Don't post identical content across accounts
- Vary posting times and content
- Enable authentic engagement (allow comments)
- Respond to user feedback
- Monitor for community guideline violations

---

## 10. Cost Analysis

### 10.1 Monthly Cost Breakdown

**Scenario: 100 videos/month**

| Component | Cost | Notes |
|-----------|------|-------|
| Veo 3.1 Fast (8s, audio) | $120 | 100 × $1.20 |
| Apify (TikTok trends) | $49 | Basic plan |
| YouTube API | $0 | Within free quota |
| TikTok API | $0 | Free after audit approval |
| Facebook/Instagram API | $0 | Free |
| Google Cloud Storage | $2 | ~20GB video storage |
| n8n hosting | $0-20 | Self-hosted or cloud basic |
| OpenAI (captions) | $10 | Optional, GPT-4o mini |
| **TOTAL** | **~$181-201/month** | For 100 videos |

**Per-Video Cost**: ~$1.81-2.01

**Scaling**:
- 300 videos/month: ~$500/month
- 1000 videos/month: ~$1,600/month

### 10.2 ROI Considerations

**Break-Even Analysis**:
- Assumes monetization via ads or sponsorships
- YouTube: $2-5 RPM (revenue per 1000 views)
- TikTok Creator Fund: $0.02-0.04 per 1000 views
- Instagram: Brand deals, typically $100-500 per sponsored post

**Example ROI**:
- 100 videos generating average 50K views each = 5M views/month
- YouTube revenue: 5M × $3 CPM = $15,000/month
- Cost: $200/month
- Net: $14,800/month (7400% ROI)

*(Note: Actual results vary greatly; this is optimistic scenario)*

---

## 11. Troubleshooting Guide

### Common Issues

**Issue 1: Veo 3.1 Generation Times Out**
- **Cause**: Processing takes >5 minutes
- **Solution**: Increase wait time to 10 minutes, check operation status more frequently

**Issue 2: YouTube Quota Exceeded**
- **Cause**: Too many API calls
- **Solution**: Request quota increase, reduce polling frequency, cache trend data

**Issue 3: TikTok Rate Limit (429 error)**
- **Cause**: >6 requests/minute
- **Solution**: Add delays between posts, implement queue system

**Issue 4: Videos Look Too Similar to Trends**
- **Cause**: Insufficient transformation
- **Solution**: Strengthen negative prompts, add more uniqueness constraints, increase abstraction level

**Issue 5: Platform Removes Content**
- **Cause**: Spam detection or policy violation
- **Solution**: Reduce posting frequency, add more variation, ensure disclosures are present

---

## 12. Next Steps & Scaling

### Immediate Implementation (Week 1-2)
1. Set up n8n instance
2. Configure all API credentials
3. Build trend detection module
4. Test Veo 3.1 generation manually
5. Create basic workflow (trend → video → YouTube only)

### Expansion (Week 3-4)
1. Add TikTok and Instagram publishing
2. Implement transformation layers
3. Add quality control gates
4. Set up monitoring dashboards
5. Enable cron scheduling

### Optimization (Month 2)
1. Refine prompt engineering based on results
2. Implement A/B testing for captions
3. Add advanced NLP for topic extraction
4. Optimize costs (model selection logic)
5. Scale to higher volume

### Advanced Features (Month 3+)
1. Multi-language support
2. Custom music generation integration
3. Thumbnail generation (Midjourney/DALL-E)
4. Advanced analytics dashboard
5. Automatic trend prediction (ML model)

---

## Resources & Documentation

### Essential Documentation
- **n8n**: https://docs.n8n.io
- **Vertex AI Veo**: https://cloud.google.com/vertex-ai/generative-ai/docs/video/overview
- **YouTube Data API**: https://developers.google.com/youtube/v3
- **TikTok Content Posting API**: https://developers.tiktok.com/doc/content-posting-api-get-started
- **Meta Graph API**: https://developers.facebook.com/docs/graph-api
- **Apify**: https://docs.apify.com

### Code Examples
- **n8n Veo Template**: https://n8n.io/workflows/5228
- **Python YouTube Upload**: https://github.com/youtube/api-samples
- **TikTok API Examples**: https://github.com/tiktok-for-developers

### Community Support
- **n8n Community**: https://community.n8n.io
- **Google Cloud Discord**: AI/ML channels
- **Reddit**: r/n8n, r/automation

---

## Conclusion

This comprehensive guide provides everything needed to build a fully autonomous video automation system. The workflow leverages cutting-edge AI (Veo 3.1) while maintaining copyright compliance and platform policy adherence.

**Key Success Factors**:
1. **Robust trend detection** with engagement filtering
2. **Strong transformation framework** (3-layer approach)
3. **Quality AI prompting** with uniqueness constraints
4. **Reliable n8n architecture** with error handling
5. **Multi-platform optimization** with format adaptation
6. **Compliance-first approach** with mandatory disclosures

**Expected Timeline**:
- Setup: 1-2 weeks
- Testing: 1 week
- Full deployment: Month 1
- Optimization: Ongoing

**Critical Warnings**:
- Monitor costs closely (Veo charges per second)
- Never skip AI content disclosures
- Respect platform rate limits strictly
- Continuously verify content originality
- Stay updated on platform policy changes

With proper implementation, this system can generate 100+ unique, trend-inspired videos monthly at ~$2/video cost, with minimal manual intervention once established.

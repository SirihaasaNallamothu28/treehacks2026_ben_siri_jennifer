# User Interests Implementation

## Overview

The `get_medical_interests_and_technical_interests()` function retrieves user interests for paper search and video generation.

## How It Works

### Current Implementation (File-Based)

The function reads from `backend/user_interests.json`:

```json
{
  "medical_interests": "cancer treatment, immunotherapy, oncology research",
  "technical_interests": "machine learning, deep learning, computer vision, neural networks"
}
```

### Fallback Behavior

If `user_interests.json` doesn't exist, the function will:
1. Prompt the user to enter their interests via console input
2. Save the entered interests to `user_interests.json` for future use

### Return Value

Returns a tuple of two strings:
```python
medical_interests, technical_interests = get_medical_interests_and_technical_interests()
```

## Integration Flow

```
1. get_medical_interests_and_technical_interests()
   ↓ (reads user_interests.json)

2. get_best_paper_json()
   ↓ (passes interests to search_for_papers)

3. search_for_papers(medical_interests, technical_interests)
   ↓ (uses test_synapsis agent to select best paper)

4. Returns paper JSON with all required fields:
   - title
   - authors
   - journal
   - publication_year
   - abstract
   - pmid
   - doi

5. generate_video_from_paper()
   ↓ (uses paper JSON to create video)
```

## Testing

Run the integration test to verify everything works:

```bash
cd backend
python test_interests_standalone.py
```

## Future: API Integration

When the backend API server is implemented, the flow will be:

### Frontend → Backend API

The frontend (React) currently saves interests to localStorage:
```typescript
// frontend/src/app/pages/Home.tsx
const userProfile = `User interested in healthcare: user interests in ${selectedInterests.join(", ")}.
User strengths in ${selectedStrengths.join(", ")}.`;
localStorage.setItem("userProfile", userProfile);
```

### Planned API Endpoint

Create a Flask/FastAPI endpoint to receive interests:

```python
# Future: backend/api/server.py
@app.post("/api/generate-video")
async def generate_video(request):
    medical_interests = request.json.get("medical_interests")
    technical_interests = request.json.get("technical_interests")

    # Save to user_interests.json or pass directly
    # Then call generate_video_from_paper()
```

### Frontend Update

Update the frontend to send interests to the API:

```typescript
// frontend/src/app/services/api.ts
export async function generateVideo(
  medicalInterests: string[],
  technicalInterests: string[]
): Promise<VideoJob> {
  const response = await fetch(`${API_BASE_URL}/api/generate-video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      medical_interests: medicalInterests.join(", "),
      technical_interests: technicalInterests.join(", "),
    }),
  });
  return response.json();
}
```

## Manual Usage

To update interests manually, edit `backend/user_interests.json`:

```json
{
  "medical_interests": "your medical interests here",
  "technical_interests": "your technical interests here"
}
```

Or delete the file to be prompted for new interests on next run.

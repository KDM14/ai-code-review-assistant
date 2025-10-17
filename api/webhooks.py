from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import hmac
import hashlib
import json
import os
from app.services.ai_reviewer import AIReviewer
from app.services.github_service import GitHubService
@router.post("/webhook/test")
async def test_webhook():
    print("🎯 TEST WEBHOOK HIT! Server is working!")
    return {"status": "test_success", "message": "Webhook server is working!"}


async def process_pull_request(payload: dict):
    """Process pull request webhook with AI review"""
    print("🎯 DEBUG: Webhook processor started!")
    
    try:
        print("🎯 DEBUG: Attempting to import services...")
        from app.services.ai_reviewer import AIReviewer
        from app.services.github_service import GitHubService
        print("🎯 DEBUG: Services imported successfully!")
        
        # ... rest of your existing code
router = APIRouter()
ai_reviewer = AIReviewer()
github_service = GitHubService()

def verify_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that the webhook came from GitHub"""
    if not signature_header:
        return False
    
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
    hash_object = hmac.new(secret, msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

@router.post("/webhook/github")
async def handle_github_webhook(request: Request, background_tasks: BackgroundTasks):
    # Get GitHub signature
    signature = request.headers.get("x-hub-signature-256")
    
    # Read request body
    body = await request.body()
    
    # Verify webhook signature
    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Parse JSON payload
    try:
        payload = json.loads(body)
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Get event type
    event_type = request.headers.get("x-github-event")
    
    print(f"📨 Received GitHub event: {event_type}")
    
    # Handle pull request events
    if event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            # Process in background to avoid timeout
            background_tasks.add_task(process_pull_request, payload)
            return {"status": "processing", "event": "pull_request", "action": action}
    
    return {"status": "ignored", "event": event_type}

async def process_pull_request(payload: dict):
    """Process pull request webhook with AI review"""
    pr_data = payload["pull_request"]
    repo = payload["repository"]
    
    pr_number = pr_data["number"]
    repo_full_name = repo["full_name"]
    repo_owner = repo["owner"]["login"]
    repo_name = repo["name"]
    pr_title = pr_data["title"]
    
    print(f"🔍 Analyzing PR #{pr_number}: {pr_title} in {repo_full_name}")
    
    # Get files changed in PR
    files_changed = github_service.get_pr_files(repo_owner, repo_name, pr_number)
    
    if not files_changed:
        print("❌ No files to review")
        return
    
    # Get AI review suggestions
    suggestions = ai_reviewer.review_code_changes(files_changed, pr_data)
    
    print(f"💡 AI generated {len(suggestions)} suggestions")
    
    # Post comments to GitHub
    successful_comments = 0
    for suggestion in suggestions[:3]:  # Limit to 3 comments to avoid spam
        if github_service.create_review_comment(repo_owner, repo_name, pr_number, suggestion):
            successful_comments += 1
    
    # Post summary
    github_service.post_review_summary(repo_owner, repo_name, pr_number, suggestions)
    
    print(f"🎉 Successfully posted {successful_comments} comments to PR #{pr_number}")
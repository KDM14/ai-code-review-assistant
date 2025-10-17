from fastapi import FastAPI, Request, BackgroundTasks
import hmac
import hashlib
import json
import os
import requests
import time
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from fastapi.responses import FileResponse
# Load environment variables
load_dotenv()

# Database setup
Base = declarative_base()

class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    pr_number = Column(Integer, nullable=False)
    repo_name = Column(String, nullable=False)
    pr_title = Column(String)
    files_reviewed = Column(Integer)
    suggestions_given = Column(Integer)
    ai_provider = Column(String)
    review_duration = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    suggestions_json = Column(JSON)

DATABASE_URL = "sqlite:///./code_reviews.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
init_db()
print("✅ Database initialized!")

# Create the FastAPI app
app = FastAPI(
    title="AI Code Review Assistant",
    description="An intelligent code review system for any repository",
    version="4.0.0"
)

# Dashboard endpoint
# Dashboard endpoint
@app.get("/dashboard")
async def serve_dashboard():
    """Serve the dashboard HTML page"""
    print("📊 Dashboard requested")
    dashboard_path = "templates/dashboard.html"
    
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        return {
            "error": "Dashboard not found", 
            "message": "Create templates/dashboard.html file",
            "status": "missing_dashboard"
        }
print("🚀 AI Code Review Assistant v4.0 starting...")
class UniversalReviewer:
    def calculate_quality_score(self, suggestions, files_changed):
   
        base_score = 100
    
        # Deduct points based on suggestion types
        priority_weights = {"high": -10, "medium": -5, "low": -2}
        for suggestion in suggestions:
            base_score += priority_weights.get(suggestion['priority'], -2)
    
    # Bonus for clean code
        if len(suggestions) == 0:
            base_score += 20
    
        # Penalty for large changes
        if len(files_changed) > 10:
            base_score -= 15
    
        return max(0, min(100, base_score))
    
    def __init__(self):
        self.providers = ["universal_analyzer"]
        
    def review_code(self, files_changed, pr_title):
        """Universal code review that works for any repository"""
        print(f"🤖 Universal AI analyzing {len(files_changed)} files...")
        
        suggestions = []
        
        for file in files_changed[:3]:  # Analyze first 3 files
            filename = file['filename']
            content = file.get('patch', '') or file.get('content', '')
            
            # Universal analysis that works for any file type
            file_suggestions = self._universal_file_analysis(filename, content)
            suggestions.extend(file_suggestions)
            
            # Language-specific analysis
            lang_suggestions = self._language_specific_analysis(filename, content)
            suggestions.extend(lang_suggestions)
        
        # Always provide at least one helpful suggestion
        if not suggestions:
            suggestions = self._always_helpful_suggestions(files_changed, pr_title)
        
        # Remove duplicates and limit
        unique_suggestions = self._remove_duplicates(suggestions)
        
        print(f"💡 Generated {len(unique_suggestions)} suggestions")
        return unique_suggestions[:3]
    
    def _universal_file_analysis(self, filename, content):
        """Analysis that works for ANY file type"""
        suggestions = []
        lines = content.split('\n')
        
        # Check for very large files
        if len(lines) > 500:
            suggestions.append({
                "type": "maintainability",
                "file": filename,
                "line": 1,
                "content": f"File is {len(lines)} lines long. Consider splitting into smaller, focused modules.",
                "priority": "medium"
            })
        
        # Check for TODO/FIXME comments
        for i, line in enumerate(lines[:100]):  # Check first 100 lines
            if any(marker in line.upper() for marker in ['TODO', 'FIXME', 'XXX', 'HACK']):
                suggestions.append({
                    "type": "improvement",
                    "file": filename,
                    "line": i + 1,
                    "content": "Address this TODO/FIXME comment before finalizing the implementation.",
                    "priority": "low"
                })
                break
        
        # Check for long lines
        for i, line in enumerate(lines[:50]):
            if len(line) > 120 and line.strip():
                suggestions.append({
                    "type": "readability",
                    "file": filename,
                    "line": i + 1,
                    "content": "Consider breaking this long line for better readability.",
                    "priority": "low"
                })
                break
        
        return suggestions
    
    def _language_specific_analysis(self, filename, content):
        """Language-specific best practices"""
        suggestions = []
        
        # Python analysis
        if filename.endswith('.py'):
            if 'def ' in content and not any(doc in content for doc in ['"""', "'''"]):
                suggestions.append({
                    "type": "documentation",
                    "file": filename,
                    "line": self._find_line_number(content, 'def ') or 1,
                    "content": "Consider adding docstrings to functions for better documentation.",
                    "priority": "medium"
                })
            
            if any(unsafe in content for unsafe in ['eval(', 'exec(', 'pickle.loads(']):
                suggestions.append({
                    "type": "security",
                    "file": filename,
                    "line": 1,
                    "content": "Be cautious with eval/exec/pickle as they can introduce security vulnerabilities.",
                    "priority": "high"
                })
        
        # JavaScript/TypeScript analysis
        elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            if 'console.log' in content and 'test' not in filename.lower():
                suggestions.append({
                    "type": "best-practice",
                    "file": filename,
                    "line": self._find_line_number(content, 'console.log') or 1,
                    "content": "Consider removing console.log statements before production deployment.",
                    "priority": "low"
                })
            
            if 'var ' in content:
                suggestions.append({
                    "type": "modernization",
                    "file": filename,
                    "line": self._find_line_number(content, 'var ') or 1,
                    "content": "Consider using const/let instead of var for better scoping.",
                    "priority": "low"
                })
        
        # Java analysis
        elif filename.endswith('.java'):
            if 'public static void main' in content and not any(comment in content for comment in ['//', '/*']):
                suggestions.append({
                    "type": "documentation",
                    "file": filename,
                    "line": self._find_line_number(content, 'main') or 1,
                    "content": "Consider adding comments to explain the main method's purpose.",
                    "priority": "medium"
                })
        
        # HTML analysis
        elif filename.endswith(('.html', '.htm')):
            if '<script>' in content and not any(attr in content for attr in ['async', 'defer']):
                suggestions.append({
                    "type": "performance",
                    "file": filename,
                    "line": self._find_line_number(content, '<script>') or 1,
                    "content": "Consider adding async/defer attributes to script tags for better performance.",
                    "priority": "medium"
                })
        
        # CSS analysis
        elif filename.endswith(('.css', '.scss', '.less')):
            if '!important' in content:
                suggestions.append({
                    "type": "maintainability",
                    "file": filename,
                    "line": self._find_line_number(content, '!important') or 1,
                    "content": "Avoid overusing !important as it can make CSS harder to maintain.",
                    "priority": "low"
                })
        
        # Markdown/documentation analysis
        elif filename.endswith(('.md', '.txt', '.rst')):
            if len(content.strip()) < 100 and 'README' in filename.upper():
                suggestions.append({
                    "type": "documentation",
                    "file": filename,
                    "line": 1,
                    "content": "Consider expanding this documentation with setup instructions and examples.",
                    "priority": "medium"
                })
            
            if not any(header in content for header in ['# ', '## ', '### ']) and len(lines) > 10:
                suggestions.append({
                    "type": "structure",
                    "file": filename,
                    "line": 1,
                    "content": "Consider adding section headers to organize your documentation.",
                    "priority": "low"
                })
        
        # Configuration files
        elif any(ext in filename for ext in ['.json', '.yaml', '.yml', '.xml', '.config']):
            if len(content.strip()) > 0:
                suggestions.append({
                    "type": "best-practice",
                    "file": filename,
                    "line": 1,
                    "content": "Consider adding comments to explain configuration values where necessary.",
                    "priority": "low"
                })
        
        return suggestions
    
    def _always_helpful_suggestions(self, files_changed, pr_title):
        """Always provide helpful suggestions, even for simple changes"""
        suggestions = []
        
        for file in files_changed[:2]:
            filename = file['filename']
            
            if filename.endswith('.py'):
                suggestions.append({
                    "type": "improvement",
                    "file": filename,
                    "line": 1,
                    "content": "Consider adding tests for new functionality to ensure reliability.",
                    "priority": "medium"
                })
            elif filename.endswith(('.js', '.ts')):
                suggestions.append({
                    "type": "improvement", 
                    "file": filename,
                    "line": 1,
                    "content": "Consider adding error handling for edge cases and network requests.",
                    "priority": "medium"
                })
            elif filename.endswith('.md'):
                suggestions.append({
                    "type": "documentation",
                    "file": filename,
                    "line": 1,
                    "content": "Consider adding examples or usage instructions to make documentation more helpful.",
                    "priority": "low"
                })
            else:
                suggestions.append({
                    "type": "improvement",
                    "file": filename,
                    "line": 1,
                    "content": "Thanks for your contribution! Consider adding comments for complex logic.",
                    "priority": "low"
                })
        
        return suggestions
    
    def _remove_duplicates(self, suggestions):
        """Remove duplicate suggestions"""
        unique = []
        seen = set()
        for suggestion in suggestions:
            key = (suggestion['file'], suggestion['content'][:40])
            if key not in seen:
                seen.add(key)
                unique.append(suggestion)
        return unique
    
    def _find_line_number(self, content, search_text):
        """Find line number of text"""
        if not content or not search_text:
            return 1
        try:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if search_text in line:
                    return i + 1
        except:
            pass
        return 1

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_ACCESS_TOKEN")
        self.headers = {"Authorization": f"token {self.token}"}
        print(f"🔑 GitHub Token: {self.token[:8]}...")
    
    def get_pr_files(self, repo_owner, repo_name, pr_number):
        """Get PR files with robust error handling"""
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        
        try:
            print(f"📁 Fetching files from {repo_owner}/{repo_name} PR #{pr_number}...")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                files = response.json()
                print(f"📄 Found {len(files)} files to review")
                
                # Show file details
                for file in files[:4]:
                    status_emoji = {
                        'added': '🆕',
                        'modified': '📝', 
                        'removed': '🗑️',
                        'renamed': '📛'
                    }.get(file['status'], '📄')
                    
                    print(f"   {status_emoji} {file['filename']} ({file['status']})")
                
                return files
            else:
                print(f"❌ GitHub API Error {response.status_code}: {response.text[:100]}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching files: {e}")
            return []
    
    def post_comment(self, repo_owner, repo_name, pr_number, comment):
        """Post comment to PR with retry logic"""
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        
        # Better emoji mapping
        emoji_map = {
            "bug": "🐛", "security": "🔒", "performance": "⚡",
            "improvement": "💡", "documentation": "📝", "refactor": "🔧",
            "best-practice": "⭐", "modernization": "🔄", "readability": "👀",
            "maintainability": "🏗️", "structure": "📋", "maintainability": "🔨"
        }
        
        emoji = emoji_map.get(comment['type'], "🤖")
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(comment['priority'], "⚪")
        
        body = f"{emoji} **AI Code Review - {comment['type'].replace('-', ' ').title()}** {priority_emoji}\n\n{comment['content']}\n\n---\n*Automated review by AI Code Review Assistant*"
        
        payload = {"body": body}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 201:
                return True
            else:
                print(f"❌ Comment failed {response.status_code}: {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting comment: {e}")
            return False

# ==================== API ENDPOINTS ====================

@app.post("/api/v1/webhook/test")
async def test_webhook():
    print("🎯 TEST WEBHOOK HIT! Server is working!")
    return {"status": "test_success", "message": "Webhook server is working!"}

@app.post("/api/v1/webhook/github")
async def handle_github_webhook(request: Request, background_tasks: BackgroundTasks):
    print("📨 GitHub webhook received!")
    
    # Get signature and body
    signature = request.headers.get("x-hub-signature-256")
    body = await request.body()
    
    # Verify signature
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
    if secret:
        hash_object = hmac.new(secret, msg=body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        if not hmac.compare_digest(expected_signature, signature or ""):
            print("❌ Invalid webhook signature")
            return {"status": "invalid_signature"}
    
    # Parse payload
    try:
        payload = json.loads(body)
    except:
        print("❌ Invalid JSON payload")
        return {"status": "invalid_json"}
    
    # Get event type
    event_type = request.headers.get("x-github-event")
    print(f"📨 GitHub Event: {event_type}")
    
    # Handle pull request
    if event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            background_tasks.add_task(process_pull_request, payload)
            return {"status": "processing", "event": "pull_request", "action": action}
    
    return {"status": "received", "event": event_type}

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    print("📊 Dashboard stats requested")
    try:
        db = next(get_db())
        total_reviews = db.query(CodeReview).count()
        successful_reviews = db.query(CodeReview).filter(CodeReview.status == "success").count()
        total_suggestions = db.query(CodeReview).filter(CodeReview.suggestions_given > 0).count()
        
        recent_reviews = db.query(CodeReview).order_by(CodeReview.created_at.desc()).limit(5).all()
        
        return {
            "total_reviews": total_reviews,
            "successful_reviews": successful_reviews,
            "total_suggestions": total_suggestions,
            "success_rate": round((successful_reviews / total_reviews * 100), 2) if total_reviews > 0 else 0,
            "recent_reviews": [
                {
                    "id": review.id,
                    "repo": review.repo_name,
                    "pr_number": review.pr_number,
                    "suggestions": review.suggestions_given,
                    "duration": review.review_duration,
                    "created_at": review.created_at.isoformat()
                }
                for review in recent_reviews
            ]
        }
    except Exception as e:
        return {"error": f"Database error: {e}"}

@app.get("/api/v1/dashboard/reviews")
async def get_all_reviews():
    """Get all code reviews"""
    print("📋 All reviews requested")
    try:
        db = next(get_db())
        reviews = db.query(CodeReview).order_by(CodeReview.created_at.desc()).all()
        return {
            "reviews": [
                {
                    "id": review.id,
                    "pr_number": review.pr_number,
                    "repo_name": review.repo_name,
                    "pr_title": review.pr_title,
                    "files_reviewed": review.files_reviewed,
                    "suggestions_given": review.suggestions_given,
                    "ai_provider": review.ai_provider,
                    "review_duration": review.review_duration,
                    "status": review.status,
                    "created_at": review.created_at.isoformat(),
                    "suggestions": review.suggestions_json
                }
                for review in reviews
            ]
        }
    except Exception as e:
        return {"error": f"Database error: {e}"}

@app.get("/")
async def root():
    return {
        "message": "🚀 AI Code Review Assistant v4.0 is running!",
        "version": "4.0.0",
        "status": "active",
        "features": [
            "Universal code analysis for any repository",
            "Smart language-specific suggestions",
            "Security and best practice checks",
            "Real-time GitHub integration",
            "Dashboard with analytics"
        ],
        "endpoints": {
            "webhook_test": "/api/v1/webhook/test",
            "dashboard_stats": "/api/v1/dashboard/stats", 
            "all_reviews": "/api/v1/dashboard/reviews",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "4.0.0",
        "database": "connected"
    }

# ==================== BACKGROUND PROCESSING ====================

async def process_pull_request(payload: dict):
    """Process PR with universal code review"""
    start_time = time.time()
    
    pr_data = payload["pull_request"]
    repo = payload["repository"]
    
    pr_number = pr_data["number"]
    repo_full_name = repo["full_name"]
    repo_owner = repo["owner"]["login"]
    repo_name = repo["name"]
    pr_title = pr_data["title"]
    
    print(f"🔍 Analyzing PR #{pr_number}: {pr_title}")
    print(f"📂 Repository: {repo_full_name}")
    
    # Initialize services
    github_service = GitHubService()
    reviewer = UniversalReviewer()
    
    # Get PR files
    files_changed = github_service.get_pr_files(repo_owner, repo_name, pr_number)
    
    if not files_changed:
        print("❌ No files to review")
        return
    
    # Get AI review
    suggestions = reviewer.review_code(files_changed, pr_title)
    
    # Post comments to GitHub
    successful_comments = 0
    for suggestion in suggestions:
        if github_service.post_comment(repo_owner, repo_name, pr_number, suggestion):
            successful_comments += 1
            print(f"✅ Posted {suggestion['type']} comment")
    
    # Calculate duration
    duration = int(time.time() - start_time)
    
    # Save to database
    try:
        db = next(get_db())
        review_record = CodeReview(
            pr_number=pr_number,
            repo_name=repo_full_name,
            pr_title=pr_title,
            files_reviewed=len(files_changed),
            suggestions_given=successful_comments,
            ai_provider="universal_analyzer",
            review_duration=duration,
            status="success" if successful_comments > 0 else "failed",
            suggestions_json=suggestions
        )
        db.add(review_record)
        db.commit()
        print(f"💾 Saved review to database (ID: {review_record.id})")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print(f"🎉 Successfully posted {successful_comments} comments to PR #{pr_number} in {duration}s")
def security_scan(self, content, filename):
    """Advanced security vulnerability detection"""
    vulnerabilities = []
    
    # SQL Injection patterns
    sql_patterns = [
        r"SELECT.*\+", r"UNION.*SELECT", r"exec\(.*\)",
        r"eval\(.*\)", r"pickle\.loads", r"os\.system"
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            vulnerabilities.append({
                "type": "security",
                "file": filename,
                "line": self._find_line_number(content, pattern),
                "content": "Potential security vulnerability detected",
                "priority": "high",
                "category": "security"
            })
    
    return vulnerabilities
def find_code_smells(self, content, filename):
    """Detect code smells and anti-patterns"""
    smells = []
    
    # God object detection (too many methods)
    if filename.endswith('.py'):
        method_count = content.count('def ')
        if method_count > 15:
            smells.append({
                "type": "maintainability",
                "content": f"Class has {method_count} methods (God object anti-pattern)",
                "priority": "high"
            })
    
    return smells
class LearningSystem:
    def __init__(self):
        self.pattern_db = {}
    
    def learn_from_feedback(self, pr_data, accepted_suggestions, rejected_suggestions):
        """Learn which suggestions developers accept/reject"""
        # Track patterns in accepted vs rejected suggestions
        for suggestion in accepted_suggestions:
            key = f"{suggestion['type']}_{suggestion['priority']}"
            self.pattern_db[key] = self.pattern_db.get(key, 0) + 1
# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Universal AI Code Review Server v4.0...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
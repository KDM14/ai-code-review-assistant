import openai
import os
from typing import List, Dict
import json

class AIReviewer:
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def review_code_changes(self, files_changed: List[Dict], pr_details: Dict) -> List[Dict]:
        """Main method to review code changes"""
        
        print("🤖 AI is reviewing code changes...")
        
        # Build prompt for AI
        prompt = self._build_review_prompt(files_changed, pr_details)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert senior software engineer reviewing code changes.
                        Provide CONCISE, ACTIONABLE feedback focusing on:
                        1. Code quality and best practices
                        2. Potential bugs or logical errors
                        3. Security concerns
                        4. Performance improvements
                        5. Readability and maintainability

                        Be constructive and specific. Point to exact lines when possible.
                        Format your response as JSON."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            print(f"🤖 AI Response: {ai_response[:200]}...")  # Debug log
            return self._parse_ai_response(ai_response, files_changed)
            
        except Exception as e:
            print(f"❌ Error calling OpenAI: {e}")
            return [{
                "type": "error",
                "content": "Unable to generate AI review at this time.",
                "file": "general",
                "line": 1
            }]
    
    def _build_review_prompt(self, files_changed: List[Dict], pr_details: Dict) -> str:
        """Build the prompt for AI review"""
        
        prompt = f"Review this pull request: #{pr_details.get('number', 'N/A')} - {pr_details.get('title', 'No title')}\n\n"
        
        for file in files_changed[:2]:  # Limit to 2 files to avoid token limits
            prompt += f"--- FILE: {file['filename']} ---\n"
            if file.get('patch'):
                # Limit patch size
                patch_preview = file['patch'][:1000] + "..." if len(file['patch']) > 1000 else file['patch']
                prompt += f"Changes:\n```diff\n{patch_preview}\n```\n\n"
        
        prompt += """
        Provide your review in this EXACT JSON format:
        {
            "suggestions": [
                {
                    "type": "bug|security|performance|improvement|question",
                    "file": "filename.py", 
                    "line": 15,
                    "content": "Specific suggestion here",
                    "priority": "high|medium|low"
                }
            ]
        }
        Keep suggestions brief and actionable. Maximum 3 suggestions.
        """
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str, files_changed: List[Dict]) -> List[Dict]:
        """Parse AI response into structured suggestions"""
        
        try:
            # Try to extract JSON from response
            if "{" in ai_response and "}" in ai_response:
                json_str = ai_response[ai_response.find("{"):ai_response.rfind("}")+1]
                data = json.loads(json_str)
                suggestions = data.get("suggestions", [])
                print(f"✅ Parsed {len(suggestions)} suggestions from AI")
                return suggestions
        except Exception as e:
            print(f"⚠️ Could not parse AI response as JSON: {e}")
        
        # Fallback: return general feedback
        return [{
            "type": "improvement",
            "file": files_changed[0]['filename'] if files_changed else "general",
            "line": 1,
            "content": ai_response[:300],  # Truncate if too long
            "priority": "medium"
        }]
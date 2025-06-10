import json
import requests
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import PyPDF2
import io
import os
from urllib.parse import urlparse, urljoin
import re
from bs4 import BeautifulSoup

@dataclass
class ResearchStep:
    step_id: int
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    tools_used: List[str] = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []

@dataclass
class ResearchPlan:
    topic: str
    objective: str
    steps: List[ResearchStep]
    created_at: str
    updated_at: str
    
class LMStudioClient:
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Make a chat completion request to LM Studio"""
        payload = {
            "model": "local-model",  # LM Studio uses this as default
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error calling LM Studio: {e}")
            return f"Error: Could not get response from LLM - {str(e)}"

class WebSearchTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_duckduckgo(self, query: str, num_results: int = 5) -> List[Dict]:
        """Simple DuckDuckGo search implementation"""
        try:
            # Using DuckDuckGo's instant answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            results = []
            
            # Extract abstract if available
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Abstract'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': 'duckduckgo_abstract'
                })
            
            # Extract related topics
            for topic in data.get('RelatedTopics', [])[:num_results-1]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('Text', '')[:100] + '...',
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'duckduckgo_related'
                    })
            
            return results[:num_results]
            
        except Exception as e:
            print(f"Search error: {e}")
            return [{'title': 'Search Error', 'url': '', 'snippet': f'Could not perform search: {str(e)}', 'source': 'error'}]
    
    def fetch_webpage(self, url: str) -> str:
        """Fetch and extract text content from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limit to first 5000 characters
            
        except Exception as e:
            return f"Error fetching webpage: {str(e)}"

class PDFTool:
    def read_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def write_pdf_report(self, content: str, output_path: str) -> bool:
        """Write research report to PDF (simple text-based)"""
        try:
            # For a simple implementation, we'll create a text file
            # In a full implementation, you'd use reportlab or similar
            with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Report saved as text file: {output_path.replace('.pdf', '.txt')}")
            return True
        except Exception as e:
            print(f"Error writing report: {e}")
            return False

class ResearchAgent:
    def __init__(self, lm_studio_url: str = "http://localhost:1234/v1"):
        self.llm = LMStudioClient(lm_studio_url)
        self.web_search = WebSearchTool()
        self.pdf_tool = PDFTool()
        self.current_plan: Optional[ResearchPlan] = None
        self.research_data: Dict[str, Any] = {}
        
    def create_research_plan(self, topic: str, objective: str) -> ResearchPlan:
        """Generate a research plan using the LLM"""
        messages = [
            {
                "role": "system",
                "content": """You are a research planning assistant. Create a detailed step-by-step research plan.
                Return your response as a JSON object with this structure:
                {
                    "steps": [
                        {
                            "step_id": 1,
                            "description": "Clear description of what to do",
                            "tools_needed": ["web_search", "pdf_reader", etc.]
                        }
                    ]
                }
                
                Make sure each step is specific and actionable. Include 5-8 steps typically."""
            },
            {
                "role": "user", 
                "content": f"Create a research plan for the topic: '{topic}' with the objective: '{objective}'"
            }
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.3)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
                steps = [
                    ResearchStep(
                        step_id=step["step_id"],
                        description=step["description"],
                        tools_used=step.get("tools_needed", [])
                    ) 
                    for step in plan_data["steps"]
                ]
            else:
                # Fallback if JSON parsing fails
                steps = self._create_default_plan()
                
        except Exception as e:
            print(f"Error parsing plan: {e}")
            steps = self._create_default_plan()
        
        plan = ResearchPlan(
            topic=topic,
            objective=objective,
            steps=steps,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.current_plan = plan
        return plan
    
    def _create_default_plan(self) -> List[ResearchStep]:
        """Fallback research plan if LLM planning fails"""
        return [
            ResearchStep(1, "Define key concepts and terminology", tools_used=["web_search"]),
            ResearchStep(2, "Search for recent academic sources", tools_used=["web_search"]),
            ResearchStep(3, "Gather statistical data and facts", tools_used=["web_search"]),
            ResearchStep(4, "Find expert opinions and analysis", tools_used=["web_search"]),
            ResearchStep(5, "Identify controversies or debates", tools_used=["web_search"]),
            ResearchStep(6, "Synthesize findings", tools_used=[]),
        ]
    
    def execute_step(self, step: ResearchStep) -> str:
        """Execute a single research step"""
        step.status = "in_progress"
        print(f"\n🔍 Executing Step {step.step_id}: {step.description}")
        
        if "web_search" in step.tools_used:
            return self._execute_web_search_step(step)
        elif "pdf_reader" in step.tools_used:
            return self._execute_pdf_step(step)
        else:
            return self._execute_analysis_step(step)
    
    def _execute_web_search_step(self, step: ResearchStep) -> str:
        """Execute a step that requires web searching"""
        # Generate search query based on step description
        messages = [
            {
                "role": "system",
                "content": "Generate 1-3 specific search queries for this research step. Return only the queries, one per line."
            },
            {
                "role": "user",
                "content": f"Research topic: {self.current_plan.topic}\nStep: {step.description}\nGenerate search queries:"
            }
        ]
        
        query_response = self.llm.chat_completion(messages, temperature=0.5)
        queries = [q.strip() for q in query_response.split('\n') if q.strip()][:3]
        
        all_results = []
        for query in queries:
            print(f"  🔍 Searching: {query}")
            results = self.web_search.search_duckduckgo(query)
            all_results.extend(results)
            time.sleep(1)  # Be respectful to the API
        
        # Fetch some webpage content
        content_samples = []
        for result in all_results[:3]:  # Fetch top 3 results
            if result['url']:
                print(f"  📄 Fetching: {result['url']}")
                content = self.web_search.fetch_webpage(result['url'])
                content_samples.append(f"Source: {result['title']}\nURL: {result['url']}\nContent: {content[:1000]}...")
        
        # Analyze and summarize findings
        analysis_messages = [
            {
                "role": "system",
                "content": "Analyze the search results and provide a clear, structured summary of key findings relevant to the research step."
            },
            {
                "role": "user",
                "content": f"Research step: {step.description}\n\nSearch results:\n" + "\n\n".join(content_samples)
            }
        ]
        
        analysis = self.llm.chat_completion(analysis_messages, temperature=0.3)
        
        step.result = analysis
        step.status = "completed"
        
        return analysis
    
    def _execute_pdf_step(self, step: ResearchStep) -> str:
        """Execute a step that requires PDF analysis"""
        # This would be implemented if you have specific PDFs to analyze
        step.result = "PDF analysis step - implement based on your specific PDF sources"
        step.status = "completed"
        return step.result
    
    def _execute_analysis_step(self, step: ResearchStep) -> str:
        """Execute a step that requires synthesis/analysis"""
        # Gather all previous results
        previous_findings = []
        for prev_step in self.current_plan.steps:
            if prev_step.status == "completed" and prev_step.result:
                previous_findings.append(f"Step {prev_step.step_id}: {prev_step.result}")
        
        messages = [
            {
                "role": "system",
                "content": "Synthesize and analyze the research findings. Provide insights, connections, and conclusions."
            },
            {
                "role": "user",
                "content": f"Research objective: {self.current_plan.objective}\nCurrent step: {step.description}\n\nPrevious findings:\n" + "\n\n".join(previous_findings)
            }
        ]
        
        analysis = self.llm.chat_completion(messages, temperature=0.4)
        
        step.result = analysis
        step.status = "completed"
        
        return analysis
    
    def reflect_on_progress(self) -> str:
        """Reflect on research progress and suggest adjustments"""
        completed_steps = [s for s in self.current_plan.steps if s.status == "completed"]
        
        messages = [
            {
                "role": "system",
                "content": """You are reflecting on research progress. Analyze what has been accomplished, 
                identify gaps, and suggest next steps or adjustments to the research plan."""
            },
            {
                "role": "user",
                "content": f"""Research Topic: {self.current_plan.topic}
                Objective: {self.current_plan.objective}
                
                Completed Steps:
                """ + "\n".join([f"Step {s.step_id}: {s.description}\nResult: {s.result[:200]}..." 
                               for s in completed_steps])
            }
        ]
        
        reflection = self.llm.chat_completion(messages, temperature=0.6)
        print(f"\n🤔 Reflection:\n{reflection}")
        return reflection
    
    def conduct_research(self, topic: str, objective: str) -> str:
        """Main method to conduct complete research"""
        print(f"🎯 Starting research on: {topic}")
        print(f"📋 Objective: {objective}")
        
        # Create plan
        plan = self.create_research_plan(topic, objective)
        print(f"\n📝 Created research plan with {len(plan.steps)} steps:")
        for step in plan.steps:
            print(f"  {step.step_id}. {step.description}")
        
        # Execute steps
        for step in plan.steps:
            try:
                result = self.execute_step(step)
                self.research_data[f"step_{step.step_id}"] = result
                
                # Reflect every few steps
                if step.step_id % 3 == 0:
                    self.reflect_on_progress()
                    
            except Exception as e:
                print(f"❌ Error in step {step.step_id}: {e}")
                step.status = "failed"
                step.result = f"Failed: {str(e)}"
        
        # Final synthesis
        print("\n📊 Generating final report...")
        return self.generate_final_report()
    
    def generate_final_report(self) -> str:
        """Generate comprehensive final report"""
        all_findings = []
        for step in self.current_plan.steps:
            if step.status == "completed" and step.result:
                all_findings.append(f"## {step.description}\n{step.result}")
        
        messages = [
            {
                "role": "system",
                "content": """Create a comprehensive research report. Include:
                1. Executive Summary
                2. Key Findings
                3. Analysis and Insights
                4. Conclusions
                5. Areas for Further Research
                
                Make it well-structured and professional."""
            },
            {
                "role": "user",
                "content": f"""Topic: {self.current_plan.topic}
                Objective: {self.current_plan.objective}
                
                Research Findings:
                """ + "\n\n".join(all_findings)
            }
        ]
        
        final_report = self.llm.chat_completion(messages, temperature=0.3, max_tokens=3000)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Research Report: {self.current_plan.topic}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("="*80 + "\n\n")
            f.write(final_report)
        
        print(f"📄 Report saved: {filename}")
        return final_report

# Example usage
if __name__ == "__main__":
    # Initialize the research agent
    agent = ResearchAgent("http://localhost:1234/v1")  # Adjust URL as needed
    
    # Conduct research
    topic = "The impact of artificial intelligence on job markets in 2024"
    objective = "Understand how AI is currently affecting employment, which sectors are most impacted, and what the future outlook is for workers"
    
    try:
        final_report = agent.conduct_research(topic, objective)
        print(f"\n" + "="*80)
        print("FINAL REPORT")
        print("="*80)
        print(final_report)
        
    except KeyboardInterrupt:
        print("\n🛑 Research interrupted by user")
    except Exception as e:
        print(f"❌ Error during research: {e}")
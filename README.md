# 🔬 AURA - AUtonomous Research Agent

AURA is an intelligent, autonomous research assistant powered by local LLMs through LM Studio. This agent can plan, execute, and synthesize comprehensive research on any topic using web search, document analysis, and iterative reflection.

## 🌟 Features

### 🧠 **Intelligent Planning**
- Automatically generates structured research plans
- Breaks down complex topics into actionable steps
- Adapts research direction based on findings

### 🔍 **Multi-Tool Research**
- **Web Search**: DuckDuckGo API integration for current information
- **Web Scraping**: Extracts and analyzes content from web sources
- **PDF Analysis**: Reads and processes PDF documents
- **Content Synthesis**: Combines findings from multiple sources

### 🤖 **Autonomous Operation**
- Self-directed research execution
- Progress tracking and status management
- Iterative reflection and course correction
- Comprehensive report generation

### 🏠 **Local LLM Integration**
- Works with any LM Studio hosted model
- OpenAI-compatible API calls
- Configurable model parameters
- Privacy-focused (no external LLM APIs required)

## 🚀 Quick Start

### Prerequisites

1. **LM Studio**: Download and install [LM Studio](https://lmstudio.ai/)
2. **Python 3.8+**: Ensure you have Python installed
3. **Local LLM**: Load any compatible model in LM Studio (7B+ recommended)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ai-research-agent.git
cd ai-research-agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start LM Studio:**
   - Open LM Studio
   - Load your preferred model (e.g., Llama 2, Mistral, etc.)
   - Start the local server (default: `http://localhost:1234`)

### Basic Usage

```python
from research_agent import ResearchAgent

# Initialize the agent
agent = ResearchAgent("http://localhost:1234/v1")

# Conduct research
topic = "The impact of renewable energy on global economics"
objective = "Understand current trends, market dynamics, and future projections"

final_report = agent.conduct_research(topic, objective)
print(final_report)
```

## 📋 Requirements

Create a `requirements.txt` file:
```
requests>=2.31.0
PyPDF2>=3.0.1
beautifulsoup4>=4.12.2
lxml>=4.9.3
```

## 🎯 How It Works

### 1. **Planning Phase**
The agent analyzes your research topic and creates a structured plan:
```
📝 Created research plan with 6 steps:
  1. Define key concepts and terminology
  2. Search for recent academic sources
  3. Gather statistical data and facts
  4. Find expert opinions and analysis
  5. Identify controversies or debates
  6. Synthesize findings
```

### 2. **Execution Phase**
Each step is executed autonomously:
- **Web searches** with dynamically generated queries
- **Content extraction** from relevant sources
- **Analysis and summarization** using the local LLM
- **Progress tracking** with status updates

### 3. **Reflection Phase**
Periodic self-evaluation:
- Reviews completed work
- Identifies research gaps
- Suggests plan adjustments
- Ensures objective alignment

### 4. **Synthesis Phase**
Final report generation:
- Executive summary
- Key findings
- Analysis and insights
- Conclusions
- Areas for further research

## ⚙️ Configuration

### LM Studio Setup
```python
# Default configuration
agent = ResearchAgent("http://localhost:1234/v1")

# Custom configuration
agent = ResearchAgent(
    lm_studio_url="http://localhost:8080/v1",  # Custom port
)

# Adjust LLM parameters in the code:
response = self.llm.chat_completion(
    messages, 
    temperature=0.7,    # Creativity level
    max_tokens=2000     # Response length
)
```

### Customizing Research Steps
You can modify the default research plan by editing the `_create_default_plan()` method:

```python
def _create_default_plan(self) -> List[ResearchStep]:
    return [
        ResearchStep(1, "Your custom research step", tools_used=["web_search"]),
        ResearchStep(2, "Another custom step", tools_used=["pdf_reader"]),
        # Add more steps as needed
    ]
```

## 🛠️ Advanced Usage

### Adding Custom Tools
Extend the agent with your own research tools:

```python
class CustomTool:
    def analyze_data(self, data: str) -> str:
        # Your custom analysis logic
        return analysis_result

# Integrate into the agent
class ExtendedResearchAgent(ResearchAgent):
    def __init__(self, lm_studio_url: str):
        super().__init__(lm_studio_url)
        self.custom_tool = CustomTool()
```

### PDF Document Analysis
```python
# Analyze specific PDFs
pdf_content = agent.pdf_tool.read_pdf("research_document.pdf")

# Include PDF analysis in research steps
step = ResearchStep(
    step_id=7,
    description="Analyze uploaded research papers",
    tools_used=["pdf_reader"]
)
```

## 📊 Example Output

The agent generates detailed reports like this:

```
Research Report: The Future of Quantum Computing
Generated: 2024-01-15T10:30:00

# Executive Summary
Quantum computing represents a paradigm shift in computational capability...

# Key Findings
1. Current State: Major tech companies have invested $X billion...
2. Technical Challenges: Quantum decoherence remains the primary obstacle...
3. Market Projections: Expected to reach $X billion by 2030...

# Analysis and Insights
The convergence of quantum algorithms and error correction...

# Conclusions
While still in early stages, quantum computing shows promise...

# Areas for Further Research
1. Quantum error correction improvements
2. Practical algorithm development
3. Industry adoption timelines
```

## 🔧 Troubleshooting

### Common Issues

**LM Studio Connection Error:**
```
Error calling LM Studio: Connection refused
```
- Ensure LM Studio is running
- Check the server URL and port
- Verify model is loaded and server is started

**Search API Limitations:**
```
Search error: Rate limited
```
- The agent includes delays between requests
- DuckDuckGo has usage limits for their free API
- Consider implementing additional search providers

**Memory Usage:**
- Large models (70B+) may require significant RAM
- Consider using smaller models (7B-13B) for development
- Monitor system resources during operation

## 🚀 Future Enhancements

### Planned Features
- [ ] Multiple search engine support (Google, Bing)
- [ ] Database integration for research storage
- [ ] Interactive web interface
- [ ] Collaborative research sessions
- [ ] Citation tracking and bibliography generation
- [ ] Real-time research monitoring dashboard

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 Use Cases

### Academic Research
- Literature reviews
- Market analysis
- Technology assessments
- Policy research

### Business Intelligence
- Competitor analysis
- Market trends
- Industry reports
- Strategic planning

### Personal Learning
- Topic exploration
- Fact-checking
- Comprehensive overviews
- Educational summaries

## ⚖️ Ethical Considerations

- **Respect robots.txt** and website terms of service
- **Rate limiting** implemented to avoid overwhelming servers
- **Source attribution** in all generated reports
- **Fact verification** recommended for critical decisions

## 🤝 Community & Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join the conversation in GitHub Discussions
- **Documentation**: Wiki pages for advanced configuration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LM Studio](https://lmstudio.ai/) for local LLM hosting
- [DuckDuckGo](https://duckduckgo.com/) for search API
- The open-source community for various Python libraries

---

**⭐ If you find this project useful, please give it a star!**

Built with ❤️ for the AI research community
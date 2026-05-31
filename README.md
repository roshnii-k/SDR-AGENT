# Self-Correcting SDR Agent 🤖

A multi-node agentic AI system built with LangGraph that automatically drafts and self-corrects B2B cold outreach emails.

## How It Works
- **Writer Agent** drafts a personalized cold email
- **Critic Agent** reviews it against strict quality rules
- If rejected, the Writer automatically fixes it based on feedback
- Loops up to 3 times until the email is approved

## Tech Stack
- LangGraph — agentic workflow orchestration
- LangChain — LLM integration
- Groq (LLaMA 3) — free LLM API
- Python 3.13

## Setup
1. Clone the repo
2. Install dependencies:
   pip install langgraph langchain-groq python-dotenv rich
3. Create a `.env` file and add your Groq API key:
   GROQ_API_KEY=your-key-here
4. Run:
   python agent.py

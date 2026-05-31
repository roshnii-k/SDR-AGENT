import os
from typing import Dict, Any
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.panel import Panel
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7) 

console = Console()

def create_initial_state(company: str, value_prop: str) -> Dict[str, Any]:
    return {
        "company_name": company,
        "value_proposition": value_prop,
        "draft_email": "",
        "critic_feedback": "",
        "attempts": 0,
        "status": "start"
    }

def write_email_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["attempts"] += 1
    console.print(Panel(f"[bold yellow]🤖 Writer Agent (Attempt #{state['attempts']}):[/bold yellow] Drafting email for [green]{state['company_name']}[/green]..."))
    prompt = f"""
    You are an expert AI B2B SDR. Write a highly personalized cold outreach email to the company '{state['company_name']}'.
    Our product value proposition: '{state['value_proposition']}'.
    Keep it concise, professional, and outcome-focused.
    """
    if state["critic_feedback"]:
        prompt += f"\nYour previous attempt was REJECTED. Fix this specific feedback: {state['critic_feedback']}"
    response = llm.invoke(prompt)
    state["draft_email"] = response.content
    return state

def critique_email_node(state: Dict[str, Any]) -> Dict[str, Any]:
    console.print(Panel("[bold magenta]🧐 Critic Agent:[/bold magenta] Evaluating the quality of the draft..."))
    prompt = f"""
    You are a strict Sales Manager reviewing a junior SDR's cold email.
    Review this draft:
    \"\"\"
    {state['draft_email']}
    \"\"\"
    CRITERIA RULES:
    1. The email must be brief and strictly under 150 words.
    2. It must NOT contain corporate buzzwords like 'synergy', 'revolutionize', or 'game-changing'.
    3. It must clearly reference our value proposition.

    If the email follows all rules, reply with exactly one word: APPROVED
    If it fails, reply with a short, brutal sentence explaining exactly what to fix.
    """
    response = llm.invoke(prompt)
    feedback = response.content.strip()
    if "APPROVED" in feedback.upper():
        state["critic_feedback"] = "PASS"
    else:
        state["critic_feedback"] = feedback
    return state

workflow = StateGraph(dict)
workflow.add_node("writer_station", write_email_node)
workflow.add_node("critic_station", critique_email_node)
workflow.set_entry_point("writer_station")
workflow.add_edge("writer_station", "critic_station")

def routing_decision_logic(state: Dict[str, Any]) -> str:
    if state["critic_feedback"] == "PASS":
        return "accept"
    if state["attempts"] >= 3:
        return "give_up"
    return "try_again"

workflow.add_conditional_edges(
    "critic_station",
    routing_decision_logic,
    {
        "accept": END,
        "try_again": "writer_station",
        "give_up": END
    }
)

agent_app = workflow.compile()

if __name__ == "__main__":
    console.print("[bold blue]🚀 Launching Self-Correcting SDR Agent...[/bold blue]\n")
    target_company = "Acme Logistics Corp"
    our_value_proposition = "We provide an autonomous AI scheduling platform that cuts truck routing delays by 40% using multi-agent workflows."
    initial_state = create_initial_state(target_company, our_value_proposition)
    final_result = agent_app.invoke(initial_state)
    console.print("\n[bold green]🏆 WORKFLOW COMPLETE! FINAL SANITIZED EMAIL OUTPUT:[/bold green]")
    console.print(Panel(final_result["draft_email"], subtitle=f"Total self-correction attempts: {final_result['attempts']}"))

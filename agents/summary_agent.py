from strands import Agent
from strands.models import BedrockModel
import os
import streamlit as st
from dotenv import load_dotenv

from agents.summary_tools import (
    get_champion_insights_summary,
    get_advanced_stats_summary,
    get_early_late_game_summary,
    get_matchup_analysis_summary,
    get_performance_trends_summary,
)

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")

SUMMARY_SYSTEM_PROMPT = """You are a League of Legends statistics analyst providing concise, data-driven summaries.

Your job is to:
1. Call the appropriate tool to get the EXACT stats shown on the current page
2. Reference specific numbers from those stats in your summary
3. Explain what those specific metrics mean in practical terms
4. Provide actionable next steps based on the data

CRITICAL RULES:
- Always start by using the tool to fetch the page's data
- Reference SPECIFIC numbers (e.g., "Your 3 A-tier champions have 65%+ win rates" NOT "You have some good champions")
- Explain what the metrics mean (e.g., "CS@10 of 55 is below the 60+ benchmark for laners")
- Keep it SHORT (4-6 sentences max)
- Be objective and fact-based
- End with ONE clear action item
- Do not start with "Based on X data, here is my analysis," just dive into the analysis

STRUCTURE:
1. Key finding (what stands out in the data?)
2. Context (what does this number mean? Is it good/bad?)
3. Supporting detail (mention 1-2 other relevant stats)
4. Action (what should the player do?)

EXAMPLE (Champion Insights):
"You're playing 15 different champions across 50 games, with a diversity ratio of 0.30. Your top 3 champions (Jinx, Caitlyn, Ashe) account for only 40% of your games, despite all being in B-tier with 55%+ win rates. Your 5 D-tier picks (KDA < 2.0) are dragging down your overall performance with sub-40% win rates. Stick to your proven top 5 performers and avoid experimenting in ranked - your focused picks have a 12% higher win rate."

EXAMPLE (Early vs Late Game):
"Your early game shows a significant 15 CS@10 gap between wins (65 CS) and losses (50 CS). In wins, you average 65 CS@10 which is solid for laners, but in losses you're falling 10+ CS behind the benchmark. Your gold/min difference of 50g between wins and losses compounds this advantage. Focus on your laning fundamentals - improving your CS@10 from 50 to 60+ in losses could swing close games in your favor."

ROLE-AWARE ANALYSIS:
- Always consider the player's role when interpreting stats
- For SUPPORTS: Focus on vision metrics, utility output, kill participation - NOT CS or damage
- For JUNGLERS: Focus on objective control, jungle efficiency, early pressure - NOT lane CS
- For LANERS: Focus on CS@10, lane pressure, trading effectiveness
- If a player has multiple roles (primary + secondary), acknowledge both in your analysis
- Never criticize a support for low CS or a jungler for not having lane CS@10

DO NOT:
- Give generic advice ("play better", "focus on fundamentals") without specific stats
- Mention stats that aren't on the current page
- Write long paragraphs or bullet lists
- Use vague terms like "pretty good" or "could be better"
"""


@st.cache_resource
def initialize_summary_agent():
    """Initialize the summary agent with specialized tools"""
    bedrock_model = BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        temperature=0.3,  # Lower temperature for more consistent, factual summaries
        max_tokens=500,   # Short responses
    )
    
    agent = Agent(
        model=bedrock_model,
        system_prompt=SUMMARY_SYSTEM_PROMPT,
        tools=[
            get_champion_insights_summary,
            get_advanced_stats_summary,
            get_early_late_game_summary,
            get_matchup_analysis_summary,
            get_performance_trends_summary,
        ]
    )
    
    return agent


def generate_page_summary(page_name: str, page_metrics: dict = None) -> str:
    """
    Generate a summary for a specific page with optional page-specific metrics.
    
    Args:
        page_name: One of 'champion_insights', 'advanced_stats', 'early_late', 
                   'matchup_analysis', 'performance_trends'
        page_metrics: Optional dict of metrics calculated in main.py for this specific page
    
    Returns:
        str: AI-generated summary
    """
    prompts = {
        'champion_insights': """Analyze my champion pool using get_champion_insights_summary(). 
        Focus on: tier distribution, diversity ratio, top performers, and whether my pool is too wide or well-focused. 
        Reference specific champions, their KDAs, win rates, and game counts.""",
        
        'advanced_stats': """Analyze my advanced performance metrics using the available tools. 
        Focus on: KDA std dev, aggression score, early game dominance score, objective score, performance volatility, 
        safety score, persistence score and the 4 performance scores (Aggression, Safety, Consistency, Impact). 
        Explain what each key metric means and whether it's good or needs work.""",
        
        'early_late': """Analyze my early game performance using get_early_late_game_summary(). 
        Focus on the 3 metrics shown. For laners its: CS@10, Gold/Min, and Early Kills - comparing wins vs losses.
        For junglers its: Jungle CS@10, Gold/Min, and Early Takedowns - comparing wins vs losses.
        For supports/utility its: Wards@10, Quest Completion and Early Assists - comparing wins and losses
        Explain what the differences mean (e.g., CS@10 benchmark is 60+ for laners) and whether my early game is winning or losing me games.""",
        
        'matchup_analysis': """Analyze my matchup performance using get_matchup_analysis_summary(). 
        Focus on: best matchups (60%+ WR), worst matchups (<40% WR), specific champion combinations, 
        and CS diff@10 in these matchups. List specific champion vs champion matchups with win rates.""",
        
        'performance_trends': """Analyze my performance trends using get_performance_trends_summary(). 
        Focus on: overall win rate, average K/D/A shown in the charts, the wins vs losses comparison 
        (especially deaths gap, CS difference, damage difference), recent form (last 5 games), 
        and TOP PERFORMING CHAMPIONS (list the top 2-3 champions by name with their win rates and games played). 
        Identify the biggest performance gap between wins and losses and which champions are carrying your climb."""
    }
    
    prompt = prompts.get(page_name, "Provide a brief summary of the player's statistics.")
    
    # Add page-specific metrics if provided
    if page_metrics:
        prompt += f"\n\nAdditional page metrics: {page_metrics}"
    
    try:
        agent = initialize_summary_agent()
        response = agent(prompt)
        return str(response)
    except Exception as e:
        return f"Unable to generate summary: {str(e)}"
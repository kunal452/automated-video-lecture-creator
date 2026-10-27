import json
import re
from typing import List, Dict, Any, Optional
import requests

def generate_curriculum_heuristically(topic: str, num_slides: int = 4, audience: str = "undergraduate") -> List[Dict[str, Any]]:
    """
    Offline pedagogical curriculum generator that builds a coherent,
    structured lecture deck without requiring external LLM API keys.
    """
    clean_topic = topic.strip().title()
    templates = [
        {
            "title": f"Introduction to {clean_topic}",
            "bullets": [
                f"Core definition and foundational motivations for {clean_topic}",
                "Historical background and emerging industry relevance",
                "Key problems solved by this conceptual framework"
            ],
            "script": (
                f"Welcome to today's lecture on {clean_topic}. "
                f"In this introductory session tailored for {audience} level study, "
                f"we will break down the essential foundations of {clean_topic}, "
                f"examine why it matters in real-world applications, and preview the core architecture."
            )
        },
        {
            "title": f"Core Architecture & Principles of {clean_topic}",
            "bullets": [
                "Fundamental building blocks and data flow",
                "Internal mechanism and mathematical/algorithmic intuition",
                "Key trade-offs, constraints, and latency considerations"
            ],
            "script": (
                f"Now let us examine the internal architecture of {clean_topic}. "
                f"Rather than treating it as a black box, notice how each component interacts. "
                f"The flow of data and execution invariants ensure both stability and efficiency, "
                f"balancing computational complexity against scalability."
            )
        },
        {
            "title": f"Real-World Implementations & Case Studies",
            "bullets": [
                "Practical production deployment patterns",
                "Common failure modes and how to diagnose them",
                "Industry standards, tooling, and ecosystem integration"
            ],
            "script": (
                f"Moving forward, how does {clean_topic} perform in real-world systems? "
                f"In production environments, teams often encounter specific bottlenecks. "
                f"By following established design patterns and automated monitoring, "
                f"engineers achieve optimal resilience and predictable latency."
            )
        },
        {
            "title": f"Summary, Future Horizons & Key Takeaways",
            "bullets": [
                "Recap of foundational pillars and best practices",
                "Active research directions and state-of-the-art benchmarks",
                "Recommended next steps, experiments, and references"
            ],
            "script": (
                f"To wrap up our discussion on {clean_topic}, let us review the primary takeaways. "
                f"Mastering the underlying mechanics gives you the intuition to design better systems. "
                f"Thank you for your attention, and be sure to review the accompanying notes and references."
            )
        }
    ]

    # Adjust to requested slide count
    slides = []
    for i in range(min(num_slides, len(templates))):
        item = templates[i]
        slides.append({
            "index": i + 1,
            "title": item["title"],
            "bullet_points": item["bullets"],
            "code_snippet": None,
            "spoken_script": item["script"]
        })

    # If more slides requested, extrapolate further modules
    while len(slides) < num_slides:
        curr_idx = len(slides) + 1
        slides.append({
            "index": curr_idx,
            "title": f"Deep Dive Part {curr_idx - 3}: Advanced Concepts in {clean_topic}",
            "bullet_points": [
                f"High-performance tuning for {clean_topic}",
                "Edge-case handling and security mitigations",
                "Comparative benchmark analysis"
            ],
            "code_snippet": None,
            "spoken_script": (
                f"In this section, we take a deeper technical dive into {clean_topic}. "
                f"Specifically focusing on edge-case behavior, security implications, "
                f"and performance optimization techniques essential for complex implementations."
            )
        })

    return slides

def generate_via_gemini_or_openai(
    topic: str, 
    num_slides: int = 4, 
    audience: str = "undergraduate",
    provider: str = "gemini",
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Calls Gemini or OpenAI if API key is provided, falling back gracefully to heuristic generator.
    """
    if not api_key:
        return generate_curriculum_heuristically(topic, num_slides, audience)

    system_prompt = (
        "You are an expert university professor creating an automated video lecture. "
        "Generate a structured JSON output with an array of slides. "
        "Each slide object must contain: 'index' (int), 'title' (string), "
        "'bullet_points' (list of 3 strings), 'code_snippet' (optional string or null), "
        "and 'spoken_script' (a natural, conversational teaching narration of 2-4 sentences explaining the concepts)."
    )
    user_prompt = f"Create a {num_slides}-slide lecture on '{topic}' for {audience} students. Return ONLY valid JSON."

    try:
        if provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                raw_json = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                data = json.loads(raw_json)
                if isinstance(data, dict) and "slides" in data:
                    return data["slides"]
                if isinstance(data, list):
                    return data
        elif provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = requests.post(url, json=payload, headers=headers, timeout=25)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return parsed.get("slides", parsed)
    except Exception as e:
        print(f"LLM API generation failed: {e}. Falling back to heuristic generator.")

    return generate_curriculum_heuristically(topic, num_slides, audience)

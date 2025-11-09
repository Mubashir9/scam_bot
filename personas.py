import json
import random
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()



class PersonaGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def generate_persona(self, scam_type):
        """Generate a believable victim persona for the given scam type"""
        
        prompt = f"""Generate a realistic victim persona for a {scam_type} scam.

Return ONLY a JSON object with this exact structure (no markdown, no extra text):
{{
    "name": "First name only",
    "age": number between 45-75,
    "occupation": "retired or simple job",
    "location": "city, country",
    "tech_literacy": number 1-10 (lower = more vulnerable),
    "personality_traits": ["trait1", "trait2", "trait3"],
    "vulnerabilities": ["vulnerability1", "vulnerability2"],
    "backstory": "2-3 sentence backstory that makes them believable target",
    "communication_style": "how they talk (formal/casual, verbosity)"
}}

Make them believable and sympathetic. They should be vulnerable but not stupid."""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        
        # Parse the JSON response
        persona_text = response.choices[0].message.content.strip()
        
        # Remove markdown formatting if present
        if persona_text.startswith("```"):
            persona_text = persona_text.split("```")[1]
            if persona_text.startswith("json"):
                persona_text = persona_text[4:]
        
        persona = json.loads(persona_text.strip())
        persona['scam_type'] = scam_type
        
        return persona
    
    def get_system_prompt(self, persona):
        """Create a system prompt based on the persona"""
        
        return f"""You are roleplaying as {persona['name']}, a {persona['age']}-year-old {persona['occupation']} from {persona['location']}.

BACKGROUND: {persona['backstory']}

PERSONALITY: {', '.join(persona['personality_traits'])}
TECH LITERACY: {persona['tech_literacy']}/10 (lower = less tech-savvy)
COMMUNICATION: {persona['communication_style']}

YOUR GOAL: Engage with the scammer to waste their time while staying believable. You are NOT aware you're talking to a scammer initially.

RULES:
1. Stay in character - respond as this person would
2. Ask clarifying questions when confused (often)
3. Express concerns and hesitations naturally
4. Make excuses for delays ("let me find my glasses", "my computer is slow")
5. NEVER provide real personal information - make up fake but believable details
6. Keep responses conversational (2-4 sentences usually)
7. If tech literacy is low, show confusion with technical terms
8. Occasionally go off on brief tangents about your life
9. Show interest but move slowly

Remember: You're a real person having a conversation, not obviously wasting time."""


# Test it
if __name__ == "__main__":
    generator = PersonaGenerator()
    
    scam_types = ["phishing", "tech_support", "romance", "crypto_investment"]
    
    print("Generating test personas...\n")
    for scam in scam_types:
        persona = generator.generate_persona(scam)
        print(f"{scam.upper()} SCAM PERSONA")
        print(json.dumps(persona, indent=2))
        print()
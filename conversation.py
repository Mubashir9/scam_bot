from groq import Groq
from dotenv import load_dotenv
import os
import random

load_dotenv()

class ConversationManager:
    def __init__(self, persona, intelligence_extractor):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.persona = persona
        self.intelligence = intelligence_extractor
        self.conversation_history = []
        self.intel_log = []
        self.turn_count = 0
        
        # Conversation states
        self.state = "INITIAL_CONTACT"
        
        # Stalling tactics
        self.tactics = [
            "technical_difficulty",
            "need_assistance",
            "clarification_needed",
            "distraction",
            "fake_compliance"
        ]
    
    def get_current_tactic(self):
        """Select a stalling tactic based on conversation state"""
        
        if self.turn_count < 3:
            return "clarification_needed"
        elif self.turn_count < 6:
            return random.choice(["technical_difficulty", "need_assistance"])
        elif self.turn_count < 10:
            return random.choice(["distraction", "fake_compliance"])
        else:
            return "fake_compliance"
    
    def update_state(self, scammer_message):
        """Update conversation state based on scammer behavior"""
        
        lower_msg = scammer_message.lower()
        
        if any(word in lower_msg for word in ['click', 'link', 'website', 'download']):
            self.state = "REQUEST"
        elif any(word in lower_msg for word in ['urgent', 'now', 'immediately', 'hurry']):
            self.state = "PRESSURE"
        elif self.turn_count > 15:
            self.state = "DISENGAGE"
        elif self.turn_count > 8:
            self.state = "LATE_STAGE"
        
    def generate_response(self, scammer_message):
        """Generate a response to the scammer"""
        
        # Extract intelligence first
        intel = self.intelligence.process_message(scammer_message)
        self.intel_log.append(intel)
        
        # Update state
        self.update_state(scammer_message)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": scammer_message
        })
        
        # Get current tactic
        tactic = self.get_current_tactic()
        
        # Build the system prompt
        from personas import PersonaGenerator
        persona_gen = PersonaGenerator()
        system_prompt = persona_gen.get_system_prompt(self.persona)
        
        # Add tactical guidance
        tactic_guidance = self._get_tactic_guidance(tactic)
        
        user_prompt = f"""The scammer just said: "{scammer_message}"

Current situation:
- Conversation turn: {self.turn_count + 1}
- Your current strategy: {tactic}
- Guidance: {tactic_guidance}

Respond naturally as {self.persona['name']}. Remember your goal is to waste their time while staying believable."""

        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history[-6:],  # Keep last 6 messages for context
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.9,
            max_tokens=200
        )
        
        bot_response = response.choices[0].message.content
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": bot_response
        })
        
        self.turn_count += 1
        
        return bot_response
    
    def _get_tactic_guidance(self, tactic):
        """Get specific guidance for each tactic"""
        
        guidance = {
            "technical_difficulty": "Express confusion with technology. Say your computer is slow, you can't find buttons, etc.",
            "need_assistance": "Say you need to ask your grandson/daughter/friend for help with this.",
            "clarification_needed": "Ask them to explain in simpler terms. Act confused about specific details.",
            "distraction": "Go off on a brief tangent about something in your life. Then ask them to repeat what they said.",
            "fake_compliance": "Act like you're going to do it, but create obstacles ('let me find my reading glasses', 'my internet is slow')"
        }
        
        return guidance.get(tactic, "Engage naturally")
    
    def get_conversation_summary(self):
        """Get a summary of the conversation"""
        
        return {
            'total_turns': self.turn_count,
            'final_state': self.state,
            'messages_exchanged': len(self.conversation_history),
            'intelligence_gathered': len(self.intel_log),
            'estimated_time_wasted': f"{self.turn_count * 2} minutes"
        }


# Test it
if __name__ == "__main__":
    from personas import PersonaGenerator
    from intelligence import IntelligenceExtractor
    
    # Create persona
    generator = PersonaGenerator()
    persona = generator.generate_persona("phishing")
    
    print("=== GENERATED PERSONA ===")
    print(f"Name: {persona['name']}")
    print(f"Age: {persona['age']}")
    print(f"Tech Literacy: {persona['tech_literacy']}/10")
    print()
    
    # Create intelligence extractor
    extractor = IntelligenceExtractor()
    
    # Create conversation manager
    manager = ConversationManager(persona, extractor)
    
    # Simulate a conversation
    print("=== SIMULATED CONVERSATION ===\n")
    
    scam_messages = [
        "Hello! This is David from Commonwealth Bank security. We've detected suspicious activity on your account.",
        "Your account will be locked in 24 hours unless you verify your identity immediately.",
        "Please click this link to verify: https://commbank-security-verify.com",
        "Why haven't you clicked the link yet? Your account is at risk!",
        "You need to act now or you'll lose access to all your money!"
    ]
    
    for i, scam_msg in enumerate(scam_messages, 1):
        print(f"SCAMMER (Turn {i}): {scam_msg}")
        response = manager.generate_response(scam_msg)
        print(f"BOT ({persona['name']}): {response}")
        print()
    
    # Show summary
    summary = manager.get_conversation_summary()
    print("CONVERSATION SUMMARY")
    for key, value in summary.items():
        print(f"{key}: {value}")
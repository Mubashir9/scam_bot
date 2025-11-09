import re
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

class IntelligenceExtractor:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Regex patterns for IOCs (Indicators of Compromise)
        self.patterns = {
            'urls': r'https?://[^\s]+',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'crypto_wallet': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            'bank_keywords': r'\b(account|routing|transfer|wire|deposit|bank)\b',
            'urgency_words': r'\b(urgent|immediately|now|expires|limited|today|asap)\b',
            'authority_claims': r'\b(police|IRS|government|microsoft|apple|amazon|bank)\b',
        }
    
    def extract_patterns(self, text):
        """Extract IOCs using regex patterns"""
        iocs = {}
        
        for ioc_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Remove duplicates and store
                iocs[ioc_type] = list(set(matches))
        
        return iocs
    
    def analyze_tactics(self, scammer_message):
        """Use LLM to analyze scammer tactics"""
        
        prompt = f"""Analyze this scammer message and identify the manipulation tactics being used.

Message: "{scammer_message}"

Return ONLY a JSON object with this structure (no markdown):
{{
    "primary_tactic": "main manipulation technique (urgency/authority/fear/greed)",
    "impersonation": "who they're pretending to be (or 'none')",
    "requested_action": "what they want victim to do",
    "pressure_level": number 1-10,
    "sophistication": number 1-10,
    "red_flags": ["list", "of", "obvious", "scam", "indicators"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Clean up markdown if present
            if analysis_text.startswith("```"):
                analysis_text = analysis_text.split("```")[1]
                if analysis_text.startswith("json"):
                    analysis_text = analysis_text[4:]
            
            return json.loads(analysis_text.strip())
        except:
            # Fallback if LLM analysis fails
            return {
                "primary_tactic": "unknown",
                "impersonation": "unknown",
                "requested_action": "unknown",
                "pressure_level": 5,
                "sophistication": 5,
                "red_flags": []
            }
    
    def process_message(self, scammer_message):
        """Full intelligence extraction from a scammer message"""
        
        intel = {
            'timestamp': datetime.now().isoformat(),
            'message': scammer_message,
            'iocs': self.extract_patterns(scammer_message),
            'tactics': self.analyze_tactics(scammer_message)
        }
        
        return intel
    
    def generate_report(self, conversation_intel):
        """Generate a threat intelligence report from full conversation"""
        
        report = {
            'summary': {
                'total_messages': len(conversation_intel),
                'duration_estimate': f"{len(conversation_intel) * 2} minutes",
                'unique_iocs': {}
            },
            'timeline': conversation_intel,
            'threat_profile': {}
        }
        
        # Aggregate IOCs
        all_iocs = {}
        for intel in conversation_intel:
            for ioc_type, values in intel.get('iocs', {}).items():
                if ioc_type not in all_iocs:
                    all_iocs[ioc_type] = []
                all_iocs[ioc_type].extend(values)
        
        # Remove duplicates
        for ioc_type in all_iocs:
            all_iocs[ioc_type] = list(set(all_iocs[ioc_type]))
        
        report['summary']['unique_iocs'] = all_iocs
        
        # Calculate average sophistication
        sophistications = [
            intel['tactics'].get('sophistication', 5) 
            for intel in conversation_intel 
            if 'tactics' in intel
        ]
        
        if sophistications:
            report['threat_profile']['avg_sophistication'] = sum(sophistications) / len(sophistications)
        
        return report


# Test it
if __name__ == "__main__":
    extractor = IntelligenceExtractor()
    
    test_message = """
    URGENT! Your bank account has been compromised. 
    Click here immediately: https://fake-bank-security.com/verify
    Call us at 555-0123 or your account will be locked!
    - Commonwealth Bank Security Team
    """
    
    print("Extracting intelligence from test message...\n")
    intel = extractor.process_message(test_message)
    
    print("EXTRACTED INTELLIGENCE")
    print(json.dumps(intel, indent=2))
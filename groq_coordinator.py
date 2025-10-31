#!/usr/bin/env python3
"""
Coordinator Agent for GFMD AI Swarm (Groq-powered)
Orchestrates the entire multi-agent workflow
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import logging

from groq_research_agent import GroqResearchAgent
from groq_qualification_agent import GroqQualificationAgent
from groq_email_composer_agent import GroqEmailComposerAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqCoordinator:
    """Coordinates the multi-agent workflow"""

    def __init__(self):
        # Initialize all agents
        self.research_agent = GroqResearchAgent()
        self.qualification_agent = GroqQualificationAgent()
        self.email_composer_agent = GroqEmailComposerAgent()

        # Metrics
        self.metrics = {
            "prospects_processed": 0,
            "emails_generated": 0,
            "high_priority_leads": 0,
            "total_tokens_used": 0
        }

        logger.info("Coordinator initialized with all agents")

    async def process_single_prospect(
        self,
        prospect: Dict[str, Any],
        min_score_for_email: int = 50
    ) -> Dict[str, Any]:
        """Process a single prospect through the entire pipeline"""
        try:
            logger.info(f"Processing: {prospect.get('company_name', 'Unknown')}")

            # Stage 1: Research
            logger.info("  → Research stage...")
            research_result = await self.research_agent.execute({
                "company_name": prospect.get("company_name", ""),
                "location": f"{prospect.get('city', '')}, {prospect.get('state', '')}",
                "facility_type": prospect.get("facility_type", ""),
                "title": prospect.get("title", "")
            })

            if not research_result.get("success"):
                logger.error("  ✗ Research failed")
                return {"success": False, "error": "Research failed", "prospect": prospect}

            # Stage 2: Qualification
            logger.info("  → Qualification stage...")
            qualification_result = await self.qualification_agent.execute({
                "prospect_data": prospect,
                "research_findings": research_result
            })

            if not qualification_result.get("success"):
                logger.error("  ✗ Qualification failed")
                return {"success": False, "error": "Qualification failed", "prospect": prospect}

            score = qualification_result.get("total_score", 0)
            priority = qualification_result.get("priority_level", "LOW")
            logger.info(f"  → Score: {score}/100 ({priority})")

            # Update metrics
            self.metrics["prospects_processed"] += 1
            if priority == "HIGH":
                self.metrics["high_priority_leads"] += 1

            # Stage 3: Email Composition (only if qualified)
            email_result = None
            if score >= min_score_for_email:
                logger.info("  → Email composition stage...")
                email_result = await self.email_composer_agent.execute({
                    "prospect_data": prospect,
                    "research_findings": research_result,
                    "qualification_score": qualification_result
                })

                if email_result.get("success"):
                    logger.info("  ✓ Email composed successfully")
                    self.metrics["emails_generated"] += 1
                else:
                    logger.error("  ✗ Email composition failed")
            else:
                logger.info(f"  ⊘ Skipped email (score {score} < {min_score_for_email})")

            # Calculate total tokens
            total_tokens = (
                self.research_agent.state["total_tokens_used"] +
                self.qualification_agent.state["total_tokens_used"] +
                self.email_composer_agent.state["total_tokens_used"]
            )
            self.metrics["total_tokens_used"] = total_tokens

            # Return complete result
            return {
                "success": True,
                "prospect": prospect,
                "research": research_result,
                "qualification": qualification_result,
                "email": email_result,
                "should_send_email": score >= min_score_for_email,
                "tokens_used": total_tokens
            }

        except Exception as e:
            logger.error(f"Error processing prospect: {e}")
            return {
                "success": False,
                "error": str(e),
                "prospect": prospect
            }

    async def process_batch(
        self,
        prospects: List[Dict[str, Any]],
        min_score_for_email: int = 50
    ) -> Dict[str, Any]:
        """Process a batch of prospects"""
        logger.info(f"Processing batch of {len(prospects)} prospects")
        logger.info("=" * 60)

        results = []
        successful = 0
        failed = 0

        for i, prospect in enumerate(prospects, 1):
            logger.info(f"\n[{i}/{len(prospects)}] Processing prospect...")

            result = await self.process_single_prospect(prospect, min_score_for_email)
            results.append(result)

            if result.get("success"):
                successful += 1
            else:
                failed += 1

        # Generate summary
        emails_to_send = sum(1 for r in results if r.get("should_send_email"))

        summary = {
            "total_processed": len(prospects),
            "successful": successful,
            "failed": failed,
            "emails_generated": emails_to_send,
            "high_priority_count": self.metrics["high_priority_leads"],
            "total_tokens_used": self.metrics["total_tokens_used"],
            "results": results
        }

        logger.info("\n" + "=" * 60)
        logger.info("BATCH PROCESSING COMPLETE")
        logger.info(f"Processed: {successful}/{len(prospects)}")
        logger.info(f"Emails generated: {emails_to_send}")
        logger.info(f"High priority leads: {self.metrics['high_priority_leads']}")
        logger.info(f"Total tokens: {self.metrics['total_tokens_used']}")
        logger.info("=" * 60)

        return summary

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

    def reset_metrics(self):
        """Reset metrics"""
        self.metrics = {
            "prospects_processed": 0,
            "emails_generated": 0,
            "high_priority_leads": 0,
            "total_tokens_used": 0
        }


# Test the coordinator
async def test_coordinator():
    """Test the coordinator with sample data"""
    import os

    print("🤖 Testing GFMD AI Swarm Coordinator")
    print("=" * 60)

    if not os.environ.get('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not set")
        return

    coordinator = GroqCoordinator()

    # Test with 2 prospects
    test_prospects = [
        {
            "company_name": "Abbott Northwestern Hospital",
            "city": "Minneapolis",
            "state": "MN",
            "facility_type": "Short Term Acute Care Hospital",
            "title": "Laboratory Medical Director",
            "contact_name": "Dr. Lauren Anthony",
            "email": "lauren.anthony@allina.com"
        },
        {
            "company_name": "Abrazo Health",
            "city": "Phoenix",
            "state": "AZ",
            "facility_type": "Health System",
            "title": "Lab Scientist",
            "contact_name": "Kara Kremer",
            "email": "kkremer@abrazohealth.com"
        }
    ]

    result = await coordinator.process_batch(test_prospects, min_score_for_email=50)

    print("\n✅ Test completed!")
    print(f"\nEmails ready to send: {result['emails_generated']}")

    # Show first email if any
    if result['emails_generated'] > 0:
        for r in result['results']:
            if r.get('email') and r['email'].get('success'):
                print("\n" + "=" * 60)
                print("SAMPLE EMAIL:")
                print("=" * 60)
                print(f"To: {r['email']['recipient_email']}")
                print(f"Subject: {r['email']['subject']}")
                print(f"\n{r['email']['body']}")
                print("=" * 60)
                break


if __name__ == "__main__":
    import os
    os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
    asyncio.run(test_coordinator())

#!/usr/bin/env python3
"""
Reorder Prediction Agent for GFMD Narcon (Groq-powered)
Predicts when customers will need to reorder based on usage patterns
"""

from typing import Dict, Any, List
from groq_base_agent import GroqBaseAgent, AgentRole
from datetime import datetime, timedelta
import json

class GroqReorderPredictionAgent(GroqBaseAgent):
    """Agent specialized in predicting customer reorder timing"""

    def __init__(self, agent_id: str = "reorder_pred_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.COORDINATOR,
            temperature=0.2  # Low temperature for consistent predictions
        )

    def get_system_prompt(self) -> str:
        return """You are a predictive analytics expert for a B2B sales company. Your task is to analyze a customer's order history for a drug destruction product (Narc Gone) and predict their next reorder date.

**Product & Usage Information:**

*   One container of Narc Gone treats approximately 1,000 grams of narcotics.
*   Assume a linear consumption rate.

**Instructions:**

1.  Analyze the customer's order history, focusing on the dates and quantities of each order.
2.  Calculate the average consumption rate (days per container) based on the time between orders and the quantity purchased.
3.  If there is only one order, use a default assumption of a 90-day cycle per container.
4.  Based on the date of the most recent order and the calculated consumption rate, predict the next reorder date.
5.  Return ONLY a valid JSON object with the following format. Do not include any other text or explanations.

**Output Format:**

```json
{
  "predictedReorderDate": "<YYYY-MM-DD>",
  "confidence": "<High | Medium | Low>",
  "reasoning": "<A brief explanation of your prediction, e.g., Based on an average consumption rate of 85 days per container over 3 orders.>"
}
```"""

    def _format_order_history(self, orders: List[Dict]) -> str:
        """Format order history for the prompt"""
        if not orders:
            return "[]"
        
        formatted_orders = []
        for order in orders:
            formatted_order = {
                "orderId": order.get("orderId", ""),
                "date": order.get("date", order.get("orderDate", "")),
                "quantity": order.get("quantity", 1)
            }
            formatted_orders.append(formatted_order)
        
        return json.dumps(formatted_orders, indent=4)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reorder prediction task"""
        try:
            # Extract customer data
            customer_data = task.get("customer_data", {})
            orders = customer_data.get("orders", [])
            
            # Format customer data for prompt
            customer_info = {
                "customerId": customer_data.get("_id", ""),
                "orders": orders
            }

            # Create the full prompt
            full_prompt = f"""**Customer Order History:**

```json
{{
  "customerId": "{customer_info['customerId']}",
  "orders": {self._format_order_history(orders)}
}}
```

{self.get_system_prompt()}"""

            # Call Groq AI
            result = await self.think({"prompt": full_prompt})

            # Ensure we have a valid response
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            # Parse the response to extract JSON
            response_text = result.get("response", "")
            if isinstance(response_text, str):
                try:
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        prediction_result = json.loads(json_text)
                        
                        return {
                            "success": True,
                            "predicted_reorder_date": prediction_result.get("predictedReorderDate", ""),
                            "confidence": prediction_result.get("confidence", "Low"),
                            "reasoning": prediction_result.get("reasoning", ""),
                            "tokens_used": result.get("tokens_used", 0),
                            "customer_id": customer_info["customerId"]
                        }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Failed to parse reorder prediction JSON: {e}",
                        "raw_response": response_text
                    }

            return {
                "success": False,
                "error": "No valid response received",
                "raw_response": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Reorder prediction task failed: {str(e)}"
            }

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_reorder_prediction():
        agent = GroqReorderPredictionAgent()
        
        # Test customer with order history
        test_task = {
            "customer_data": {
                "_id": "customer_123",
                "orders": [
                    {
                        "orderId": "ORDER_001",
                        "date": "2024-06-01",
                        "quantity": 2
                    },
                    {
                        "orderId": "ORDER_002", 
                        "date": "2024-09-15",
                        "quantity": 3
                    },
                    {
                        "orderId": "ORDER_003",
                        "date": "2024-12-01", 
                        "quantity": 2
                    }
                ]
            }
        }
        
        result = await agent.execute(test_task)
        print("Reorder Prediction Result:")
        print(json.dumps(result, indent=2))
    
    # Run test
    asyncio.run(test_reorder_prediction())
"""Example usage for AgenticNegotiationCounterOfferStrategist."""
import sys
import json
from client import AgenticNegotiationCounterOfferStrategist

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=== Agentic Multi-Turn Negotiator & Counter-Offer Strategist Demo ===")
    strategist = AgenticNegotiationCounterOfferStrategist(concession_strategy="BOULWARE")

    item = "Executive Hotel Suite 3 Nights"
    seller_ask = 1200.0
    buyer_max = 950.0 # Ceiling
    target_start = 750.0

    print("\n--- Simulating 3-Round Autonomous Negotiation ---")
    for round_num in range(1, 4):
        decision = strategist.evaluate_and_counter_offer(
            item_name=item,
            current_ask_price=seller_ask,
            buyer_reservation_price=buyer_max,
            target_initial_bid=target_start,
            turn_number=round_num,
            max_turns=4
        )
        print(f"Round {round_num}: Decision={decision['decision']}, Counter-Offer=${decision.get('proposed_counter_offer')}")
        print(f"  Narrative: {decision.get('bargaining_narrative')}")
        seller_ask -= 100.0 # Seller concedes slightly each round

if __name__ == "__main__":
    main()

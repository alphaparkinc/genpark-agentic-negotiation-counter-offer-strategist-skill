"""
Autonomous Agentic Multi-Turn Negotiator & Counter-Offer Strategist (Zero External Dependencies)
Provides ZOPA calculation, concession decay functions (Boulware vs Conceder), and deal closure.
"""
import time
import math
import hashlib
import json
from typing import Dict, Any, List, Optional

class AgenticNegotiationCounterOfferStrategist:
    def __init__(self, concession_strategy: str = "BOULWARE"): # BOULWARE = firm early, concedes late
        self.strategy = concession_strategy

    def calculate_zopa_range(
        self,
        buyer_reservation_price: float,
        seller_estimated_reservation: float
    ) -> Dict[str, Any]:
        """Calculates Zone of Possible Agreement (ZOPA)."""
        zopa_exists = buyer_reservation_price >= seller_estimated_reservation
        spread = max(0.0, buyer_reservation_price - seller_estimated_reservation)
        return {
            "zopa_exists": zopa_exists,
            "zopa_spread_usd": round(spread, 2),
            "seller_floor_est": seller_estimated_reservation,
            "buyer_ceiling": buyer_reservation_price
        }

    def evaluate_and_counter_offer(
        self,
        item_name: str,
        current_ask_price: float,
        buyer_reservation_price: float,
        target_initial_bid: float,
        turn_number: int = 1,
        max_turns: int = 4
    ) -> Dict[str, Any]:
        """
        Evaluates incoming seller ask and computes mathematically disciplined counter-offer.
        If seller ask <= buyer reservation, evaluates potential deal acceptance.
        """
        # If seller price already meets or beats initial bid
        if current_ask_price <= target_initial_bid:
            return {
                "decision": "ACCEPT_DEAL",
                "agreed_price": current_ask_price,
                "reason": "Seller ask is at or below target initial price",
                "savings_vs_ceiling": round(buyer_reservation_price - current_ask_price, 2)
            }

        # If turn limit reached
        if turn_number >= max_turns:
            if current_ask_price <= buyer_reservation_price:
                return {
                    "decision": "ACCEPT_DEAL_FINAL_ROUND",
                    "agreed_price": current_ask_price,
                    "reason": "Final turn reached within reservation boundary"
                }
            else:
                return {
                    "decision": "WALK_AWAY",
                    "reason": f"Seller price ${current_ask_price} exceeds buyer ceiling ${buyer_reservation_price}"
                }

        # Time-based concession factor (0.0 to 1.0)
        t_ratio = min(1.0, float(turn_number) / float(max_turns))
        beta = 2.0 if self.strategy == "BOULWARE" else 0.5 # Boulware holds firm early
        concession_progress = math.pow(t_ratio, beta)

        # Counter-offer formula: Initial + (Reservation - Initial) * progress
        counter_offer = target_initial_bid + (buyer_reservation_price - target_initial_bid) * concession_progress
        counter_offer = round(min(counter_offer, buyer_reservation_price, current_ask_price - 1.0), 2)

        # Formulate persuasive rationale
        diff_pct = round(((current_ask_price - counter_offer) / current_ask_price) * 100.0, 1)

        return {
            "decision": "COUNTER_OFFER",
            "turn_number": turn_number,
            "max_turns": max_turns,
            "seller_ask": current_ask_price,
            "proposed_counter_offer": counter_offer,
            "discount_requested_pct": diff_pct,
            "concession_progress": round(concession_progress, 3),
            "bargaining_narrative": (
                f"We appreciate the offer of ${current_ask_price} for {item_name}. "
                f"Based on real-time market inventory and immediate guaranteed settlement, "
                f"our authorized counter-offer is ${counter_offer}."
            )
        }

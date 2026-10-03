"""MCP Server for Agentic Negotiation Counter-Offer Strategist."""
import sys
import json
import time
from client import AgenticNegotiationCounterOfferStrategist

strategist = AgenticNegotiationCounterOfferStrategist()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "negotiate_counter_offer":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "evaluate_and_counter_offer")
    if action == "evaluate_and_counter_offer":
        return strategist.evaluate_and_counter_offer(
            item_name=args.get("item_name", "Service Contract"),
            current_ask_price=float(args.get("current_ask_price", 100.0)),
            buyer_reservation_price=float(args.get("buyer_reservation_price", 90.0)),
            target_initial_bid=float(args.get("target_initial_bid", 70.0)),
            turn_number=int(args.get("turn_number", 1)),
            max_turns=int(args.get("max_turns", 4))
        )
    elif action == "calculate_zopa_range":
        return strategist.calculate_zopa_range(
            buyer_reservation_price=float(args.get("buyer_reservation_price", 100.0)),
            seller_estimated_reservation=float(args.get("current_ask_price", 80.0))
        )
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        res = strategist.evaluate_and_counter_offer("Camera Lens", 500.0, 450.0, 380.0, turn_number=1, max_turns=4)
        assert res["decision"] == "COUNTER_OFFER"
        assert res["proposed_counter_offer"] <= 450.0
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "AgenticNegotiationCounterOfferStrategist", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "negotiate_counter_offer",
                            "description": "Autonomous multi-turn negotiation: analyze seller bids, calculate ZOPA bargaining range, apply concession curves, and formulate optimal counter-offers.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["evaluate_and_counter_offer", "calculate_zopa_range"]},
                                    "item_name": {"type": "string"},
                                    "current_ask_price": {"type": "number"},
                                    "buyer_reservation_price": {"type": "number"},
                                    "target_initial_bid": {"type": "number"},
                                    "turn_number": {"type": "integer"},
                                    "max_turns": {"type": "integer"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()

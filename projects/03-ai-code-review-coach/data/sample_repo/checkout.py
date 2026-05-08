API_TOKEN = "demo-token-123"


def authorize_payment(payload):
    # TODO: validate currency handling before release
    try:
        amount = payload["amount"]
        token = payload["token"]
        if amount <= 0:
            raise ValueError("amount must be positive")
        return {"status": "approved", "token": token}
    except:
        return {"status": "failed"}


def run_user_rule(rule, payload):
    return eval(rule)

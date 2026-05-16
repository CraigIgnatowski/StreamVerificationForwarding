# StreamVerificationForwarding

An agentic AI pipeline that monitors Gmail for streaming service verification code emails and forwards the codes to family members via SMS.

## What it does

1. Monitors Gmail for verification code emails from streaming services (Netflix, Hulu, Disney+, Max, Prime Video, etc.)
2. Extracts the 4-8 digit verification code using an LLM with structured output
3. Infers the requester's location from the email body (most services include "sign-in from City, ST")
4. Texts the code to relevant family members via Twilio SMS
5. Family roster is maintained in `config/family.csv` (name, phone, location_city)

## Tech stack

- Python
- LangChain / LangGraph (agent orchestration)
- Gmail API via `google-api-python-client` (OAuth2)
- Twilio (SMS)
- `python-dotenv`, `pandas`

## Project structure

```
StreamVerificationForwarding/
├── .env                    # secrets (gitignored)
├── credentials.json        # Gmail OAuth client secrets (gitignored)
├── token.json              # Gmail OAuth token (gitignored)
├── config/
│   └── family.csv          # family roster: name, phone, location_city
├── src/
│   ├── main.py             # entry point
│   ├── agent.py            # LangGraph agent and state graph
│   ├── email_client.py     # Gmail API wrapper
│   ├── sms.py              # Twilio wrapper
│   └── utils.py
├── tests/
├── logs/
├── gmail_auth_test.py      # standalone Gmail OAuth test (run this first)
└── requirements.txt
```

## Build order

- [x] Project structure and dependencies
- [ ] Gmail API OAuth working (`gmail_auth_test.py`)
- [ ] Collect 5-10 sample verification emails as test fixtures (`samples/`, gitignored)
- [ ] LLM extraction prompt returning structured JSON (service, code, requester_location, confidence)
- [ ] Family CSV loader (`load_family() -> list[dict]`)
- [ ] Twilio standalone SMS test
- [ ] Wire everything with LangGraph state machine

## LangGraph node plan

`classify_email` → `extract_code` → `identify_service` → `check_context` → `decide_action` → `dispatch_sms` → `log`

## Key design decisions

- **Pre-filter before LLM calls:** check sender domain and subject keywords first to avoid burning API tokens on irrelevant emails
- **Location-based routing:** infer which family member triggered the code from the location mentioned in the email body
- **Sender domain whitelist:** guard against phishing emails tricking the agent into texting codes to attackers
- **Latency matters:** verification codes expire in ~5-10 minutes; keep the pipeline fast

## Error handling style

Functions that can fail and are called from `__main__` or an orchestration layer should return `(result, error)` tuples with descriptive error strings rather than letting exceptions propagate raw.

## Secrets (never commit these)

- `.env` — API keys (Twilio, OpenAI/Anthropic)
- `credentials.json` — Gmail OAuth client secrets
- `token.json` — Gmail OAuth token
- `samples/` — real emails that may contain personal info

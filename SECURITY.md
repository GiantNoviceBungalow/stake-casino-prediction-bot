# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | yes (security only) |
| < 0.3   | no        |

## Reporting a vulnerability

Email `security@stake-predict.dev` with a PGP-encrypted report. Do not open
a public issue for anything that could allow remote code execution or seed
leakage. We triage within 72 hours.

## Threat model

stake-casino-prediction-bot runs entirely on the operator's Windows machine.
It reads round history from a local SQLite cache and optionally polls public
Stake endpoints. It does **not**:

- Authenticate as you against Stake.
- Hold or transmit your account session cookies.
- Place bets on your behalf.

If you find a path where a crafted round payload can execute code inside the
predictor process, that is a P0. Send it in.

## Secrets

Never commit `.env`. The loader in `src/stake_predict/config/settings.py`
reads from environment first, then `config/local.yaml`, and refuses to start
if a production-looking key is hardcoded.
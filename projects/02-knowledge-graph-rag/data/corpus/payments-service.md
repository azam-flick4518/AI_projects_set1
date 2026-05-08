# Payments Service

System: payments-api
Owner: payments-platform
Depends-On: token-vault, fraud-scoring-api
Policy: payment-token-policy, customer-data-handling
Data: payment token, authorization result
SLO: 99.95 payment authorization availability

## Overview

payments-api validates payment tokens and requests authorization from external payment providers.

## Operational Notes

payments-api owns token validation behavior. Token validation changes require review against the payment-token-policy before rollout.

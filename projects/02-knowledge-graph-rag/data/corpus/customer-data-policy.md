# Customer Data Handling Policy

System: customer-data-policy
Owner: security-compliance
Policy: customer-data-handling
Data: customer profile, payment token, order

## Requirements

Services that handle customer profile data, order data, or payment tokens must encrypt data at rest, minimize retention, and provide audit logs for privileged access.

## Review

Any new service handling payment tokens must complete security review before production rollout.

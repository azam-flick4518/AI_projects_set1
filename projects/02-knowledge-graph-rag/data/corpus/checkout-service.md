# Checkout Service

System: checkout-api
Owner: commerce-platform
Depends-On: payments-api, customer-profile-api
Policy: customer-data-handling
Data: customer profile, order, payment token
SLO: 99.9 checkout creation availability

## Overview

checkout-api creates customer orders and coordinates payment authorization. It receives cart details, customer identity, and payment tokens from the storefront.

## Operational Notes

checkout-api should degrade gracefully if customer-profile-api is slow. It must not persist raw payment tokens after authorization.

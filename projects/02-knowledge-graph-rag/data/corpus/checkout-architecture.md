# Checkout Architecture

System: checkout-platform
Owner: commerce-platform
Depends-On: checkout-api, payments-api, customer-profile-api
Policy: customer-data-handling
Data: customer profile, order, payment token

## Request Flow

The storefront calls checkout-api. checkout-api validates customer profile state through customer-profile-api, then calls payments-api for token validation and authorization.

## Reliability

Checkout incident reviews should inspect checkout-api, payments-api, and customer-profile-api together because failures often cross service boundaries.

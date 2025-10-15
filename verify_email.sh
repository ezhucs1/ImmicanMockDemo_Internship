#!/bin/bash

# Email Verification Helper Script
# Usage: ./verify_email.sh <email>

if [ $# -eq 0 ]; then
    echo "Usage: $0 <email>"
    echo "Example: $0 user@example.com"
    exit 1
fi

EMAIL="$1"

echo "🔍 Verifying email for: $EMAIL"

# Update email_verified to true for the user
docker exec immican_db psql -U appuser -d appdb -c "
UPDATE users_login 
SET email_verified = TRUE 
WHERE email = '$EMAIL';
"

# Check if the update was successful
RESULT=$(docker exec immican_db psql -U appuser -d appdb -t -c "
SELECT email_verified 
FROM users_login 
WHERE email = '$EMAIL';
" | tr -d ' ')

if [ "$RESULT" = "t" ]; then
    echo "✅ Email verified successfully for $EMAIL"
    echo "The user can now login to their account."
else
    echo "❌ Failed to verify email for $EMAIL"
    echo "User might not exist in the database."
fi

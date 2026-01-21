
#!/bin/bash

# Configuration
URL="http://localhost:8000"
TOKEN="test_token"

echo "🚀 Starting Asana Replica Full Lifecycle Demo..."
echo "------------------------------------------------"

# Function to check status code
check_status() {
    if [[ "$1" =~ ^2 ]]; then
        echo "✅ Success ($1)"
    else
        echo "❌ Failed with status $1"
        # exit 1 
    fi
}

echo "\n--- 1. AUTHENTICATION ---"
echo "Requesting User Info..."
USER_RESP=$(curl -s -w "\n%{http_code}" -X GET "$URL/users/me" -H "Authorization: Bearer $TOKEN")
USER_BODY=$(echo "$USER_RESP" | sed '$d')
USER_CODE=$(echo "$USER_RESP" | tail -n 1)
check_status "$USER_CODE"
echo "User: $(echo $USER_BODY | grep -o '"name":"[^"]*"' | cut -d'"' -f4)"

echo "\n--- 2. WORKSPACE ---"
echo "Creating a new Workspace..."
WS_RESP=$(curl -s -w "\n%{http_code}" -X POST "$URL/workspaces" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "Engineering Team", "resource_type": "workspace"}}')
WS_BODY=$(echo "$WS_RESP" | sed '$d')
WS_CODE=$(echo "$WS_RESP" | tail -n 1)
check_status "$WS_CODE"

WS_GID=$(echo $WS_BODY | grep -o '"gid":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "➡️  Created Workspace GID: $WS_GID"

echo "\n--- 3. PROJECT ---"
echo "Creating a Project in Workspace $WS_GID..."
PROJ_RESP=$(curl -s -w "\n%{http_code}" -X POST "$URL/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\": {\"name\": \"Q1 Roadmap\", \"workspace\": \"$WS_GID\", \"resource_type\": \"project\"}}")
PROJ_BODY=$(echo "$PROJ_RESP" | sed '$d')
PROJ_CODE=$(echo "$PROJ_RESP" | tail -n 1)
check_status "$PROJ_CODE"

PROJ_GID=$(echo $PROJ_BODY | grep -o '"gid":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "➡️  Created Project GID: $PROJ_GID"

echo "\n--- 4. TASK CREATION ---"
echo "Creating Task 1..."
TASK1_RESP=$(curl -s -w "\n%{http_code}" -X POST "$URL/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\": {\"name\": \"Design Database Schema\", \"project\": \"$PROJ_GID\", \"resource_type\": \"task\"}}")
TASK1_GID=$(echo "$TASK1_RESP" | sed '$d' | grep -o '"gid":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "➡️  Created Task 1 GID: $TASK1_GID"

echo "Creating Task 2..."
TASK2_RESP=$(curl -s -w "\n%{http_code}" -X POST "$URL/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\": {\"name\": \"Implement API\", \"project\": \"$PROJ_GID\", \"resource_type\": \"task\"}}")
TASK2_GID=$(echo "$TASK2_RESP" | sed '$d' | grep -o '"gid":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "➡️  Created Task 2 GID: $TASK2_GID"

echo "\n--- 5. LIST OPERATIONS ---"
echo "Listing all tasks in Project $PROJ_GID..."
LIST_RESP=$(curl -s -X GET "$URL/tasks?project=$PROJ_GID" -H "Authorization: Bearer $TOKEN")
COUNT=$(echo $LIST_RESP | grep -o '"gid"' | wc -l)
echo "➡️  Found $COUNT tasks in project."

echo "\n--- 6. TASK UPDATE ---"
echo "Marking Task 1 ($TASK1_GID) as Completed..."
UPDATE_RESP=$(curl -s -w "\n%{http_code}" -X PUT "$URL/tasks/$TASK1_GID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"completed": true}}')
UPDATE_CODE=$(echo "$UPDATE_RESP" | tail -n 1)
check_status "$UPDATE_CODE"
echo "➡️  Task Update Confirmed."

echo "\n--- 7. TASK DELETION ---"
echo "Deleting Task 2 ($TASK2_GID)..."
DEL_RESP=$(curl -s -w "\n%{http_code}" -X DELETE "$URL/tasks/$TASK2_GID" \
  -H "Authorization: Bearer $TOKEN")
DEL_CODE=$(echo "$DEL_RESP" | tail -n 1)
check_status "$DEL_CODE"

echo "Verifying Deletion (Should be 404)..."
VERIFY_RESP=$(curl -s -w "\n%{http_code}" -X GET "$URL/tasks/$TASK2_GID" \
  -H "Authorization: Bearer $TOKEN")
VERIFY_CODE=$(echo "$VERIFY_RESP" | tail -n 1)

if [[ "$VERIFY_CODE" == "404" ]]; then
    echo "✅ Verification Success: Task Not Found (404)"
else
    echo "❌ Verification Failed: Got $VERIFY_CODE"
fi

echo "\n------------------------------------------------"
echo "🎉 Full Lifecycle Demo Complete!"

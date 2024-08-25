
#!/bin/bash

# Check if the USER_ID environment variable is set
if [ -n "$USER_ID" ]; then
  usermod -u $USER_ID eventscraper
fi


if [ -n "$GROUP_ID" ]; then
  groupadd -g $GROUP_ID eventscraperg
  usermod -g eventscraperg eventscraper
fi

poetry run python /app/src/Runner.py


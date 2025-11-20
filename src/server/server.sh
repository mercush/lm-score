#!/bin/bash

# Load .env file
cat .env | xargs > /dev/null
echo "ENSEMBLE: $ENSEMBLE"
echo "AGGREGATION: $AGGREGATION"
echo "THINKING: $THINKING"

# Check THINKING variable from environment
if [ "$THINKING" = "t" ]; then
    mlx_lm.server \
        --model "$MODEL" \
        --max-tokens 4000
else
    mlx_lm.server \
        --model "$MODEL" \
        --max-tokens 4000 \
        --chat-template "$(cat src/server/chat.template)"
fi

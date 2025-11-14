#!/bin/bash
# Script to create PR for P2 features

gh pr create \
  --base main \
  --head claude/comprehensive-review-restart-017QTY4wy65TWGDhohWEHWVL \
  --title "P2 Features Complete: Performance (93x faster), Benchmarks & Memory System" \
  --body-file PR_P2_SUMMARY.md

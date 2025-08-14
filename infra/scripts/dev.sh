#!/usr/bin/env bash
set -euo pipefail
echo "Frontend:"
( cd ../../CardTraders-frontend/frontend && npx expo start )

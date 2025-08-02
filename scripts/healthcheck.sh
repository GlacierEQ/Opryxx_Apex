#!/usr/bin/env bash
curl -fsSL http://localhost:3000/api/health || exit 1

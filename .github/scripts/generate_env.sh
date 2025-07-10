#!/bin/bash
set -e

echo "DATABASE_URL=sqlite+aiosqlite:///./app.db" > .env
echo "APP_NAME='SWAPI Voting API'" >> .env
echo "APP_VERSION=${1}" >> .env
echo "DEFAULT_PAGE_SIZE=20" >> .env
echo "SWAPI_BASE_URL=https://swapi.info/api" >> .env
echo "VERIFY_SWAPI_SSL=True" >> .env
echo "UPSTASH_REDIS_URL=${2}" >> .env

echo ".env generated (sensitive values hidden):"
cat .env | grep -v UPSTASH_REDIS_URL

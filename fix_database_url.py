"""
Script to update DATABASE_URL environment variable on Render via their API.
The Supabase pooler URL supports IPv4 which is required on Render Free tier.
"""
import requests

# Render API - get your API key from https://dashboard.render.com/u/settings#apikeys
# Since we don't have the API key, print instructions instead
print("=== DATABASE_URL FIX FOR RENDER ===")
print()
print("The current DATABASE_URL uses direct connection (port 5432) which doesn't work on Render Free tier.")
print("You need to update it in Render dashboard to use the Supabase CONNECTION POOLER.")
print()
print("1. Go to: https://dashboard.render.com/web/srv-d7ec7ld7vvec73f5is30/settings")
print("2. Click 'Environment'")
print("3. Find DATABASE_URL and update it to:")
print()
# Use env var so credentials are never hardcoded in source code
POOLER_URL = "<set DATABASE_URL in Render environment>"
print(f"  {POOLER_URL}")
print()
print("4. Click 'Save Changes'")
print("5. Click 'Manual Deploy' > 'Deploy latest commit'")
print()
print("This uses Supabase's connection POOLER which supports IPv4 (required by Render Free tier).")

#!/usr/bin/env python3
"""Fetch public NKT data from Chess.com PubAPI and write data.json."""
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

CLUB_SLUG = "nashediyon-ki-toli-nkt"
BASE = "https://api.chess.com/pub"
USER_AGENT = os.environ.get(
    "CHESSCOM_USER_AGENT",
    "NKT-Community-Sidebar/1.0 (GitHub Pages; public club statistics)"
)
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.json")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})


def get_json(url):
    response = SESSION.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def username_from_url(url):
    return urlparse(url).path.rstrip("/").split("/")[-1]


def latest_members(member_data):
    found = {}
    for group in ("weekly", "monthly", "all_time"):
        for member in member_data.get(group, []) or []:
            username = member.get("username")
            joined = member.get("joined")
            if username and joined:
                old = found.get(username.lower())
                if old is None or int(joined) > int(old["joined"]):
                    found[username.lower()] = {"username": username, "joined": int(joined)}
    return sorted(found.values(), key=lambda x: x["joined"], reverse=True)[:3]


def player_public_data(username):
    try:
        data = get_json(f"{BASE}/player/{username}")
        return {
            "username": data.get("username", username),
            "joined": None,
            "url": data.get("url") or f"https://www.chess.com/member/{username}",
            "avatar": data.get("avatar") or ""
        }
    except requests.RequestException as exc:
        print(f"Player profile unavailable for {username}: {exc}", file=sys.stderr)
        return {
            "username": username,
            "joined": None,
            "url": f"https://www.chess.com/member/{username}",
            "avatar": ""
        }


def get_next_registered_match(matches):
    now = int(time.time())
    candidates = []
    for match in matches.get("registered", []) or []:
        start = match.get("start_time")
        match_url = match.get("@id") or match.get("id")
        if start and int(start) > now and match_url:
            candidates.append({
                "name": match.get("name") or "NKT team match",
                "start_time": int(start),
                "url": match_url
            })
    return min(candidates, key=lambda x: x["start_time"]) if candidates else None


def main():
    club_url = f"{BASE}/club/{CLUB_SLUG}"
    members_url = f"{club_url}/members"
    matches_url = f"{club_url}/matches"

    # Serial requests: Chess.com advises avoiding parallel bursts.
    club = get_json(club_url)
    time.sleep(1)
    members = get_json(members_url)
    time.sleep(1)
    matches = get_json(matches_url)

    newest = latest_members(members)
    profiles = []
    for member in newest:
        profile = player_public_data(member["username"])
        profile["joined"] = member["joined"]
        profiles.append(profile)
        time.sleep(1)

    data = {
        "source": "Chess.com Published-Data API",
        "club_slug": CLUB_SLUG,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "club": {
            "name": club.get("name"),
            "members_count": club.get("members_count"),
            "average_daily_rating": club.get("average_daily_rating"),
            "created": club.get("created"),
            "url": club.get("@id") or f"https://www.chess.com/club/{CLUB_SLUG}"
        },
        "latest_members": profiles,
        "next_team_match": get_next_registered_match(matches)
    }

    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, OUT)
    print(f"Updated {OUT}; latest members: {len(profiles)}; upcoming registered team match: {bool(data['next_team_match'])}")


if __name__ == "__main__":
    main()

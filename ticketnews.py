import json
import os
from datetime import datetime

import feedparser
import requests
from decouple import config


class SlackMessage:
    def __init__(self):
        self.mods_webhook = config("MODS_SLACK_WEBHOOK")

    def post(self, message):
        slack_msg = {
            "blocks": [
                {"type": "divider"},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"{message}"}},
            ],
        }
        requests.post(self.mods_webhook, data=json.dumps(slack_msg))


def main():
    filename = os.path.abspath("last_ticketsnews_rss.txt")
    with open(filename, "r") as f:
        latest_rss_link = f.read()

    response = feedparser.parse("https://www.ticketnews.com/feed/")

    entries = response["entries"]
    links = [entry["links"][0]["href"] for entry in entries]
    new_posts = []
    for link in links:
        if link != latest_rss_link:
            new_posts.append(link)
        else:
            break

    if len(new_posts):
        with open(filename, "w") as f:
            f.write(new_posts[0])

        slack = SlackMessage()
        for post in new_posts:
            slack.post(post)

    msg = f"[{datetime.utcnow()}] {len(new_posts)} new posts found: {new_posts}\n"
    log_filename = os.path.abspath("cron.log")
    with open(log_filename, "a") as f:
        f.write(msg)
    print(msg)


if __name__ == "__main__":
    print("Starting TicketNews.com script...")
    main()

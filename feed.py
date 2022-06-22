from cmath import log
import re
from pydantic import BaseModel, parse_obj_as, AnyUrl
import feedparser
from typing import List, Optional
import pydantic
from bs4 import BeautifulSoup
import config
import time
import logging
from vk_api import VkApi

pattern = re.compile("\s+")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s] %(message)s",
    datefmt='%d/%m/%Y %I:%M:%S %p',
    level=logging.INFO)


class FeedEntry(BaseModel):
    summary: str
    title: str
    link: AnyUrl

    @pydantic.validator("summary", pre=True)
    def text_from_html(cls, v):
        soup = BeautifulSoup(v, features="html.parser")
        text = soup.get_text()
        normalized_text = pattern.sub(" ", text.strip())
        return normalized_text


def fetch_entries() -> List[FeedEntry]:
    data = feedparser.parse("https://export.arxiv.org/rss/cs.PL")
    return parse_obj_as(List[FeedEntry], data.entries)


vk_sess = VkApi(token=config.USER_TOKEN)
vk = vk_sess.get_api()


def fetch_last_posted_link() -> Optional[AnyUrl]:
    logging.info("checking last post")
    try:
        post = vk.wall.get(count=1, owner_id=config.GROUP_ID)['items'][0]
        post_text = post['text']
        return parse_obj_as(AnyUrl, post_text.split('\n')[1])
    except IndexError:
        logging.warning("got no posts, assuming wall is empty")
        return None


def create_post(entry: FeedEntry) -> None:
    logging.info(f"posting {entry.link}")
    text = f"{entry.title}\n{entry.link}\n{entry.summary}"
    vk.wall.post(owner_id=config.GROUP_ID, from_group=1, message=text)


last_post = fetch_last_posted_link()

while True:
    logging.info("checking arxiv")

    entries = fetch_entries()
    logging.info(f"got {len(entries)} entries")
    newest = []
    for entry in entries:
        if last_post is not None and str(entry.link) == str(last_post):
            break
        newest.append(entry)

    for entry in newest[::-1]:
        create_post(entry)

    if newest:
        last_post = newest[0].link

    time.sleep(config.CHECK_INTERVAL_SECS)

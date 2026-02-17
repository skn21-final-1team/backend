import os
from pprint import pprint

from langchain_community.document_loaders import WebBaseLoader

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)
os.environ["USER_AGENT"] = USER_AGENT

loader = WebBaseLoader(
    web_paths=("https://n.news.naver.com/mnews/article/001/0015905696?rc=N&ntype=RANKING",),
    header_template={
        "User-Agent": USER_AGENT,
    },
)

docs = loader.load()

pprint(docs[0])

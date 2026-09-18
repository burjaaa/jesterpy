import asyncio
import functools
import aiohttp

def async_retry(retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        raise e
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class ContentItem:
    def __init__(self, item_id: int, category: str, content_type: str):
        self.item_id = item_id
        self.category = category
        self.content_type = content_type

class Joke(ContentItem):
    def __init__(self, item_id: int, category: str, content_type: str, setup: str = "", delivery: str = "", joke: str = ""):
        super().__init__(item_id, category, content_type)
        self.setup = setup
        self.delivery = delivery
        self.joke = joke

    @property
    def full_text(self) -> str:
        if self.content_type == "twopart":
            return f"{self.setup}\n  -> {self.delivery}"
        return self.joke

    def to_dict(self) -> dict:
        return {
            "id": self.item_id,
            "category": self.category,
            "type": self.content_type,
            "setup": self.setup,
            "delivery": self.delivery,
            "joke": self.joke,
            "full_text": self.full_text
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            item_id=data.get("id", 0),
            category=data.get("category", "Any"),
            content_type=data.get("type", "single"),
            setup=data.get("setup", ""),
            delivery=data.get("delivery", ""),
            joke=data.get("joke", "")
        )

class JokeFetcher:
    BASE_URL = "https://v2.jokeapi.dev/joke/"

    @async_retry(retries=3)
    async def fetch_joke(self, session: aiohttp.ClientSession, category: str = "Any") -> Joke:
        url = f"{self.BASE_URL}{category}?safe-mode"
        
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"API Error: Received status code {resp.status}")
            data = await resp.json()
            if data.get("error"):
                raise ValueError(data.get("message", "Failed to fetch joke."))
            
            if data.get("type") == "twopart":
                return Joke(
                    item_id=data.get("id"),
                    category=data.get("category"),
                    content_type="twopart",
                    setup=data.get("setup"),
                    delivery=data.get("delivery")
                )
            else:
                return Joke(
                    item_id=data.get("id"),
                    category=data.get("category"),
                    content_type="single",
                    joke=data.get("joke")
                )
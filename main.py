import asyncio
import asyncpraw
from telegram import Bot
import random
from aiohttp import ClientTimeout
from environs import Env
env = Env()
env.read_env()
# Telegram Bot setup
telegram_bot = Bot(token=env.str('TOKEN'))
chat_id = env.str('CHAT_ID')
def get_random_subreddits(subreddits):
    return random.sample(subreddits, env.int('SUBREDDITS_COUNT'))
async def get_hot_posts(subreddits, limit=100):
    reddit = asyncpraw.Reddit(
    client_id=env.str('REDDIT_CLIENT_ID'),
    client_secret=env.str('REDDIT_CLIENT_SECRET'),
    user_agent=env.str('REDDIT_USER_AGENT'),
    requestor_kwargs={'timeout': ClientTimeout(total=30)}  
)
    hot_posts = {}
    for subreddit in subreddits:
        subreddit_instance = await reddit.subreddit(subreddit)
        hot_posts[subreddit] = []
        all_posts = []
        async for post in subreddit_instance.hot(limit=limit):
            all_posts.append(post)
        # Sample one random post from the collected list
        random_posts = random.sample(all_posts, 1)
        for post in random_posts:
            title = post.title
            post_url, post_description = None, None
            # Check if there is a preview image
            if hasattr(post, 'url') and post.url:
                post_url = post.url
            if hasattr(post, 'selftext') and post.selftext:
                post_description = post.selftext[:100]
            # Store the result in a dictionary
            if post_url or post_description:
                hot_posts[subreddit].append({
                    'title': title,
                    'post_url': post_url,
                    'post_description': post_description
                })
    return hot_posts
async def send_to_telegram(message):
    await telegram_bot.send_message(chat_id=chat_id, text=message)
async def main():
    subreddits = env.list('SUBREDDITS')

    random_subreddits = get_random_subreddits(subreddits)
    hot_posts = await get_hot_posts(random_subreddits)
    
    for subreddit, posts in hot_posts.items():
        for post in posts:
            message = f"From {subreddit}:\n\n{post['title']}\n\n{post['post_url']}\n\n{post['post_description']}"
            print(message)
            await send_to_telegram(message)

if __name__ == "__main__":
    asyncio.run(main())
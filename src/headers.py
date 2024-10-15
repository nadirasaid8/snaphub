from src.agent import generate_random_user_agent

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "if-none-match": 'W/"2cc-L/KMGs6EOmGfZznp6UXxDllJgL4"',
    "referer": "https://prod.snapster.bot/main",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": generate_random_user_agent(),
}
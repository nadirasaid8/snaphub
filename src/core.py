import os
import aiohttp
import urllib.parse
import json
from colorama import *
from src.headers import headers
from src.deeplchain import (
    countdown_timer, 
    read_config, log_error,
    log, mrh, pth, hju, kng, bru, htm, log_line
    )

init(autoreset=True)
config = read_config()

class SnapsterBot:
    def __init__(self, query_file="data.txt"):
        self.query_file = query_file
        self.headers = headers
        self.query_id = None
        self.user_id = None
        self.use_proxies = config.get('use_proxy', False)
        self.proxies = self.load_proxies() if self.use_proxies else []

    def load_proxies(self):
        proxies_file = os.path.join(os.path.dirname(__file__), '../proxies.txt')
        formatted_proxies = []
        with open(proxies_file, 'r') as file:
            for line in file:
                proxy = line.strip()
                if proxy:
                    if proxy.startswith("socks5://"):
                        formatted_proxies.append(proxy)
                    elif not (proxy.startswith("http://") or proxy.startswith("https://")):
                        formatted_proxies.append(f"http://{proxy}")
                    else:
                        formatted_proxies.append(proxy)
        return formatted_proxies

    async def extract_user_id(self):
        try:
            if self.query_id:
                parsed_query = urllib.parse.parse_qs(self.query_id)
                user_data = parsed_query.get("user", [None])[0]
                if user_data:
                    user_info = json.loads(urllib.parse.unquote(user_data))
                    self.user_id = user_info.get("id")
                else:
                    return None
            else:
                log(mrh + f"User id not found.")
                return None
        except Exception as e:
            log(f"An error occured check http.log")
            log_error(f"{e}")
            return None
        
    async def get_user_data(self, session, proxy):
        if not self.user_id:
            log(mrh + f"User id not found.")
            return
        
        url = f"https://prod.snapster.bot/api/user/getUserByTelegramId"
        payload = {
            "telegramId": str(self.user_id)
        }
        self.headers["telegram-data"] = self.query_id 
        async with session.post(url, headers=self.headers, json=payload, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    user_data = data['data']
                    username = user_data.get('username', 'Unknown')
                    points_count = user_data.get('pointsCount', 0)
                    league = user_data.get('currentLeague').get('title')
                    log(hju + f"Username: {pth}{username}")
                    log(hju + f"Total points: {pth}{points_count}")
                    log(hju + f"Current league: {pth}{league}")
                else:
                    log(mrh + f"Failed to fetch user data.")
            else:
                log(mrh + f"Error: {response.status}")

    async def claim_daily_bonus(self, session, proxy):
        if not self.user_id:
            log(mrh + f"User id not found.")
            return
        
        url_daily_bonus = "https://prod.snapster.bot/api/dailyQuest/claimDailyQuestBonus"
        payload = {
            "telegramId": str(self.user_id)
        }
        self.headers["telegram-data"] = self.query_id
        async with session.post(url_daily_bonus, json=payload, headers=self.headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    points_claimed = data['data']['pointsClaimed']
                    streak_count = data['data']['user']['dailyBonusStreakCount']
                    log(hju + f"Success claimed daily {bru}| Points: {pth}{points_claimed} {hju}| Streak: {pth}{streak_count}")
                else:
                    error_message = data.get('message', 'Unknown error')
                    if 'Not eligible for claiming bonus' in error_message:
                        log(kng + f"You have already checkin today")
                    else:
                        log(mrh + f"Failed to claim daily bonus!")
                        log_error(f"{error_message} {data}")
            else:
                log(mrh + f"Error claiming daily bonus!")
                log_error(f"{response.status}")

    async def claim_league_bonus(self, session, proxy):
        if not self.user_id:
            log(mrh + f"User id not found.")
            return
        
        url_leagues = f"https://prod.snapster.bot/api/user/getLeagues?telegramId={self.user_id}"
        self.headers["telegram-data"] = self.query_id
        async with session.get(url_leagues, headers=self.headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    leagues = data['data']
                    for league in leagues:
                        if league['status'] == 'UNCLAIMED':
                            league_id = league['leagueId']
                            league_title = league['title']
                            bonus_points = league['bonusPoints']
                            
                            result, message = await self._claim_league_bonus(session, proxy, league_id)
                            if result:
                                log(hju + f"Successfully claimed {pth}{bonus_points} {hju}points for {pth}{league_title}.")
                            else:
                                log(mrh + f"Failed to claim bonus for {pth}{league_title}: {mrh}{message}")
                            return
                else:
                    log(mrh + f"Failed to get league information.")
            else:
                log(mrh + f"Error fetching leagues: {response.status}")

    async def _claim_league_bonus(self, session, proxy, league_id):
        url_claim = "https://prod.snapster.bot/api/user/claimLeagueBonus"
        payload = {
            "telegramId": str(self.user_id),
            "leagueId": league_id
        }
        async with session.post(url_claim, json=payload, headers=self.headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    return True, hju + f"Successfully claimed {pth}{data['data']['pointsClaimed']} {hju}points"
                else:
                    error_message = data.get('message', 'Unknown error')
                    return False, error_message
            else:
                return False, f"Error: {response.status}"

    async def claim_mining_bonus(self, session, proxy):
        if not self.user_id:
            log(mrh + f"User id not found")
            return
        
        url = "https://prod.snapster.bot/api/user/claimMiningBonus"
        payload = {
            "telegramId": str(self.user_id)
        }
        self.headers["telegram-data"] = self.query_id
        async with session.post(url, headers=self.headers, json=payload, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    points_claimed = data['data']['pointsClaimed']
                    mining_speed = data['data']['user']['currentLeague']['miningSpeed']
                    log(hju + f"Success claimed Mining | {bru}Points: {pth}{points_claimed} {hju}")
                    log(hju + f"Mining speed: {pth}{mining_speed}x")
                else:
                    log(mrh + f"Failed! {data.get('message', 'Unknown error')}")
            else:
                log(mrh + f"Error: {response.status}")

    async def get_tasks(self, session, proxy):
        if not self.user_id:
            log(mrh + f"User id not found")
            return
        
        url = f"https://prod.snapster.bot/api/quest/getQuests?telegramId={self.user_id}"
        self.headers["telegram-data"] = self.query_id 
        async with session.get(url, headers=self.headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    tasks = data['data']
                    for task in tasks:
                        task_id = task['id']
                        task_name = task['title']
                        task_status = task['status']
                        if task_status == 'EARN':
                            result, message = await self.start_quest(session, proxy, task_id)
                        elif task_status == 'UNCLAIMED':
                            result, message = await self.claim_quest_bonus(session, proxy, task_id)
                        else:
                            result, message = False, hju + f"COMPLETE"
                        
                        log(hju + f"Tasks {pth}{task_name}")
                        log(bru + f"Status: {hju}{task_status} - {kng}{'Started' if task_status == 'EARN' else 'CLAIMED'} {hju}| {pth}{message}")
                else:
                    log(mrh + "Failed to fetch tasks list")
            else:
                log(mrh + f"{response.status}")

    async def start_quest(self, session, proxy, quest_id):
        url = "https://prod.snapster.bot/api/quest/startQuest"
        payload = {
            "telegramId": str(self.user_id),
            "questId": quest_id
        }
        async with session.post(url, json=payload, headers=self.headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    return True, hju + f"Success | {pth}{data['data']['status']}"
                else:
                    error_message = data.get('message', 'Unknown error')
                    if 'Referral Count threshold' in error_message:
                        return False, mrh + f"Not achieved."
                    elif 'The wallet is not' in error_message:
                        return False, mrh + f"Wallet not connected."
                    elif 'Quest not found' in error_message:
                        return False, mrh + f"Failed! Quest not found."
                    else:
                        return False, mrh + f"{error_message}"
            else:
                return False, mrh + f"Error starting quest: {htm}{response.status}"

    async def claim_quest_bonus(self, session, proxy, quest_id):
        url = "https://prod.snapster.bot/api/quest/claimQuestBonus"
        payload = {
            "telegramId": str(self.user_id),
            "questId": quest_id
        }
        async with session.post(url, json=payload, headers=self.headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    return True, hju + f"CLAIMED | Points: {pth}{data['data']['pointsClaimed']}"
                else:
                    error_message = data.get('message', 'Unknown error')
                    if 'already claimed' in error_message.lower():
                        return False, mrh + f"Failed! Bonus already claimed."
                    elif 'Quest not found' in error_message:
                        return False, mrh + f"Failed! Quest not found."
                    else:
                        return False, mrh + f"{error_message}"
            else:
                return False, mrh + f"Error : {response.status}"
        
    async def claim_referral_points(self, session, proxy):
        if not self.user_id:
            log(mrh + f"User id not found.")
            return
        
        url = "https://prod.snapster.bot/api/referral/claimReferralPoints"
        payload = {
            "telegramId": str(self.user_id)
        }
        async with session.post(url, json=payload, headers=self.headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('result'):
                    points_claimed = data['data'].get('pointsClaimed', 0)
                    log(hju + f"Referral reward point | {bru}Points: {pth}{points_claimed}")
                else:
                    log(mrh + f"Failed to claim referral points.")
            else:
                log(f"Error: Failed to claim referral : status {response.status}")

    async def run(self):
        tasks_enabled = config.get("auto_complete_tasks", False)
        delay = config.get("account_delay", 5)
        loop_duration = config.get("loop_countdown", 3800)

        query_ids = []
        try:
            with open(self.query_file, 'r') as file:
                query_ids = [line.strip() for line in file]
        except FileNotFoundError:
            log(f"File {self.query_file} not found!")
            return

        proxy_index = 0
        total = len(query_ids)

        while True:
            async with aiohttp.ClientSession() as session:
                proxy = None
                try:
                    for i, query_id in enumerate(query_ids):
                        self.query_id = query_id

                        log(hju + f"Account {i + 1}/{total}")
                        if self.use_proxies and self.proxies:
                            proxy = self.proxies[proxy_index]
                            if proxy:
                                proxy_host = proxy.split('@')[-1] 
                                log(hju + f"Proxy: {pth}{proxy_host}")
                            else:
                                log("No proxy selected!")
                            proxy_index = (proxy_index + 1) % len(self.proxies)
                        else:
                            log("Proxy usage is not enabled or no proxies available.")

                        log(htm + "~" * 38)

                        await self.extract_user_id()
                        await self.get_user_data(session, proxy)
                        await self.claim_daily_bonus(session, proxy)
                        await self.claim_league_bonus(session, proxy)
                        await self.claim_mining_bonus(session, proxy)

                        if tasks_enabled:
                            await self.get_tasks(session, proxy)
                        else:
                            log(kng + f"Auto complete tasks is not activated!")

                        await self.claim_referral_points(session, proxy)
                        log_line()

                        await countdown_timer(delay)

                    await countdown_timer(loop_duration)

                except (ValueError, AttributeError, KeyError, aiohttp.ClientError) as e:
                    log(f"An error occurred while processing account {query_id + 1}:")
                    log(f"Error: {str(e)}")
                    continue
                except Exception as e:
                    log(f"An unexpected error occurred, check last.log!")
                    log(f"Error: {str(e)}")
                    continue

            proxy_index = 0

async def main():
    bot = SnapsterBot() 
    await bot.run()
import aiohttp
import asyncio
import platform
import sys
import logging
from pprint import pprint
from datetime import datetime, timedelta



URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

class Connect_To_Currency_API:
    def __init__(self, url: str):
        self.url = url
    
    async def get_exchange_rate(self, date: datetime):
        result = {}
        day = date.strftime("%d.%m.%Y")
        session = aiohttp.ClientSession()
        try:
            response = await session.get(self.url + day)
            if response.status == 200:
                temp = await response.json()
                result[str(day)] = {}
                exchange_list = temp["exchangeRate"]
                for currency in exchange_list:
                    if currency["currency"] in ("USD", "EUR"):
                        result[str(day)][currency["currency"]] = {
                            "sale": f"{currency['saleRate']:0.2f}",
                            "purchase": f"{currency['purchaseRate']:0.2f}",
                        }
        except aiohttp.ClientConnectionError as err:
            result = f"Connection error: {self.url}, {err}"
        finally:
            response.close()
        await session.close()
        return result


async def main(days: int, now: datetime):
    connect = Connect_To_Currency_API(URL)
    exchages = []
    for i in range(days):
        day = now - timedelta(days=i)
        result = await connect.get_exchange_rate(day)
        if result:
            logging.info(f"Exchange rate for {day} is {result}")
            exchages.append(result)
        else:
            logging.info(f"Exchange rate for {day} is not found")
    for date in exchages:
        pprint(date)



if __name__ == "__main__":
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            days = int(sys.argv[1])
            if days not in range(1,11):
                logging.warning(f"Invalid number of days: {days}, set to 1")
                days = 1
            asyncio.run(main(days, now))
        except ValueError:
            logging.error("Must be a digit")
            


import aiohttp
import asyncio
import csv

url = "https://4lapy.ru/api/goods_search/"

signs = [
    "2ab208cedd8b1db862af22e63d46fb04",
    "2f5d735f3e33c7dd705eb293f382cca6",
    "16d60596c6f127cfff6b91133c9bad11",
    "d75c5b08714f58a0aaa4e1dda123bfad",
    "37ccacd2ac7fba0dc20bfb5fe1419175",
    "74220cae72c42b8d7f09532bf19333fd",
    "aae131783811cb92a4ee488a76f032b2",
    "b5bdbb268f466e4d6fbea51fde2772fd",
]

city_codes = {"Санкт-Петербург": "0000103664", "Москва": "0000073738"}

pages = list(range(1, 9))

headers = {
    "User-Agent": "v4.5.1(Android 12, Google sdk_gphone64_x86_64)",
    "Version-Build": "223",
    "Authorization": "Basic NGxhcHltb2JpbGU6eEo5dzFRMyhy",
    "X-Apps-Build": "4.5.1(223)",
    "X-Apps-Os": "12",
    "X-Apps-Screen": "2274x1080",
    "X-Apps-Device": "Google sdk_gphone64_x86_64",
    "X-Apps-Location": "lat:37.4219983,lon:-122.084",
    "X-Apps-Additionally": "200",
    "Accept-Encoding": "gzip, deflate, br",
}


async def fetch_data(session, city_code, sign, page):
    params = {
        "filters[categories]": 166,
        "request": "корм для собак",
        "page": page,
        "count": 30,
        "token": "342086efc4b81e16529ac6ea5d9bc651",
        "sign": sign,
    }

    headers["Cookie"] = f"selected_city_code={city_code}"

    async with session.get(url, headers=headers, params=params) as response:
        return await response.json()


async def main():
    async with aiohttp.ClientSession() as session:
        for city_name, city_code in city_codes.items():
            csv_data = []
            tasks = []
            for page in pages:
                for sign in signs:
                    task = fetch_data(session, city_code, sign, page)
                    tasks.append((task, city_name, csv_data))

            # Выполнение всех задач
            results = await asyncio.gather(*[task for task, _, _ in tasks])

            # Обработка полученных данных
            for result, (_, city_name, csv_data) in zip(results, tasks):
                if "data" in result and "goods" in result["data"]:
                    goods = result["data"]["goods"]
                    for item in goods:
                        item_id = item.get("id", "")
                        title = item.get("title", "")
                        webpage = item.get("webpage", "")
                        actual_price = item["price"].get("actual", "")
                        old_price = item["price"].get("old", "")
                        base_price = item["price"].get("basePrice", "")
                        courier_price = item["price"].get("courierPrice", "")
                        subscribe_price = item["price"].get("subscribe", "")
                        single_item_pack_discount_price = item["price"].get(
                            "singleItemPackDiscountPrice", ""
                        )
                        whole_pack_discount_price = item["price"].get(
                            "wholePackDiscountPrice", ""
                        )
                        whole_pack_without_discount_price = item["price"].get(
                            "wholePackWithoutDiscountPrice", ""
                        )
                        brand = item.get("brand_name", "")

                        # Добавляем данные в список
                        csv_data.append(
                            [
                                item_id,
                                title,
                                webpage,
                                actual_price,
                                old_price,
                                base_price,
                                courier_price,
                                subscribe_price,
                                single_item_pack_discount_price,
                                whole_pack_discount_price,
                                whole_pack_without_discount_price,
                                brand,
                            ]
                        )

            # Запись данных в CSV файл для текущего города
            output_filename = f"output_{city_name}.csv"
            with open(output_filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(
                    [
                        "ID",
                        "Title",
                        "URL",
                        "Actual Price",
                        "Old Price",
                        "Base Price",
                        "Courier Price",
                        "Subscribe Price",
                        "Single Item Pack Discount Price",
                        "Whole Pack Discount Price",
                        "Whole Pack Without Discount Price",
                        "Brand",
                    ]
                )
                writer.writerows(csv_data)

            print(f"Данные для {city_name} успешно записаны в {output_filename}.")


# Запуск асинхронной функции main
if __name__ == "__main__":
    asyncio.run(main())

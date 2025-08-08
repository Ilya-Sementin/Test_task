import requests
from bs4 import BeautifulSoup
import re
import math
import csv
import argparse

# удаляем лишние пробелы, переносы строк. Заменяем все ; на , чтобы в файле csv не было разрывов по колонкам. 
def del_sp(line: str) -> str:
    return re.sub(r'[\r\n\s]+', ' ', line).replace(";", ",").strip()

# в последнем столбце может быть список, поэтому нужно его отдельно обрабатывать через цикл
def get_list_customer(row: str) -> list:
    li = []
    items = row.find_all('li', class_='list-branches__li')
    for item in items:
        li.append(item.get_text(strip=True))

    return li

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, required=True, help='Количество тендеров (строк)')
    parser.add_argument('--output', type=str, required=True, help='Имя выходного csv файла')
    args = parser.parse_args()

    file = open(args.output, "w", encoding="utf-8-sig", newline="")
    writer = csv.writer(file, delimiter='|')
    writer.writerow(["№ строки", "№ тендера", "Дата", "Название", "Город", "Регион", "Начальная цена", "Окончание", "Заказчик/Отрасли"])

    # на одной странице 20 строк с записями, поэтому нужно желаемое количество записей
    # поделить на 20 и округлить в большую сторону, так мы загрузим нужное количество страниц.
    count_html_page = math.ceil(args.max / 20)
    base_url = "https://rostender.info/extsearch?page="
    count = 1

    try:
        for page_num in range(1, count_html_page + 1):
            url = base_url + str(page_num)
            response = requests.get(url)
        
            soup = BeautifulSoup(response.text, 'html.parser')
            tender_rows = soup.find_all('article', class_='tender-row')
        
            for row in tender_rows:
                if count > args.max:
                    break

                number = row.find('span', class_='tender__number').get_text(strip=True) if row.find('span', class_='tender__number') else 'Цена не указана'
                date = row.find('span', class_='tender__date-start').get_text(strip=True) if row.find('span', class_='tender__number') else 'Цена не указана'
                name = row.find('a', class_='description tender-info__description tender-info__link').get_text(strip=True) if row.find('a', class_='description tender-info__description tender-info__link') else 'Цена не указана'
                city = row.find('div', class_='line-clamp line-clamp--n3').get_text(strip=True) if row.find('div', class_='line-clamp line-clamp--n3') else 'Цена не указана'
                region = row.find('a', class_='tender__region-link').get_text(strip=True) if row.find('a', class_='tender__region-link') else 'Цена не указана'
                start_price = row.find('div', class_='starting-price__price starting-price--price').get_text(strip=True) if row.find('div', class_='starting-price__price starting-price--price') else 'Цена не указана'
                end_time = row.find('span', class_='tender__countdown-text').get_text() if row.find('span', class_='tender__countdown-text') else 'Цена не указана'
                
                writer.writerow([
                    count,
                    del_sp(number.replace("Тендер", '')),
                    del_sp(date.replace('от', '')),
                    del_sp(name),
                    del_sp(city),
                    del_sp(region),
                    del_sp(start_price.replace("₽", '')),
                    del_sp(end_time.replace('Окончание (МСК) ', '')),
                    *get_list_customer(row)
                ])
                count += 1

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")

    file.close()


if __name__ == '__main__':
    main()
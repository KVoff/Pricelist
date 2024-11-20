"""
Модуль для анализа и обработки прайс-листов.

Основные функции:
- Загрузка данных из CSV-файлов с прайсами.
- Выгрузка данных в HTML-таблицу.
- Поиск позиций по текстовому запросу с интерактивным интерфейсом.
"""

import os
import csv
import logging

from tabulate import tabulate


class PriceAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data = []

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def load_prices(self):
        """
        Загружает данные из CSV-файлов с 'price' в названии, сопоставляет столбцы,
        проверяет обязательные поля ('name', 'price', 'weight'), обрабатывает строки
        и добавляет данные в self.data. Пропущенные строки и ошибки логируются.
        """
        files = [f for f in os.listdir(self.folder_path) if 'price' in f]
        column_mapping = {
            'название': 'name', 'продукт': 'name', 'товар': 'name',
            'наименование': 'name',
            'цена': 'price', 'розница': 'price',
            'фасовка': 'weight', 'масса': 'weight', 'вес': 'weight'
        }

        for file in files:
            file_path = os.path.join(self.folder_path, file)
            try:
                with open(file_path, encoding='utf-8') as csvfile:
                    # разделитель в ТЗ ";" заменен на "," для
                    # предоставленных файлов
                    reader = csv.DictReader(csvfile, delimiter=',')

                    columns = {}
                    for col in reader.fieldnames:
                        mapped_col = column_mapping.get(col.lower(), None)
                        if mapped_col:
                            columns[mapped_col] = col

                    required_columns = ['name', 'price', 'weight']
                    missing_columns = [col for col in required_columns if
                                       col not in columns]
                    if missing_columns:
                        logging.warning(
                            f"Файл {file} пропущен из-за отсутствия столбцов: "
                            f"{', '.join(missing_columns)}")
                        continue

                    for row in reader:
                        try:
                            name = row[columns['name']].strip()
                            price = float(row[columns['price']].strip())
                            weight = float(row[columns['weight']].strip())
                            price_per_kg = price / weight
                            self.data.append(
                                (name, price, weight, file, price_per_kg))

                        except (KeyError, ValueError, TypeError) as e:
                            logging.error(
                                f"Ошибка обработки строки в файле {file}: {e}. "
                                f"Строка пропущена.")
                            continue

            except Exception as e:
                logging.error(f"Ошибка при открытии файла {file}: {e}")

    def find_text(self, query):
        """Ищет позиции по текстовому запросу."""
        results = [entry for entry in self.data if
                   query.lower() in entry[0].lower()]
        return sorted(results, key=lambda x: x[-1])

    def export_to_html(self, fname='output.html'):
        """Выгружает данные в HTML файл."""
        with open(fname, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Позиции продуктов</title>
            </head>
            
            <body>
                <table border=1>
                    <tr>
                        <th>№</th>
                        <th>Наименование</th>
                        <th>Цена</th>
                        <th>Вес</th>
                        <th>Файл</th>
                        <th>Цена за кг.</th>
                    </tr>
            """)
            for number, (name, price, weight, file, price_per_kg) in enumerate(
                    self.data, 1):
                htmlfile.write(f"""
                    <tr>
                        <td>{number}</td>
                        <td>{name}</td>
                        <td>{price}</td>
                        <td>{weight}</td>
                        <td>{file}</td>
                        <td>{price_per_kg:.2f}</td>
                    </tr>
                """)
            htmlfile.write("""
                </table>
            <footer>
                <hr>
                Табличка с рамочками
            </footer>
            </body>
            </html>
            """)

    def interactive_search(self):
        """Запускает интерактивный поиск по запросам из консоли."""
        print("Введите текст для поиска. Для выхода введите 'exit'.")
        while True:
            query = input("Поиск: ").strip()
            if query.lower() == 'exit':
                print("Работа завершена.")
                break
            results = self.find_text(query)
            if not results:
                print("Ничего не найдено.")
            else:
                headers = ["№", "Наименование", "Цена", "Вес", "Файл",
                           "Цена за кг."]
                rows = [[i + 1, *result] for i, result in enumerate(results)]
                print(tabulate(rows, headers=headers, tablefmt="grid"))


# Основная программа
if __name__ == "__main__":
    folder = "./price_lists"  # Путь к папке с файлами
    analyzer = PriceAnalyzer(folder)
    analyzer.load_prices()
    analyzer.export_to_html()
    analyzer.interactive_search()

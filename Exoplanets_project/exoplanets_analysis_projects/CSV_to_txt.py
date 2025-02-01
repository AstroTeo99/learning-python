import csv
import re

csv_path = "./NAME_FILE_TO_CONVERT.csv"
txt_output = "./NAME_CONVERTED_FILE.txt"

data = []

unit_pattern = re.compile(r"\[(.*?)\]")

with open(csv_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    
    for row in reader:
        if len(row) >= 2:
            col_name = row[0].strip()
            description = row[1].strip()
            unit_match = unit_pattern.search(description)
            unit = unit_match.group(1) if unit_match else ""
            description = unit_pattern.sub("", description).strip()
            data.append(f"{col_name:<30} {unit:<20} {description}")

with open(txt_output, "w", encoding="utf-8") as txtfile:
    txtfile.write(f"{'Column Name':<30} {'Unit':<20} {'Description'}\n")
    txtfile.write("-" * 80 + "\n")
    txtfile.write("\n".join(data))

print(f"File TXT creato: {txt_output}")

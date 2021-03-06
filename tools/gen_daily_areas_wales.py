#!/usr/bin/env python

# Extract local authority case data (Wales) from an HTML page and save in CSV format.

from bs4 import BeautifulSoup
import csv
import dateparser
import pandas as pd
import re
import sys

html_file = sys.argv[1]
csv_file = sys.argv[2]


def normalize_whitespace(text):
    return text.replace(
        u"\xa0", u" "
    ).strip()  # replace non-breaking spaces with regular spaces


# Get upper tier local authority name to code mapping.
la_mapping = pd.read_csv(
    "data/raw/Lower_Tier_Local_Authority_to_Upper_Tier_Local_Authority_April_2019_Lookup_in_England_and_Wales.csv"
)
la_name_to_code = dict(zip(la_mapping["UTLA19NM"], la_mapping["UTLA19CD"]))
la_name_to_code["Cornwall and Isles of Scilly"] = la_name_to_code["Cornwall"]
la_name_to_code["Hackney and City of London"] = la_name_to_code["Hackney"]

country = "Wales"

html = open(html_file).read()
soup = BeautifulSoup(html, features="html.parser")
table = soup.find_all("table")[-1]

text = soup.get_text()
text = text.replace(u"\xa0", u" ")  # replace non-breaking spaces with regular spaces

pattern = re.compile(r"(?s)Updated: (?P<time>.+?),? \S+ (?P<date>\d+\s\w+\s\d{4})")
m = re.search(pattern, text)
groups = m.groupdict()
date = dateparser.parse(groups["date"]).strftime("%Y-%m-%d")

output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
for table_row in table.findAll("tr"):
    columns = [normalize_whitespace(col.text) for col in table_row.findAll("td")]
    if len(columns) == 0:
        continue
    if columns[0] == "Local Authority" or columns[0] == "Total:":
        continue
    la = (
        columns[0]
        .replace("City and County of Swansea", "Swansea")
        .replace("City of Cardiff", "Cardiff")
        .replace("Newport City", "Newport")
        .replace("County Borough Council", "")
        .replace("County Council", "")
        .replace("Council", "")
        .strip()
    )
    cases = columns[3]
    output_row = [date, country, la_name_to_code.get(la, ""), la, cases]
    output_rows.append(output_row)

with open(csv_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(output_rows)

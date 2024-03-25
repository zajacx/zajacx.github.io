import requests  # do pobrania całego html
from bs4 import BeautifulSoup  # do wyciągania danych z html
import re
import os
from googlesearch import search

# Ponieważ googlesearch nie działa...
wiki_list = [
         ("Python", "https://en.wikipedia.org/wiki/Python_(programming_language)"),
         ("C", "https://en.wikipedia.org/wiki/C_(programming_language)"),
         ("C++", "https://en.wikipedia.org/wiki/C%2B%2B"),
         ("Java", "https://en.wikipedia.org/wiki/Java_(programming_language)"),
         ("C#", "https://en.wikipedia.org/wiki/C_Sharp_(programming_language)"),
         ("JavaScript", "https://en.wikipedia.org/wiki/JavaScript"),
         ("SQL", "https://en.wikipedia.org/wiki/SQL"),
         ("Go", "https://en.wikipedia.org/wiki/Go_(programming_language)"),
         ("Visual Basic", "https://en.wikipedia.org/wiki/Visual_Basic_(.NET)"),
         ("PHP", "https://en.wikipedia.org/wiki/PHP"),
         ("Fortran", "https://en.wikipedia.org/wiki/Fortran"),
         (
             "Delphi/Object Pascal",
             "https://en.wikipedia.org/wiki/Pascal_(programming_language)",
         ),
         ("MATLAB", "https://en.wikipedia.org/wiki/MATLAB"),
         ("Assembly language", "https://en.wikipedia.org/wiki/Assembly_language"),
         ("Scratch", "https://en.wikipedia.org/wiki/Scratch_(programming_language)"),
         ("Swift", "https://en.wikipedia.org/wiki/Swift_(programming_language)"),
         ("Kotlin", "https://en.wikipedia.org/wiki/Kotlin_(programming_language)"),
         ("Rust", "https://en.wikipedia.org/wiki/Rust_(programming_language)"),
         ("COBOL", "https://en.wikipedia.org/wiki/COBOL"),
         ("Ruby", "https://en.wikipedia.org/wiki/Ruby_(programming_language)"),
     ]


''' Webscraping '''


def scrape_page(url):
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')
    return soup


''' Przygotowanie strony głównej '''


def get_header(soup):
    header = soup.find('h1').find('b').text.strip()
    return "## " + header


def get_welcome_text(soup):
    # Find welcome text:
    text = soup.find_all('p')[2].get_text()[0:2019]
    text = ''.join(text.splitlines())
    pattern = re.compile(r'CEO TIOBE Software')

    # Find the pattern in a text to separate paragraphs:
    match = pattern.search(text)
    text1 = text[:match.end()]
    text2 = text[match.end():]
    text = text1 + "\n\n" + text2
    return text


def create_welcome_page(header, text):
    list_page_link = f"[TIOBE Index Top 20](list_page.md)"
    with open("index.md", "w") as w_page:
        w_page.write(header)
        w_page.write("\n\n")
        w_page.write(text)
        w_page.write("\n\n")
        w_page.write(list_page_link)


''' Przygotowanie strony z listą '''


def get_table_rows(table):
    rows = []
    tr_blocks = table.find_all('tr')
    for tr in tr_blocks:
        td_blocks = tr.find_all('td')
        row = []
        for td in td_blocks:
            text = td.text.strip()
            # Poprawki:
            if text != '':
                row.append(text)
        if row:
            rows.append(row)
    return rows


def get_table(soup):
    table = soup.find('table')
    if not table:
        print("Nie znaleziono tabeli")
        return

    rows = get_table_rows(table)
    return rows


def better_name_creator(lang_name):
    better_name = lang_name.lower()
    better_name = better_name.replace('/', '-')
    better_name = better_name.replace(' ', '_')
    return better_name


def create_lang_info(row):
    curr_pos = row[0]
    prev_pos = row[1]
    lang_name = row[2]
    ratings = row[3]
    change = row[4]

    better_name = better_name_creator(lang_name)
    lang_page_dir = f"{better_name}.md"
    lang_page_link = f"[{lang_name}]({lang_page_dir})"
    create_lang_page(lang_name, lang_page_dir)

    return f"### {lang_page_link}\n\n" \
           f"**Current position (Feb 2024):** {curr_pos}\n\n" \
           f"**Previous position (Feb 2023):** {prev_pos}\n\n" \
           f"**Ratings:** {ratings}\n\n**Change:** {change}\n\n"


def create_list_page(table):
    header = "## List of languages with highest TIOBE Index:"
    content = ""

    for row in table:
        content += create_lang_info(row)

    welcome_page_link = f"[Back to TIOBE description](index.md)"

    with open("list_page.md", "w") as l_page:
        l_page.write(header)
        l_page.write("\n\n")
        l_page.write(content)
        l_page.write("\n\n\n")
        l_page.write(welcome_page_link)


''' Przygotowanie stron z opisami języków '''


def remove_square_brackets(text):
    pattern = re.compile(r'\[.*?\]')
    result = re.sub(pattern, '', text)
    return result


def create_lang_page(name, page_dir):
    # Oryginalny kod:
    # url = list(search(f"{name} Wikipedia", stop=1))
    # url = url[0]

    # Zaślepka na linki do stron:
    url = ""
    for pair in wiki_list:
        if pair[0] == name:
            url = pair[1]
            break

    page = scrape_page(url)

    info = page.find_all('p')
    description = f"{info[0].text}\n\n{info[1].text}"
    description = remove_square_brackets(description)
    images = page.find_all('img')

    logo_link = ""
    for image in images:
        source = image.get('src')
        if "logo" in source or "Logo" in source:
            logo_link = "https:" + source
            break

    list_page_link = f"[Back to the list](list_page.md)"
    logo_alias = f'![logo is gone :(]({logo_link} "Logo {name}")'
    url_alias = f"[{name} Wikipedia page]({url})"

    with open(page_dir, "w") as file:
        print(f"Created {name} page!")
        file.write("## " + name)
        file.write("\n\n")
        file.write(logo_alias)
        file.write("\n\n")
        file.write(description)
        file.write("\n\n")
        file.write(url_alias)
        file.write("\n\n")
        file.write(list_page_link)


def main():
    url = 'https://www.tiobe.com/tiobe-index/'
    soup = scrape_page(url)
    header = get_header(soup)
    welcome_text = get_welcome_text(soup)
    create_welcome_page(header, welcome_text)
    table = get_table(soup)
    create_list_page(table)


if __name__ == '__main__' :
    main()

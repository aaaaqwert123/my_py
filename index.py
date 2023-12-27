import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import openpyxl 

def crawl_news(keywords, start_date, end_date, number):
    search_results = []

    for key in keywords:
        count = 0
        page = 1
        while count < number:
            response = requests.get(f"https://search.naver.com/search.naver?where=news&query={key}&sort=0&photo=0&page={page}&field=0&pd=3&ds={start_date}&de={end_date}&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:from{start_date}to{end_date},a:all&start={(page - 1) * 10 + 1}")
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            news_items = soup.find_all("div", class_="news_area")

            if not news_items:
                break

            for item in news_items:
                if count >= number:
                    break

                title_element = item.find("a", class_="news_tit")
                if not title_element:
                    continue
                title = title_element.get_text(strip=True)
                url = title_element["href"]

                date_element = item.find("span", class_="info")
                if date_element:
                    date = date_element.get_text(strip=True).split()[0]

                    search_results.append({"Keyword": key, "Title": title, "URL": url, "Date": date})
                    count += 1

            page += 1

    return search_results

def main():
    st.title("입력해주세요")

    keywords = st.text_input("키워드")
    start_date = st.date_input("시작날짜:")
    end_date = st.date_input("끝나는날짜:")
    number = st.number_input("검색 갯수:", min_value=1, step=1)

    if st.button("검색하기"):
        keywords_list = keywords.split(',')
        search_results = crawl_news(keywords_list, start_date, end_date, number)

        if not search_results:
            st.warning("No articles found for the given criteria.")
        else:
            st.success("News crawled successfully!")

            # Display search results
            st.table(pd.DataFrame(search_results))

            # Save results to Excel file
            file_name = '-'.join(keywords_list) + '_results.xlsx'
            df = pd.DataFrame(search_results)
            st.markdown(get_table_download_link(df, file_name), unsafe_allow_html=True)

import base64

def get_table_download_link(df, file_name):
    # Specify the file path for saving the Excel file
    excel_file_path = f"./{file_name}"
    df.to_excel(excel_file_path, index=False, header=True)

    # Read the content of the Excel file as bytes
    with open(excel_file_path, 'rb') as f:
        file_content = f.read()

    # Remove the temporary Excel file
    os.remove(excel_file_path)

    # Encode the bytes to base64
    file_content_base64 = base64.b64encode(file_content).decode("utf-8")

    # Generate download link
    return f'<a href="data:application/octet-stream;base64,{file_content_base64}" download="{file_name}">Download Excel File</a>'

if __name__ == '__main__':
    main()

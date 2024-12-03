from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials

arquivo_credenciais = "clipping-bot-418820-52ef5e8ed495.json"
conteudo_credenciais = os.environ["KEY_GOOGLE"]
with open(arquivo_credenciais, mode="w") as arquivo:
    arquivo.write(conteudo_credenciais)
conta = ServiceAccountCredentials.from_json_keyfile_name(arquivo_credenciais)
api = gspread.authorize(conta)
planilha = api.open_by_key(os.environ["SHEET_ID"])
sheet = planilha.worksheet("Página2")



chave_api = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=chave_api)

def get_epbr():
    #captura página "Ultimas Noticias EPBR"
    result = requests.get("https://eixos.com.br/ultimas-noticias/")

    #variável result vai receber o codigo da execução da página chamada pela request
    soup = BeautifulSoup(result.text)

    titles = soup.find_all("article", class_="feed feed-lg-v1 g-col-12")

    # Itera sobre as tags encontradas para extrair os títulos e os links
    for title in titles:
        # Extrai o texto do título
        title_text = title.a.text.strip()
        # Extrai o link
        link = title.a["href"]

        # Faz uma solicitação HTTP para obter o conteúdo da página do link
        link_response = requests.get(link)
        link_html = link_response.text

        # Cria um objeto BeautifulSoup para a página do link
        link_soup = BeautifulSoup(link_html, "html.parser")

        # Extrai o conteúdo dos parágrafos principais
        main_paragraphs = link_soup.find("div", class_="single-content").find_all("p")


        # Concatena o texto dos parágrafos principais
        main_text = "\n".join(paragraph.get_text().strip() for paragraph in main_paragraphs)


        coluna_links = sheet.col_values(2) #testa para ver se o link já está na coluna e já foi lido, para evitar repetições.

        if link in coluna_links:
            print("Link já raspado")

        else:
            if "Brava Energia" in main_text:
                prompt = "Resuma a matéria abaixo, referente a uma empresa de petróleo de capital aberto, em um texto de até 300 caracteres. Esse resumo será utilizado pela alta gerência para analisar rapidamente o conteúdo da matéria."

                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[{"role": "user", "content": f"{prompt}: {main_text}"}
                ])    

                resumo_text = response.choices[0].message.content

                linha_armazenar = [title_text, link,response.choices[0].message.content] #armazenar título, link e resumo na planilha
                sheet.insert_row(linha_armazenar, 2)
                token = os.environ.get("TOKEN_TELEGRAM")
                chat_id = "-1002260808675"

                url = f"https://api.telegram.org/bot{token}/sendMessage"
                params = {"chat_id": chat_id, "text": 'Título: '+ title_text + '\n\n' + 'Link: ' + link + '\n\n' + 'Resumo:' + resumo_text}
                response = requests.post(url, params=params)


def get_infomoney():
    #captura página "Ultimas Noticias Infomoney"
    result = requests.get("https://www.infomoney.com.br/ultimas-noticias/")

    #variável result vai receber o codigo da execução da página chamada pela request
    soup = BeautifulSoup(result.text)

    titles = soup.find_all("h2", class_="font-im-sans text-wl-neutral-950 text-base md:text-lg font-semibold tracking-wide md:tracking-normal")

    # Itera sobre as tags encontradas para extrair os títulos e os links
    for title in titles:
        # Extrai o texto do título
        title_text = title.a.text.strip()
        # Extrai o link
        link = title.a["href"]

        # Faz uma solicitação HTTP para obter o conteúdo da página do link
        link_response = requests.get(link)
        link_html = link_response.text

        # Cria um objeto BeautifulSoup para a página do link
        link_soup = BeautifulSoup(link_html, "html.parser")

        # Extrai o conteúdo dos parágrafos principais
        article = link_soup.find("article", class_= "im-article clear-fix")
        if article:
            main_paragraphs = article.find_all("p")
            main_text = "\n".join(paragraph.get_text().strip() for paragraph in main_paragraphs)

        coluna_links = sheet.col_values(2) #testa para ver se o link já está na coluna e já foi lido, para evitar repetições.
        if link in coluna_links:
            print("Link já raspado")

        else:
            if "Brava Energia" in main_text:
                prompt = "Resuma a matéria abaixo, referente a uma empresa de petróleo de capital aberto, em um texto de até 300 caracteres. Esse resumo será utilizado pela alta gerência para analisar rapidamente o conteúdo da matéria."

                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[{"role": "user", "content": f"{prompt}: {main_text}"}
                ]) 
                
                resumo_text = response.choices[0].message.content

                token = os.environ.get("TOKEN_TELEGRAM")
                chat_id = "-1002260808675"

                url = f"https://api.telegram.org/bot{token}/sendMessage"
                params = {"chat_id": chat_id, "text": 'Título: '+ title_text + '\n\n' + 'Link: ' + link + '\n\n' + 'Resumo: '+ resumo_text}
                response = requests.post(url, params=params)
                
                
def get_investing():
    #captura página "Ultimas Noticias Infomoney"
    result = requests.get("https://br.investing.com/news/latest-news")

    #variável result vai receber o codigo da execução da página chamada pela request
    soup = BeautifulSoup(result.text)

    titles = soup.find_all("div", class_="news-analysis-v2_content__z0iLP w-full text-xs sm:flex-1")

    # Itera sobre as tags encontradas para extrair os títulos e os links
    for title in titles:
        # Extrai o texto do título
        title_text = title.a.text.strip()
        # Extrai o link
        link = title.a["href"]

        # Faz uma solicitação HTTP para obter o conteúdo da página do link
        link_response = requests.get(link)
        link_html = link_response.text

        # Cria um objeto BeautifulSoup para a página do link
        link_soup = BeautifulSoup(link_html, "html.parser")

        # Extrai o conteúdo dos parágrafos principais
        article = link_soup.find("div", class_= "article_WYSIWYG__O0uhw article_articlePage__UMz3q text-[18px] leading-8")
        if article:
            main_paragraphs = article.find_all("p")
            main_text = "\n".join(paragraph.get_text().strip() for paragraph in main_paragraphs)

        coluna_links = sheet.col_values(2) #testa para ver se o link já está na coluna e já foi lido, para evitar repetições.
        if link in coluna_links:
            print("Link já raspado")

        else:
            if "Brava Energia" in main_text:
                prompt = "Resuma a matéria abaixo, referente a uma empresa de petróleo de capital aberto, em um texto de até 300 caracteres. Esse resumo será utilizado pela alta gerência para analisar rapidamente o conteúdo da matéria."

                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[{"role": "user", "content": f"{prompt}: {main_text}"}
                ]) 
                
                resumo_text = response.choices[0].message.content

                token = os.environ.get("TOKEN_TELEGRAM")
                chat_id = "-1002260808675"

                url = f"https://api.telegram.org/bot{token}/sendMessage"
                params = {"chat_id": chat_id, "text": 'Título: '+ title_text + '\n\n' + 'Link: ' + link + '\n\n' + 'Resumo: '+ resumo_text}
                response = requests.post(url, params=params)

                linha_armazenar = [title_text, link, resumo_text] #armazenar título, link e resumo na planilha
                sheet.insert_row(linha_armazenar, 2)
                
def get_petronoticias():
    #captura página "Ultimas Noticias Infomoney"
    result = requests.get("https://petronoticias.com.br/category/og/")

    #variável result vai receber o codigo da execução da página chamada pela request
    soup = BeautifulSoup(result.text)

    titles = soup.find_all("h2", class_="title")

    # Itera sobre as tags encontradas para extrair os títulos e os links
    for title in titles:
        # Extrai o texto do título
        title_text = title.a.text.strip()
        # Extrai o link
        link = title.a["href"]

        # Faz uma solicitação HTTP para obter o conteúdo da página do link
        link_response = requests.get(link)
        link_html = link_response.text

        # Cria um objeto BeautifulSoup para a página do link
        link_soup = BeautifulSoup(link_html, "html.parser")

        # Extrai o conteúdo dos parágrafos principais
        article = link_soup.find("div", class_= "entry")
        if article:
            main_paragraphs = article.find_all("p")
            main_text = "\n".join(paragraph.get_text().strip() for paragraph in main_paragraphs)

        coluna_links = sheet.col_values(2) #testa para ver se o link já está na coluna e já foi lido, para evitar repetições.
        if link in coluna_links:
            print("Link já raspado")

        else:
            if "Brava Energia" in main_text:
                prompt = "Resuma a matéria abaixo, referente a uma empresa de petróleo de capital aberto, em um texto de até 300 caracteres. Esse resumo será utilizado pela alta gerência para analisar rapidamente o conteúdo da matéria."

                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[{"role": "user", "content": f"{prompt}: {main_text}"}
                ]) 
                
                resumo_text = response.choices[0].message.content

                token = os.environ.get("TOKEN_TELEGRAM")
                chat_id = "-1002260808675"

                url = f"https://api.telegram.org/bot{token}/sendMessage"
                params = {"chat_id": chat_id, "text": 'Título: '+ title_text + '\n\n' + 'Link: ' + link + '\n\n' + 'Resumo: '+ resumo_text}
                response = requests.post(url, params=params)

                linha_armazenar = [title_text, link, resumo_text] #armazenar título, link e resumo na planilha
                sheet.insert_row(linha_armazenar, 2)
                
get_infomoney()
get_epbr()
get_investing()
get_petronoticias()
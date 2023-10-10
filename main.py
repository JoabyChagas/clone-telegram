from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pytesseract
import requests
import telebot
import time

TOKEN = ''
CHAT_ID_ENV = ''
CHAT_ID_REC = ''

chrome_options = Options()
chrome_options.add_argument("user-data-dir=selenium")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
driver.get(f"https://web.telegram.org/a/#{CHAT_ID_ENV}")

tbot = telebot.TeleBot(token=TOKEN, parse_mode='MARKDOWN')
mensagens_enviadas = set()

def format_text(texto):
    # Divida o texto em linhas
    linhas = texto.split('\n')
    linha_01 = linhas[0].split()[0].capitalize()
    linha_03 = linhas[2] if len(linhas) > 2 else ''
    linha_04 = linhas[3].split()[0]
    linha_05 = linhas[4].split()[0]
    linha_06 = linhas[5].split()[0]
    linha_07 = linhas[6].split()[0]

    return f"{linha_01} {linha_03}\nTp {linha_04}\nTp {linha_05}\nTp {linha_06}\nSL {linha_07}\n"

def capturar(img_url):
    script = f'window.open("{img_url}", "_blank");'
    driver.execute_script(script)
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    screenshot_filename = f'screenshot.png'
    driver.save_screenshot(screenshot_filename)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return screenshot_filename

def transcrever(screenshot_filename):
    imagem = screenshot_filename 
    texto = pytesseract.image_to_string(imagem, config='--psm 6')
    linhas = texto.split('\n')
    for linha in linhas:
        if '/' in linha:
            partes = linha.split('/')
            if len(partes) == 2 and len(partes[0].strip()) == 3 and len(partes[1].strip()) == 3:
                resultado = str(partes[0].strip() + partes[1].strip())
    return resultado



time.sleep(3)
try:
    while True:
        conteudo_da_pagina = driver.page_source
        soup = BeautifulSoup(conteudo_da_pagina, 'html.parser')
        mensagens_do_grupo = soup.find_all('div', class_='content-inner')


        for mensagem in mensagens_do_grupo:
            try:
                img_element = mensagem.find('img', class_='full-media')
                mensagem_html = str(mensagem)
                soup = BeautifulSoup(mensagem_html, 'html.parser')
                conversa = soup.find('div', class_='text-content clearfix with-meta')

                if conversa and img_element and 'src' in img_element.attrs:
                    try:
                        if img_element:
                            img_url = img_element['src']
                            partes_url = img_url.split('-')
                            if partes_url:
                                id_img = partes_url[4]
                                if id_img not in mensagens_enviadas:
                                    mensagens_enviadas.add(id_img)
                                    screenshot_filename = capturar(img_url)
                                    texto_da_imagem = transcrever(screenshot_filename)


                                    # Parte da imagem
                                    try:
                                        if conversa:
                                            texto = conversa.get_text('\n')
                                            if texto.startswith("BUY") or texto.startswith("SELL"):
                                                if texto not in mensagens_enviadas:
                                                    mensagens_enviadas.add(texto)
                                                    texto_formatado = format_text(texto)

                                            print(f'{texto_da_imagem}\n{texto_formatado}')
                                            tbot.send_message(CHAT_ID_REC, f'{texto_da_imagem}\n{texto_formatado}')
                                            time.sleep(1)

                                    except Exception as e_img:
                                        print(f"Erro ao processar imagem: {e_img}")

                    except Exception as e_img:
                        print(f"Erro ao processar a ulr: {e_img}")

            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")

except KeyboardInterrupt:
    driver.quit()
finally:
    driver.quit()


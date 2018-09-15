"""Download from mds-fm.ru"""

import mechanicalsoup
import re

def mds_fm(s):
    # Функция поиска ссылок на странице
    table = []
    def links_download():
        for link in browser.get_current_page().select('li h3 a'):
            if re.search('node', link.attrs['href']) == None and re.search('Все авторы', link.text) == None and re.search('Приложение для Android', link.text) == None:
                table.append([link.text, link.attrs['href']])
    
    # Подключаемся к mds-fm.ru
    browser = mechanicalsoup.StatefulBrowser()
    browser.open("http://mds-fm.ru/")

    # Заполняем форму поиска
    browser.select_form('#search-block-form')
    browser["search_block_form"] = s
    browser.submit_selected()

    # Качаем ссылки из результата с 1 страницы
    links_download()
    for page in browser.get_current_page().select("a[title^='На страницу номер']"):
        browser.open("http://mds-fm.ru" + page.attrs['href'])
        links_download()
    return table

def mds_fm_dwn(src):
    table_dwn = []
    
    # Ищем ссылки на аудиокниги на странице
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(src)
    for link in browser.get_current_page().select("a[title^='загрузить']"):
        table_dwn.append(link.attrs['href'])
        
    return table_dwn

def mds_club(s):
    table = []
    def links_download():
        pass
    
    browser = mechanicalsoup.StatefulBrowser()
    browser.open("http://mds-club.ru/cgi-bin/index.cgi?r=84&lang=rus")
    
    
    browser.select_form('form[action="http://mds-club.ru/cgi-bin/index.cgi"]')
    browser["search"] = s
    browser.submit_selected(btnName='searchbutton')
    
    counter = 0
    for link in browser.get_current_page().select("a[title='Автор рассказа']"):
        table.append([link.text, link.attrs['href']])
    #for link in browser.get_current_page().select("a[title^='Название рассказа']"):
        #table[counter].append(link.text)
        #counter += 1

    return browser.get_current_page().find("div", id="ligthline")

#print(mds_club('планета'))
#print(mds_dwn('http://mds-fm.ru/random_story'))
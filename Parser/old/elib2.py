import requests, urllib.parse, xlwt, re
from bs4 import BeautifulSoup
from datetime import date
session = requests.Session()
print("Настраиваю cookie...")
r = session.post('http://elibrary.ru/')
cookie = session.cookies.get_dict()

#Шоб время знать
current_year = date.today().year
prev_year = current_year - 1
#Функция получает количество статей автора по критериям
def itemsNum(id, curr=0, prev=0, VAK=0):
    idata = {'authorid':id}
    if curr == 1: idata['years_' + str(current_year)] = 'on'
    if prev == 1: idata['years_' + str(prev_year)] = 'on'
    if VAK == 1: idata['show_option'] = '5'
    itemsr = session.post('https://elibrary.ru/author_items.asp', data=idata, cookies=cookie)
    items_rr = BeautifulSoup(itemsr.text, 'html.parser').find("td", {"class": "redref"})
    if items_rr is not None:
        return int(items_rr.find("b").get_text())
    else:
        return 0
#Функция получает число из строки статистики автора
def writeStat(stat_ind, cell_x):
    ctr = stattable.findAll("tr")[stat_ind]
    ctd = ctr.find("td", {"align": "center", "class": "midtext"})
    ca = ctd.find("a")
    if ca is not None:
        ws.write(aline, cell_x, int(ca.get_text()))
    else:
        ws.write(aline, cell_x, int(ctd.get_text().split()[0]))
#Функция возвращает 1, если строка на английском и 0, если на других
def isEn(tmpstr):
    tmpstr = tmpstr.lstrip()
    tmpc = tmpstr[0]
    if (tmpc >= 'a' and tmpc <= 'z') or (tmpc >= 'A' and tmpc <= 'Z'):
        return 1
    else:
        return 0
#Получить количество авторов из строки с авторами
def authorsNum(tmpstr):
    return len(tmpstr.split()) / 2
#Функция расчета оценки публикации
def pubRate(monoraph=0, sut=0, rus=0,
                 not_rus=0, spravochnik=0,
                 statiya=0, VAK=0, RINC=0,
                 scopus=0, number_of_scientists=0):
    """имеет смысл передавать только ненулевые значения
Пример: Metod_ocenki(number_of_scientists=3, statiya=1, RINC=1)"""
    if monoraph != 0:
        if not_rus != 0:
            if 0 < number_of_scientists < 4: return 12
            elif number_of_scientists == 4: return 8
            elif number_of_scientists == 5: return 5.5
            elif number_of_scientists == 6: return 3.5
            elif number_of_scientists == 7: return 2
            elif number_of_scientists > 8: return 0
        elif rus != 0:
            if 0 < number_of_scientists < 4: return 10
            elif number_of_scientists == 4: return 6.5
            elif number_of_scientists == 5: return 4
            elif number_of_scientists == 6: return 2.5
            elif number_of_scientists == 7: return 1
            elif number_of_scientists > 8: return 0
        elif sut != 0:
            if 0 < number_of_scientists < 4: return 8
            elif number_of_scientists == 4: return 5
            elif number_of_scientists == 5: return 3
            elif number_of_scientists == 6: return 1.5
            elif number_of_scientists > 7: return 0
        elif spravochnik != 0:
            if 0 < number_of_scientists < 4: return 8
            elif number_of_scientists == 4: return 5
            elif number_of_scientists == 5: return 3
            elif number_of_scientists == 6: return 1.5
            elif number_of_scientists > 7: return 0
    elif statiya != 0:
        if scopus != 0:
            if 0 < number_of_scientists < 4: return 6
            elif number_of_scientists == 4: return 4
            elif number_of_scientists == 5: return 2.5
            elif number_of_scientists == 6: return 0.5
            elif number_of_scientists > 7: return 0
        elif VAK != 0:
            if 0 < number_of_scientists < 4: return 4
            elif number_of_scientists == 4: return 2
            elif number_of_scientists == 5: return 1
            elif number_of_scientists == 6: return 0.5
            elif number_of_scientists > 6: return 0
        elif RINC != 0:
            if 0 < number_of_scientists < 4: return 2
            elif number_of_scientists == 4: return 1
            elif number_of_scientists == 5: return 0.5
            elif number_of_scientists > 5: return 0
    return 0
def authorRate(id, year):
    pdata = {'authorid': str(id), 'sortorder': '3', 'order': '1', 'years_' + str(year): 'on'}
    r = session.post('https://elibrary.ru/author_items.asp', data=pdata, cookies=cookie)
    soup = BeautifulSoup(r.text, 'html.parser')
    aurate_rr = soup.find("td", {"class": "redref"})
    if aurate_rr is not None:
        pubnum = int(aurate_rr.find("b").get_text())
    else:
        return 0
    line = 1
    rate = 0
    pagenum = 1
    while pubnum > 0:
        pdata = {'authorid': str(id), 'sortorder': '3', 'order': '1', 'pagenum': str(pagenum), 'years_'+str(year): 'on'}
        r = session.post('https://elibrary.ru/author_items.asp', data=pdata, cookies=cookie)
        pubnum -= 20
        pagenum += 1
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find("table", {"id": "restab"})
        ptrs = table.findAll("tr", {"valign": "middle"})
        for ptr in ptrs:
            otd = ptr.find("td", {"align": "left", "valign": "top"})
            if otd is not None:
                anum = authorsNum(otd.findAll("font")[0].get_text())
                publink = otd.find("a")["href"]
                pubr = session.post('https://elibrary.ru' + publink, cookies=cookie)
                soup = BeautifulSoup(pubr.text, 'html.parser')
                typetable = soup.find("table", {"width": "580", "border": "0", "cellspacing": "0", "cellpadding": "2"})
                pubtype = typetable.find("tr").find("td").find("font").get_text()
                if 'статья' in pubtype:
                    #print(pubtype + ' = статья')
                    bstats = soup(text='БИБЛИОМЕТРИЧЕСКИЕ ПОКАЗАТЕЛИ:')[0].parent.parent.parent.parent.findAll("tr")[1]
                    bs_rinc = 0
                    bs_scop = 0
                    if bstats.findAll("tr")[0].find("td").find("font").get_text() == 'да': bs_rinc = 1
                    if bstats.findAll("tr")[2].find("td").find("font").get_text() == 'да': bs_scop = 1
                    rate += pubRate(number_of_scientists=anum, statiya=1, RINC=bs_rinc, scopus=bs_scop)
                elif 'монография' in pubtype:
                    izdat = typetable.find(text=re.compile('Издательство')).parent
                    if izdat.find("a") is not None:
                        izdat = izdat.find("a")["title"]
                    else:
                        izdat = izdat.find("font").get_text()

                    if isEn(izdat):
                        rate += pubRate(number_of_scientists=anum, monoraph=1, not_rus=1)
                    elif 'Санкт-Петербургский государственный университет телекоммуникаций им. проф. М.А. Бонч-Бруевича' in izdat:
                        rate += pubRate(number_of_scientists=anum, monograph=1, sut=1)
                    else:
                        rate += pubRate(number_of_scientists=anum, monoraph=1, rus=1)
    return rate

#Подготовка EXCEL
wb = xlwt.Workbook()
ws = wb.add_sheet('Авторы')
ws.write(1, 0, '№')
ws.write(1, 1, 'Должность')
ws.write(1, 2, 'Уч. степ.')
ws.write(1, 3, 'Фамилия И.О.')
ws.write_merge(0, 0, 4, 8, 'Всего публикаций')
ws.write(1, 4, "Всего")
ws.write(1, 5, "ВАК")
ws.write(1, 6, "Заруб")
ws.write(1, 7, "Ссылок")
ws.write(1, 8, "h")
ws.write_merge(0, 0, 9, 11, 'В прошлом году')
ws.write(1, 9, "Всего")
ws.write(1, 10, "ВАК")
ws.write(1, 11, "Заруб")
ws.write_merge(0, 0, 13, 15, 'В текущем году')
ws.write(1, 13, "Всего")
ws.write(1, 14, "ВАК")
ws.write(1, 15, "Заруб")
ws.write_merge(0, 1, 12, 12, 'Оценка')
ws.write_merge(0, 1, 16, 16, 'Оценка')

#Необходимые переменные
#Читаем список авторов
with open("input.txt") as f: authors = f.readlines()
authors = [x.strip() for x in authors]
orgid = open("org.txt").readline() #orgid = int(input("Введите номер организации (спбгут = 1193): ")) #'1193'
hirsch = int(open("hirsch.txt").readline()) #int(input("Введите желаемый хирш: "))
aline = 2

for author in authors:
    surname = urllib.parse.quote_plus(author) #input("Введите ФИО: ")) #Красов А В

    #Поиск автора
    print("----------------------------------")
    print("Посылаю запрос на поиск авторов...")
    r = session.post('https://elibrary.ru/authors.asp?surname='+surname+'&sortorder=0&order=0&orgid='+orgid, cookies=cookie)

    #Разбор авторов
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find("table", {"id": "restab"})
    if table is None:
        print("Автор не найден (" + author + ")")
        continue
    trs = table.findAll("tr", {"valign": "top"})

    for tr in trs:
        td = tr.find("td", {"align": "right", "class": "midtext"})
        if len(td.findAll("a")) < 2:
			print("У автора нет публикаций (" + author + ")")
			continue
        analink = "https://elibrary.ru/" + td.findAll("a")[1]["href"]
        id = int(analink[42:])
        ws.write(aline, 0, aline - 1)
        #очередной автор найден, парсим его полностью

        #Разбираем ФИО автора
        td = tr.find("td", {"align": "left", "class": "midtext"})
        fio = td.find("font").get_text().replace('\xa0', '')
        ws.write(aline, 3, fio)

        print("Разбираем автора с id = " + str(id) + " (" + fio + ")")

        #Парсинг статистики
        r = session.post(analink, cookies=cookie)
        soup = BeautifulSoup(r.text, 'html.parser')
        form = soup.find("form", {"name": "results"})
        maintable = form.find("table")
        stattable = maintable.findAll("table")[3]

        #=====================ВСЕГО========================
        #Номер "число публикаций на elibrary.ru" в массиве равен 3
        #ctr = stattable.findAll("tr")[3]
        #ctd = ctr.find("td", {"align": "center", "class": "midtext"})
        #ws.write(aline, 4, int(ctd.get_text()) + 1)
		ws.write(aline, 4, itemsNum(str(id)))

        #ВАК = 30
        writeStat(30, 5)
        #Заруб = 28
        writeStat(28, 6)
        #Зарубежные ссылки = 34
        writeStat(34, 7)

        #Хирш = 11
        ctr = stattable.findAll("tr")[11]
        ctd = ctr.find("td", {"align": "center", "class": "midtext"})
        ca = ctd.find("a")
        ws.write(aline, 8, int(ctd.get_text()))

        # ================В ПРОШЛОМ ГОДУ=================
        #всего
        ws.write(aline, 9, itemsNum(str(id), prev=1))
        #вак
        ws.write(aline, 10, itemsNum(str(id), prev=1, VAK=1))
        #ws.write(aline,12,year*4) #оценка, но надо дописать чтоб было так - вак*4 + заруб*6

        # ================В ТЕКУЩЕМ ГОДУ=================
        #всего
        ws.write(aline, 13, itemsNum(str(id), curr=1))
        #вак
        ws.write(aline, 14, itemsNum(str(id), curr=1, VAK=1))
        #ws.write(aline, 16, year * 4)  # оценка, но надо дописать чтоб было так - вак*4 + заруб*6

        #=============СЧИТАЕМ ЗАРУБЕЖНЫЕ СТАТЬИ==========
        r = session.post('https://elibrary.ru/author_items_titles.asp?id='+str(id)+'&order=0&show_hash=0', cookies=cookie)
        soup = BeautifulSoup(r.text, 'html.parser')
        ptrs = soup.findAll("tr")
        pdata = {'authorid':str(id)}
        for ptr in ptrs:
            if isEn(ptr.get_text()) == 1:
                pdata['titles_' + ptr['id'][6:]] = 'on'
        #===считаем для текущего года===
        pdata['years_' + str(current_year)] = 'on'
        itemsr = session.post('https://elibrary.ru/author_items.asp', data=pdata, cookies=cookie)
        redref = BeautifulSoup(itemsr.text, 'html.parser').find("td", {"class": "redref"})
        if redref is not None:
            ws.write(aline, 15, int(redref.find("b").get_text()))
        else:
            ws.write(aline, 15, 0)
        # ===считаем для прошлого года===
        del pdata['years_' + str(current_year)]
        pdata['years_' + str(prev_year)] = 'on'
        itemsr = session.post('https://elibrary.ru/author_items.asp', data=pdata, cookies=cookie)
        redref = BeautifulSoup(itemsr.text, 'html.parser').find("td", {"class": "redref"})
        if redref is not None:
            ws.write(aline, 11, int(redref.find("b").get_text()))
        else:
            ws.write(aline, 11, 0)

        #=================СТАТЬИ======================
        aws = wb.add_sheet((str(aline - 1) + ") " + fio)[:30])
        aws.write(0, 0, "№")
        aws.write(0, 1, "Название")
        aws.write(0, 2, "Авторы")
        aws.write(0, 3, "Издание")
        aws.write(0, 4, "Цит.")
        aws.write(0, 5, "Не хватает")
        aws.write(0, 6, "Количество авторов")
        print("Посылаю запрос на чтение публикаций автора...")
        r = session.post('https://elibrary.ru/author_items.asp?authorid='+str(id)+'&pubrole=100&show_refs=1&show_option=0&sortorder=3&order=1', cookies=cookie)
        soup = BeautifulSoup(r.text, 'html.parser')
        pubnum = int(soup.find("td", {"class":"redref"}).find("b").get_text())
        line = 1
        rate = 0
        pagenum = 1
        while pubnum > 0:
            r = session.post('https://elibrary.ru/author_items.asp?authorid=' + str(id) + '&pubrole=100&show_refs=1&show_option=0&sortorder=3&order=1&pagenum='+str(pagenum), cookies=cookie)
            pubnum -= 20
            pagenum += 1
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find("table", {"id": "restab"})
            ptrs = table.findAll("tr", {"valign": "middle"})
            for ptr in ptrs:
                ptd = ptr.find("td", {"valign": "middle", "class": "select-tr-right"})
                if ptd is not None:
                    aws.write(line, 0, line)
                    ptd = ptr.find("td", {"align": "left", "valign": "top"})
                    aws.write(line, 1, ptd.find("a").get_text())
                    aws.write(line, 2, ptd.findAll("font")[0].get_text())
                    aws.write(line, 3, ptd.findAll("font")[1].get_text())
                    ind = int(ptr.find("td", {"align": "center", "valign": "middle"}).get_text())
                    aws.write(line, 4, ind)
                    aws.write(line, 6, authorsNum(ptd.findAll("font")[0].get_text()))
                    if line - 1 < hirsch:
                        if ind < hirsch:
                            aws.write(line, 5, hirsch - ind)
                    else:
                        if ind >= hirsch:
                            aws.write(line, 5, hirsch - ind - 1)
                    line += 1
        #===========ОЦЕНКИ=======================
        print("Считаю оценки автора...")
        ws.write(aline, 12, authorRate(id, prev_year))
        ws.write(aline, 16, authorRate(id, current_year))
        aline += 1

wb.save("out.xls")

print("Расчет успешно завершён!")
input("Нажмите <enter> для выхода...")























    #author_link = td.find("a")['href'] + "&sortorder=3&order=1"
    #print("Автор найден! Ссылка на него: " + author_link)

    # print("Посылаю запрос на чтений публикаций автора...")
    # r = session.post('https://elibrary.ru/' + author_link, cookies=cookie)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # table = soup.find("table", {"id": "restab"})
    # trs = table.findAll("tr", {"valign": "middle"})
    # print("Публикации автора:")
    # i = 1
    # min = 100
    # for tr in trs:
    #     td = tr.find("td", {"valign": "middle", "class": "select-tr-right"})
    #     if td is not None:
    #         print(str(i) + ") " + tr.find("a").getText())
    #         ind = int(td.getText())
    #         print("Индекс: " + str(ind))
    #         if ind < hirsch:
    #             print("Для хирша " + str(hirsch) + " необходимо ещё " + str(hirsch - ind))
    #         if ind < min:
    #             min = ind
    #         print("------------------------------------")
    #         i += 1
    # print("Текущий хирш равен: " + str(min))
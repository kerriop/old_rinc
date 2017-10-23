def Metod_ocenki(monoraph=0, sut=0, rus=0,
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



















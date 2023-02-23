import json


def lower(original_list):
    lower_list = []
    for random_word in original_list:
        try:
            lower_word = random_word.lower()
            lower_list.append(lower_word)
        except:
            lower_list.append(random_word)
    return lower_list

def check_disease_single(data):
    with open("../../../../../../../Downloads/main/Keyword_updated.json", "r", encoding='UTF-8-sig') as json_raw:
        json_word = json.load(json_raw)
    answer = []
    main_category = json_word['진단명']
    for i in data:
        dis = i[0]
        master = []
        temp = []
        for master_key, main_value in main_category.items():
            word_data = lower([dis])
            if any(word in str(word_data) for word in lower(main_value)):
                temp.append(master_key)
            else:
                pass
        filter_data = check(temp)
        master.append(filter_data)
        master.append(i[1])
        answer.append(master)
    
    return answer



def check(dataline):
    try:
        if '중성화' and '수컷중성화' in dataline:
            dataline.remove('중성화')
        elif '중성화' and '암컷중성화' in dataline:
            dataline.remove('중성화')
        elif '수컷중성화' and '암컷중성화' in dataline:
            dataline.remove('암컷중성화')
            dataline.remove('수컷중성화')
        elif '진료(일반)' and '진료(초진)' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '진료(야간)' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '진료(재진)' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '진료(입원)' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and 'PRP시술' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '귀처치' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '항암전처치' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '항암치료' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '침술' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '한방치료' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '주사마취' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '수액' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '산소치료' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '후처치' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '진통약' in dataline:
            dataline.remove('진료(일반)')
        elif '진료(일반)' and '구토처치' in dataline:
            dataline.remove('진료(일반)')
        elif 'DHPPi접종' and 'DHPPL접종' in dataline:
            dataline.remove('DHPPL접종')
        elif '혈액검사' and '혈액검사(CBC)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액(혈청)화학검사(Chemistry)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액검사(전해질)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈청검사(호르몬검사)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액검사(간검사)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액검사(젖산검사)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액검사(췌장염검사)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액검사(혈액형검사)' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액가스검사' in dataline:
            dataline.remove('혈액검사')
        elif '혈액검사' and '혈액검사(혈당검사)' in dataline:
            dataline.remove('혈액검사')
        elif '키트검사(CIV)' and '캐니플루접종' in dataline:
            dataline.remove('캐니플루접종')
        elif '키트검사(CPV)' and '키트검사(FPV)' in dataline:
            dataline.remove('키트검사(CPV)')
        elif '종합백신접종' and '종합백신5종접종' in dataline:
            dataline.remove('종합백신접종')
        elif '고양이종합백신접종' and '고양이3종백신접종' in dataline:
            dataline.remove('고양이종합백신접종')
        elif '고양이백혈병백신접종' and '키트검사(FeLV+FIV)' in dataline:
            dataline.remove('고양이백혈병백신접종')
        elif '코로나장염접종' and '키트검사(CCV)' in dataline:
            dataline.remove('키트검사(CCV)')
            dataline.remove('키트검사(FcoV/FIP)')
        elif '항암전처치' and '항암치료' in dataline:
            dataline.remove('항암치료')
        elif 'ANF' and '캐니플루접종' in dataline:
            dataline.remove('ANF')
        elif '오메프라졸' and '에스오메프라졸' in dataline:
            dataline.remove('오메프라졸')
        elif '프레드니솔론' and '메틸프레드니솔론' in dataline:
            dataline.remove('프레드니솔론')
        elif '엔로프락신' and '아시엔로정' in dataline:
            dataline.remove('아시엔로정')
        elif '오메가3' and '인터페론오메가' in dataline:
            dataline.remove('오메가3')
            dataline.remove('듀오메가(오메가3)영양제')
            dataline.remove('세라마이드&오메가3영양간식')
        elif '주사' and '항암치료' in dataline:
            dataline.remove('주사')
        elif '주사' and '주사마취' in dataline:
            dataline.remove('주사')
        elif '주사' and '심장사상충접종' in dataline:
            dataline.remove('주사')
        elif '주사' and '피하/근육주사' in dataline:
            dataline.remove('주사')
            dataline.remove('주사')
        elif '주사' and '비타민12주사' in dataline:
            dataline.remove('주사')
        elif '마취' and '마취모니터링' in dataline:
            dataline.remove('마취')
        elif '마취' and '점안마취' in dataline:
            dataline.remove('마취')
        elif '마취' and '호흡마취' in dataline:
            dataline.remove('마취')
        elif '마취' and '주사마취' in dataline:
            dataline.remove('마취')
        elif '마취' and '유도마취' in dataline:
            dataline.remove('마취')
        elif '마취' and '국소마취' in dataline:
            dataline.remove('마취')
        elif '소독' and '소독약' in dataline:
            dataline.remove('소독')
        elif '소독' and '표피소독' in dataline:
            dataline.remove('소독')
        elif '소독' and '피부소독' in dataline:
            dataline.remove('소독')
        elif '소독' and '안소독약' in dataline:
            dataline.remove('소독')
        elif '소독' and '구강소독제' in dataline:
            dataline.remove('소독')
        elif '결석제거수술' and '방광결석수술' in dataline:
            dataline.remove('결석제거수술')
        elif '결석제거수술' and '요도결석수술' in dataline:
            dataline.remove('결석제거수술')
        else:
            pass
    except:
        pass
    return dataline
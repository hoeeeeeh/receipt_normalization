import base64

import cv2
from io import BytesIO

import uuid
import time
import json
import re

import numpy as np
import pandas as pd
import requests
from PIL import Image

from fastapi import APIRouter, UploadFile

router = APIRouter(
    prefix="/ocr",
    tags=["ocr"],
)

image_filename = 'receipt.jpeg'


def image_to_np_array(data):
    return np.array(Image.open(BytesIO(data)).convert('RGB'))


@router.get("/")
async def main():
    return {"OCR": "success"}


@router.post("/upload")
async def upload_image(file: UploadFile):
    image_np = image_to_np_array(await file.read())
    cv2.imwrite('receipt.jpeg', image_np)
    return ocr_jpg()


def base64_to_jpg(base64img):
    # 웹 프론트에서 base64 이미지로 받음
    imgdata = base64.b64decode(base64img)
    filename = image_filename
    with open(filename, 'wb') as f:
        f.write(imgdata)


def ocr_jpg():

    secret_path = 'secret.json'
    with open(secret_path, 'r') as f:
        secret = json.load(f)

    api_url = secret['api_url']
    secret_key = secret['secret_key']

    print(api_url, secret_key)

    image = image_filename

    request_json = {
        'images': [
            {
                'format': 'jpeg',
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
        ('file', open(image, 'rb'))
    ]
    headers = {
        'X-OCR-SECRET': secret_key
    }

    response = requests.request("POST", api_url, headers=headers, data=payload, files=files).json()

    return parse_receipt_to_json(response)


###### 병원 정보 ######

# 정규식을 받아서 해당 내용을 지우는 함수 + 다중공백 제거
def Remover(regex, data_save):
    # 지워진거 따로 반환하기
    data_save = re.sub(regex, " ", data_save)
    data_save = Remove_Multiple_Space(data_save)
    return data_save

# 다중공백 제거 전용함수(2개 이상의 공백 제거)
def Remove_Multiple_Space(data_save):
    data_save = re.sub(" {2,}", " ", data_save)
    return data_save

# CSV file 을 DF으로 전환
def csv_to_data(csv_file):
    df = pd.read_csv(csv_file, header=0)
    dataset = df.values
    return dataset

# final_hosp_info.csv 의 동물병원 DB와 비교하여 DB의 정보로 치환
def check_hospital_info(sub_data):
    hospital_info = csv_to_data('./final_hosp_info.csv')
    regi_number = sub_data[0]
    number = re.sub("^0", "", str(sub_data[1]))
    address = sub_data[2]
    hospital_name = sub_data[3]

    if regi_number in hospital_info and regi_number != '':
        try:
            index = np.where(regi_number == hospital_info)
            address = hospital_info[int(index[0])][2]
            hospital_name = hospital_info[int(index[0])][0]
            if number != '':
                pass
            else:
                number = str(0) + str(hospital_info[int(index[0])][1])
            return regi_number, number, address, hospital_name
        except:
            return regi_number, number, address, hospital_name

    elif number in hospital_info and number != '':
        try:
            index = np.where(number == hospital_info)
            address = hospital_info[int(index[0])][2]
            hospital_name = hospital_info[int(index[0])][0]
            if regi_number != '':
                pass
            else:
                regi_number = hospital_info[int(index[0])][3]
            return regi_number, str(sub_data[1]), address, hospital_name
        except:
            return regi_number, number, address, hospital_name

    else:
        return regi_number, number, address, hospital_name


# 병원명
def Hospital_name(data_save):
    hospital_name = []
    regex_1 = " ?병 ?원 ?명 ?:? ?(2? ?4?시? ?[가-힣 24]{2,}병 ?원 ?2? ?4? ?시?) ?"
    regex_2 = " ?청 ?구 ? ?원 ?명 ?:? ?(2? ?4?시? ?[가-힣 24]{2,}병 ?원 ?2? ?4? ?시?) ?"
    regex_3 = " ?병 ?원 ?명 ?:? ?(2? ?4?시? ?[가-힣 24]{2,}센 ?터 ?2? ?4? ?시?) ?"
    regex_4 = " ?청 ?구 ? ?원 ?명 ?:? ?(2? ?4?시? ?[가-힣 24]{2,}센 ?터 ?2? ?4? ?시?) ?"
    regex_5 = " ?병 ?원 ?명 ?:? ?"
    regex_6 = " ?청 ?구 ?원 ?명 ?:? ?"
    regex_7 = "[가-힣]+ 동 ?물 ?병 ?원 ?"
    regex_8 = " ?(2?4? ?시? ?[가-힣]{0,} ?2?4?시? ?V?I?P?N? ?[가-힣]+센 ?터 ?)"

    hospital_name_1 = re.findall(regex_1, data_save)
    hospital_name.extend(hospital_name_1)
    data_save = Remover(regex_1, data_save)

    hospital_name_2 = re.findall(regex_2, data_save)
    hospital_name.extend(hospital_name_2)
    data_save = Remover(regex_2, data_save)

    hospital_name_3 = re.findall(regex_3, data_save)
    hospital_name.extend(hospital_name_3)
    data_save = Remover(regex_3, data_save)

    hospital_name_4 = re.findall(regex_4, data_save)
    hospital_name.extend(hospital_name_4)
    data_save = Remover(regex_4, data_save)

    data_save = Remover(regex_5, data_save)
    data_save = Remover(regex_6, data_save)
    data_save = Remover(regex_7, data_save)

    hospital_name_8 = re.findall(regex_8, data_save)
    hospital_name.extend(hospital_name_8)
    data_save = Remover(regex_8, data_save)

    if len(hospital_name) > 0:
        return hospital_name[0]
    else: 
        return ''

# 사업자 등록번호 관리
def Registration_Number(data_save):
    registration_number = []
    # 사업자 등록번호 : (숫자 10자리)
    regex_1 = " ?사 ?업 ?자? ?등? ?록? ?번? ?호? ?N?o? ?:? ?(\d\d\d)(\d\d)(\d\d\d\d\d) "
    # regex_2, 3 는 수정 진행
    regex_2 = " ?사 ?업 ?자? ?등? ?록? ?번? ?호? ?N?o? ?:? ?(\d{3}) ? ? ?(\d{2}) ?- ?(\d{5})\D"
    regex_3 = " ?사 ?업 ?자? ?등? ?록? ?번? ?호? ?N?o? ?:? ?(\d{3}) ?- ?(\d{2}) ? ?(\d{5})\D"
    # 사업자 등록번호 : (숫자3 - 숫자2 - 숫자5)
    regex_4 = " ?사 ?업 ?자? ?등? ?록? ?번? ?호? ?N?o? ?:? ?(\d{3} ?- ?\d{2} ?- ?\d{5})\D"
    # 사업자 등록번호 : (숫자3 - 숫자2 - 숫자3 - 숫자2)
    regex_5 = " ?사 ?업 ?자? ?등? ?록? ?번? ?호? ?N?o? ?:? ?(\d{3} ?- ?\d{2} ?- ?\d{3} ?- ?\d{2})"
    # 숫자3 - 숫자2 - 숫자5
    regex_6 = "\D(\d{3} ?- ?\d{2} ?- ?\d{5})\D"
    regex_7 = "(\d{3} ?- ?\d{2} ?- ?\d{5})\D"
    # 사업자 등록번호 뽑아내고 남는 찌꺼기 제거
    regex_8 = " ?사 ?업 ?자 ? ?등? ?록? ?번? ?호? ?-? ?:? ?"
    regex_9 = " ?등 ?록 ?번 ?호 ?:? ?"
    # 10자리로 되어있는 사업자 등록번호 및 이레귤러 케이스들 나누어서 저장하게 치환
    data_save = re.sub(regex_1, r'\1-\2-\3', data_save)
    data_save = re.sub(regex_2, r'\1-\2-\3', data_save)
    data_save = re.sub(regex_3, r'\1-\2-\3', data_save)

    registration_number_4 = re.findall(regex_4, data_save)
    registration_number.extend(registration_number_4)
    data_save = Remover(regex_4, data_save)

    registration_number_5 = re.findall(regex_5, data_save)
    registration_number.extend(registration_number_5)
    data_save = Remover(regex_5, data_save)

    registration_number_6 = re.findall(regex_6, data_save)
    registration_number.extend(registration_number_6)
    data_save = Remover(regex_6, data_save)

    registration_number_7 = re.findall(regex_7, data_save)
    registration_number.extend(registration_number_7)
    data_save = Remover(regex_7, data_save)

    data_save = Remover(regex_8, data_save)
    data_save = Remover(regex_9, data_save)
    
    if len(registration_number) > 0:
        return registration_number[0]
    elif re.search('\d{3}-\d{2}-\d{5}', data_save):
        return data_save
    else: 
        return ''

# 전화번호
def Phone_Number(data_save):
    phone_number = []
    fixed_phone_number_to_list = []
    fixed_phone_number = ''

    regex_1 = " ?전? ?화? ?번? ?호?:? ?핸? ?드? ?폰? ?:?\D(01[0|6-9][-]?\d{3,4}[-]?\d{4})\D"
    regex_2 = " ?전? ?화? ?번? ?호? ?:? ?[\(]?\D(0\d{1,2}-\d{3,4}-\d{4})[\)]?"
    regex_3 = " ?전? ?화 ?번 ?호 ?:? ?[\(\[]?(0\d{1,2}[ -]{0,}\d{3,4}[ -]{0,}\d{4})"
    regex_4 = " ?전 ?화 ?번 ?호 ?:? ?(\d{3}-\d{4})"
    regex_5 = " ?전 ?화 ?번 ?호 ?[:;]? ?"
    regex_6 = " ?[\(\[]? ?T ?E ?L ?[:;]? ?[\d-]+[\)\]]? ?"
    regex_7 = " ?T ?E ?L ?[\)\]]? ?(\d{2,4}-?\d{2,4})"
    regex_8 = " [\(\[]? ?T ?E ?L ?[\)\]]? ?"

    phone_number_1 = re.findall(regex_1, data_save)
    phone_number.extend(phone_number_1)
    data_save = Remover(regex_1, data_save)

    phone_number_2 = re.findall(regex_2, data_save)
    phone_number.extend(phone_number_2)
    data_save = Remover(regex_2, data_save)

    phone_number_3 = re.findall(regex_3, data_save)
    phone_number.extend(phone_number_3)
    data_save = Remover(regex_3, data_save)

    phone_number_4 = re.findall(regex_4, data_save)
    phone_number.extend(phone_number_4)
    data_save = Remover(regex_4, data_save)

    data_save = Remover(regex_5, data_save)

    phone_number_6 = re.findall(regex_6, data_save)
    phone_number.extend(phone_number_6)
    data_save = Remover(regex_6, data_save)

    phone_number_7 = re.findall(regex_7, data_save)
    phone_number.extend(phone_number_7)
    data_save = Remover(regex_7, data_save)

    data_save = Remover(regex_8, data_save)
    try:
        fixed_phone_number = re.sub(' ?- ?', '', phone_number[0])
        fixed_phone_number = re.sub(' ', '', fixed_phone_number)

    except:
        fixed_phone_number = ''

    fixed_phone_number_to_list.append(fixed_phone_number)

    return data_save, fixed_phone_number_to_list

# 영수증 내 주소 수집
def Address(data_save):
    address = []

    regex_1 = "가? ?맹? ?점? ? ?주 ?소 ?:? ?[가-힣]{1,}시? ?[가-힣]{1,}구? ?[가-힣]{0,}\d{0,2} ?[동로][가-힣]{0,}\d{0,3}번? ?길? ?\d{0,3} ?\d? ?층? ?-? ?\d?\d?번? ?지?\d{0,} ?층? ?\d{0,}호?"
    regex_2 = "가? ?맹? ?점? ? ?주 ?소 ?:? ?[\D ]+시 ?\D+구 ?\D+[동로]"
    regex_3 = "가 ?맹 ?점 ?명? ?:? ?(\D+병 ?원 ?)"
    regex_4 = " ?\)? ?정? ?상? ?매? ?입? ?가 ?맹 ?점 ?명? ?:? ?정? ?보? ?즉? ?시? ?결? ?제? ?\/? ?사? ?업? ?자? ?2?4?시?\D+병원"
    regex_5 = "\( ?\D+ ?동 ?\)"
    ## 도 뒤에 ? 추가, 번?길? 사이에 지? 추가
    regex_6 = " ?[가-힣]+도? ?[가-힣]+시 ?[가-힣]{0,}구?로?동?번?길? ?[가-힣1-9]{0,}구?로?동?번?길? ?\d?층?"

    address_1 = re.findall(regex_1, data_save)
    address.extend(address_1)
    data_save = Remover(regex_1, data_save)

    address_2 = re.findall(regex_2, data_save)
    address.extend(address_2)
    data_save = Remover(regex_2, data_save)

    address_3 = re.findall(regex_3, data_save)
    address.extend(address_3)
    data_save = Remover(regex_3, data_save)

    address_4 = re.findall(regex_4, data_save)
    address.extend(address_4)
    data_save = Remover(regex_4, data_save)

    address_5 = re.findall(regex_5, data_save)
    address.extend(address_5)
    data_save = Remover(regex_5, data_save)

    address_6 = re.findall(regex_6, data_save)
    address.extend(address_6)
    data_save = Remover(regex_6, data_save)

    #return data_save, address
    
    if len(address) > 0:
        return address[0]
    else: 
        return ''


###### 합계 정보 ######
# 금액관련 중복데이터 및 다중 데이터 발생시 실질데이터를 가장 큰값 혹은 가장 작은 값으로 선택
def find_one(data):
    int_data = []
    result = []
    size_Type = "min"
    if len(data) > 0:
        for i in data:
            if i != "":
                try:
                    ch_int = int(
                        i.replace(',', '').replace(' ', '').replace('.', '').replace('-', '').replace('/', '').replace(
                            ':', ''))
                    int_data.append(ch_int)
                except ValueError:
                    continue
                if ch_int >= 0:
                    size_Type = "max"
        if size_Type == "max":
            if len(int_data) > 0:
                result.append(format(max(int_data), ','))  # 중복되는 총계 및 잘못된 총계값 필터링을 위해 최대값 추출
            else:
                return 0
        else:
            if len(int_data) > 0:
                result.append(format(min(int_data), ','))  # 중복되는 총계 및 잘못된 총계값 필터링을 위해 최솟값 추출 (할인에서 사용)
            else:
                return 0
        return result
    else:
        return 0


# 합계
def Total_Sum(data_save):
    total_sum = []
    regex_1 = " ?[가-힣]{2,3} ?의 ?합 ?계 ?([1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3}) [1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3} ?원?"
    regex_2 = " ?[가-힣]{2,3} ?의 ?합 ?계 ?([1-9]\d{0,2}[,\.]\d{3}) [1-9]\d{0,2}[,\.]\d{3} ?원?"
    regex_3 = " ?[가-힣]{2,3} ?의 ?합 ?계 ?([1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3}) ?원?"
    regex_4 = " ?[가-힣]{2,3} ?의 ?합 ?계 ?([1-9]\d{0,2}[,\.]\d{3}) ?원?"
    regex_5 = " ?품? ?목? ?결? ?제? ?금? ?액?총? ?포? ?[함암]? ? ?중? ?간? ?합 ?계 ?금? ?액? ?:? ?([1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3}) ?원?"
    regex_6 = " ?품? ?목? ?결? ?제? ?금? ?액?총? ?포? ?[함암]? ? ?중? ?간? ?합 ?계 ?금? ?액? ?:? ?([1-9]\d{0,2}[,\.]\d{3}) ?원?"
    regex_7 = " ?총? ?청? ?구? ?금 ?액 ?:? ?([1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3}) ?원? ? ?[1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3} ?원?"
    regex_8 = " ?총? ?청? ?구? ?금 ?액 ?:? ?([1-9]\d{0,2}[,\.]\d{3}) ?원? ? ?[1-9]\d{0,2}[,\.]\d{3} ?원?"
    regex_9 = " ?총? ?청? ?구? ?금 ?액 ?:? ?([1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3}) ?원?"
    regex_10 = " ?총? ?청? ?구? ?금 ?액 ?:? ?([1-9]\d{0,2}[,\.]\d{3}) ?원?"
    regex_11 = " ?진? Sign ?:? "
    regex_12 = " ?결 ?제 ?[요예] ?[청정] ?:? ?([1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3})"
    regex_13 = " ?결 ?제 ?[요예] ?[청정] ?:? ?([1-9]\d{0,2}[,\.]\d{3})"
    regex_14 = " DC "
    regex_15 = " ?구? ?분? ?내? ?용? ?일? ?자? ?세? ?부? ?용? ?품? ?내?역? ?품? ?목? ?단? ?가? ? ?수 ?량 금 ?액 ?단? ?가? ?항? ?목? ?"
    regex_16 = " ?총? ?청? ?구? ?적? ?용? ?금 ?액 ?:?"
    regex_17 = " ?결? ?제? ?전? ?체? ?품? ?목? ?포? ?함? ?합 ?계 ?:? ? ?0? ?0? ?0?(\d{0,} ?[\d]{0,}[, ]{0,2}\d{0,})원?"
    regex_18 = " ?\( ?V ?A ?T ? ?포? ?함? ?\) ?([1-9]\d{0,2}[,\.]\d{3}[,\.]\d{3}) ?원?"
    regex_19 = " ?\( ?V ?A ?T ? ?포? ?함? ?\) ?([1-9]\d{0,2}[,\.]\d{3}) ?원?"
    regex_20 = " ?\( ?V ?A ?T ? ?포? ?함? ?\) ?([1-9]\d{0,2}) ?원?"

    total_sum_1 = re.findall(regex_1, data_save)

    total_sum.extend(total_sum_1)
    data_save = Remover(regex_1, data_save)

    total_sum_2 = re.findall(regex_2, data_save)
    total_sum.extend(total_sum_2)
    data_save = Remover(regex_2, data_save)

    total_sum_3 = re.findall(regex_3, data_save)
    total_sum.extend(total_sum_3)
    data_save = Remover(regex_3, data_save)

    total_sum_4 = re.findall(regex_4, data_save)
    total_sum.extend(total_sum_4)
    data_save = Remover(regex_4, data_save)

    total_sum_5 = re.findall(regex_5, data_save)
    total_sum.extend(total_sum_5)
    data_save = Remover(regex_5, data_save)

    total_sum_6 = re.findall(regex_6, data_save)
    total_sum.extend(total_sum_6)
    data_save = Remover(regex_6, data_save)

    total_sum_7 = re.findall(regex_7, data_save)
    total_sum.extend(total_sum_7)
    data_save = Remover(regex_7, data_save)

    total_sum_8 = re.findall(regex_8, data_save)
    total_sum.extend(total_sum_8)
    data_save = Remover(regex_8, data_save)

    total_sum_9 = re.findall(regex_9, data_save)
    total_sum.extend(total_sum_9)
    data_save = Remover(regex_9, data_save)

    total_sum_10 = re.findall(regex_10, data_save)
    total_sum.extend(total_sum_10)
    data_save = Remover(regex_10, data_save)

    data_save = Remover(regex_11, data_save)

    total_sum_12 = re.findall(regex_12, data_save)
    total_sum.extend(total_sum_12)
    data_save = Remover(regex_12, data_save)

    total_sum_13 = re.findall(regex_13, data_save)
    total_sum.extend(total_sum_13)
    data_save = Remover(regex_13, data_save)

    data_save = Remover(regex_14, data_save)
    data_save = Remover(regex_15, data_save)
    data_save = Remover(regex_16, data_save)

    total_sum_17 = re.findall(regex_17, data_save)
    total_sum.extend(total_sum_17)
    data_save = Remover(regex_17, data_save)

    total_sum_18 = re.findall(regex_18, data_save)
    total_sum.extend(total_sum_18)
    data_save = Remover(regex_18, data_save)

    total_sum_19 = re.findall(regex_19, data_save)
    total_sum.extend(total_sum_19)
    data_save = Remover(regex_19, data_save)

    total_sum_20 = re.findall(regex_20, data_save)
    total_sum.extend(total_sum_20)
    data_save = Remover(regex_20, data_save)

    # 총계 금액으로 선택된 데이터들 중 가장 큰 금액 선택
    find_total_sum = find_one(total_sum)
    if find_total_sum != 0:
        total_sum = find_total_sum
    
    # 총계 금액이 없을 경우 빈 문자열 출력
    if len(total_sum) > 0:
        return total_sum[0]
    else: 
        return ''


###### 진단 정보 ######

# 컬럼 유형에 따른 정규식 컴파일

#  단가 수량 금액
aqa = re.compile(
    "( |^)(\d{0,3}[,.]\d{3}|0|\d{1,3}[,.]\d{1,3}[,.]\d{3}|\d{0,3}\d{3}원) (\d+\.\d{1,2}|\d{1,2}|!|I) (\d{0,3}[,.]\d{3}|0|\d{1,3}[,.]\d{1,3}[,.]\d{3}|\d{0,3}\d{3}원)($| )")
#  단가 수량
aq = re.compile("( |^)(\d{0,3}[,.]\d{3}|0|\d{1,3}[,.]\d{1,3}[,.]\d{3}|\d{0,3}\d{3}원) (\d+\.\d{1,2}|\d{1,2}|!|I)($| )")
#  수량 금액
qa = re.compile("( |^)(\d+\.\d{1,2}|\d{1,2}|!|I) (\d{0,3}[,.]\d{3}|0|\d{1,3}[,.]\d{1,3}[,.]\d{3}|\d{0,3}\d{3}원)($| )")
#  수량 할인 금액
qda = re.compile(
    "( |^)(\d+\.\d{1,2}|\d{1,2}|!|I) (\d*[,.]\d{3}|0) (\d{0,3}[,.]\d{3}|0|\d{1,3}[,.]\d{1,3}[,.]\d{3}|\d{0,3}\d{3}원)($| )")

# 컬럼 유형별 : 컴파일러, 수량 추출 위치, 금액 추출 위치 저장 
do_aqa = {'compiler':aqa, 'quant': 3, 'amount': 4}
do_aq = {'compiler':aq, 'quant': 3, 'amount': 2}
do_qa = {'compiler':qa, 'quant': 2, 'amount': 3}
do_qda = {'compiler':qda, 'quant': 2, 'amount': 4}

dowhat = {'aqa':do_aqa, 'aq':do_aq, 'qa':do_qa, 'qda':do_qda}


# 제외 용도
cols = re.compile('수 ?량|소 ?계|금 ?액|내 ?역|기타 \(\d+|진료 \(\d+|용품 \(\d+|입원 \(\d+|백신 \(\d+|미용 \(\d+') # 컬럼 및 소목차
lessormore = re.compile('^ ?할인 ?$|\(C:|\(P:|(?<!\S)[-\+](\d+[,.])?\d{3}(?!\S)|\(\d*[,.]\d{3}\)') # 할인/이벤트 line 구분
toolow = re.compile('비과세(?!\))|사업자|대 ?표 ?자|담 ?당 ?자?|수의사|고객|동물명|\d{4}-\d{2}-\d{2}|결 ?제|\[20\d{7}\]') # 무관한 line 구분
endhere = re.compile('청 ?구 ?금 ?액|총 ?액|총 ?금 ?액|^합 ?계|영 ?수 ?액|부 ?가 ?세[ 액]|과세 ?품목 ?합계|표시가 되어 있는') # 진단 추출 끝낼 지점 지정

# 동물명 
name_type = '(?<![가-힣])동물명(?!원) ?:? ?([가-힣]+)|동물이름 ?:? ?([가-힣]+)| ?\(?([가-힣]+)[a-zA-Z]* ?\[\d{8,9}\]?'
name = re.compile('(?<![가-힣])동물명(?!원) ?:? ?([가-힣]+)|동물이름 ?:? ?([가-힣]+)| ?\(?([가-힣]+)[a-zA-Z]* ?\[\d{8,9}\]?')

# 위의 컴파일러들 ("윗줄" 연결 여부 결정에 사용)
nope = [aqa, qa, aq, qda, cols, lessormore, toolow]


def get_keywords():
    keys = pd.DataFrame()
    with open('./Keyword_updated.json', 'r', encoding='UTF8') as f:
        keywords = json.load(f)
        for i, label in enumerate(keywords.get('진단명')):
            realwords = []

            for j, real in enumerate(keywords.get('진단명').get(label)):
                realwords.append(real.lower())

            df_new = pd.DataFrame({'word': realwords, 'label': [label] * len(realwords)})
            keys = pd.concat([keys, df_new]).reset_index().iloc[:, 1:]
    keys = keys.drop_duplicates().sort_values('word').set_index('word')
    return keys


fam = ['진료(일반)', '진료(야간)', '진료(입원)', '진료(초진)', '진료(재진)']  # desc family
path_now = "./"


def parse_receipt_to_json(json_file):
    print(json_file)

    file_path = "./receipt.json"

    with open(file_path, 'w') as outfile:
        json.dump(json_file, outfile)

    global Satze_dft, keys
    global this_receipt, Desc, Quant, Amount, Name, image

    Satze_dft = data_load_into_df(file_path)
    keys = get_keywords()

    #   병원 정보 DataFrame
    Text = ' '.join(Satze_dft[ receipt ].values)
    temp = []

    temp.extend( [Registration_Number(Text).strip()] )
    temp.extend( [Phone_Number(Text)[-1][-1].strip()] )
    temp.extend( [Address(Text).strip()] )
    temp.extend( [Hospital_name(Text).strip()] )
    
    ##  사업자등록번호, 주소, 전화번호, 병원명 검증 및 새로운 명 반환
    ver_registration_number, ver_phone_number, ver_address, ver_hospital_name = check_hospital_info(temp)
    
    df_info = pd.DataFrame( {'동물병원':[ver_hospital_name], '사업자 번호':[ver_registration_number], '전화번호': [ver_phone_number], '주소':[ver_address]} ).T.rename(columns = {0:''})

    #   합계 정보 추출
    total = Total_Sum(Text)

    total_info = pd.DataFrame( {'합계' : [ total ]}).T.rename(columns = { 0 : '' })

    
    #   진단 내용 DataFrame

    thisreceipt = pd.DataFrame({'영수증 번호':[], '동물명':[], '진단내용':[], '수량':[], '금액':[]})
    
    Desc = []  # 진단
    Quant = []  # 수량
    Amount = []  # 금액
    Name = []  # 이름
    petname = ''   # 없는 경우 대비

    pet_label = []

    compiler_name = typeofcols(receipt)

    for j, satz in enumerate(Satze_dft[ receipt ].dropna()):  # FOR on Satze_dft[ receipt ][ j ]

        # 진단내역 지난 후의 line일 경우 => 해당 영수증 검수 
        if endhere.search(satz) is not None:
            break
            
        # 1) 동물 이름
        if re.search( name_type , satz):
            matched = name.search(satz).group()
            petname = re.sub(  '.*동물(명|이름) ?:? ?|^\(|\(|[a-zA-Z]* ?\[\d{8,9}\]?'  , '', matched  ).strip() 
        
        # 2) 항목 유형별 [진단/수량/금액] 처리
        # 무의미 line 아닌 경우에만
        elif realcolname(satz):
            compiler_name = realcolname(satz)
            Name, Desc, Quant, Amount, desc = get_NDQA(compiler_name , receipt, j, petname)
            
            row_label = []
            
            # 진단 단어들 => Keywords.json 단어 목록과 비교
            d = re.sub('\s+', ' ', desc)
            
            for realword in list(keys.index):
                if (realword in d) & (type(keys['label'][realword]) == str):
                    if (( len(set( row_label ).intersection( fam )) > 0 ) & ( keys['label'][realword] in fam)) | (keys['label'][realword] in row_label):
                        pass
                        
                    else:
                        row_label = row_label + [ keys['label'][realword] ]
                            
                elif (realword in d) & (type(keys['label'][realword]) != str):
                    row_label = row_label + list( keys['label'][realword] )
                        
            pet_label.append(', '.join(set(row_label)))

    df_new = pd.DataFrame(
        {'영수증 번호': [receipt]*len(Desc), '동물명': Name, '진단내용' : Desc, '수량':Quant, '금액':Amount})
    thisreceipt = pd.concat([thisreceipt, df_new]).reset_index().iloc[:, 1:]
    
    labeled_receipt = pd.DataFrame(
        {'영수증 번호': [receipt]*len(Desc), '동물명': Name, '진단내용' : pet_label, '수량':Quant, '금액':Amount})
    
    print(thisreceipt)
    print(labeled_receipt)
    print(df_info)
    html = thisreceipt.to_html(justify='center')
    reg_html = labeled_receipt.to_html(justify='center')
    df_info = df_info.to_html(justify='center')


    return [html, reg_html, df_info, total_info] 

    # return labeled_df, allreceipt


def data_load_into_df(json_path):
    image = json_path
    global receipt

    receipt = image.split('_')[-1].split('.')[0]
    with open(json_path, 'r') as f:
        pet = json.load(f)

    this_pet_txts = []
    satz = ''

    for i, j in enumerate(pet.get('images')[0].get('fields')):

        satz += j.get('inferText') + ' '
        if j.get('lineBreak'):
            this_pet_txts.append(satz)
            satz = ''

    Satze_df = pd.DataFrame(this_pet_txts).rename(columns={0: receipt})

    return Satze_df


# 윗줄 포함 여부 판단

def upper(compiler, receipt, row_no):
    if row_no > 0:
        upperrow = Satze_dft[receipt][row_no]
        if sum([True if (n.search( upperrow ) is None) else False for n in nope]) == len(nope):
            return True
        else:
            return False
    else:
        return False


# 윗줄 포함 여부 결정 후 desc 내용 확정

def withupperline(compiler, receipt, j):
    
    global rows
    rows = []
    
    satz = Satze_dft[ receipt ][ j ]

    desc = satz[ : compiler.search(satz).start() ].strip()  # 지금 line j의 진단내용
    # desc = re.split('[( )]\d*,\d{3}[( ))]', desc)[-1].strip()     # <-- 1) 진단에서 금액부분 제거
    rows.append(j)

    # 윗줄의 진단내용 연결
    if upper(compiler, receipt, j - 1):
        upper_line = Satze_dft[receipt][j - 1]
        upper_line = re.split('[( )]\d*,\d{3}[( ))]', upper_line)[-1].strip()  # <-- 1) 진단에서 금액부분 제거

        desc = upper_line + ' ' + desc
        rows.append(j - 1)

    if upper(compiler, receipt, j - 1) & upper(compiler, receipt, j - 2):
        upper_line = Satze_dft[receipt][j - 2]
        upper_line = re.split('[( )]\d*,\d{3}[( ))]', upper_line)[-1].strip()  # <-- 1) 진단에서 금액부분 제거

        desc = upper_line + ' ' + desc
        rows.append(j - 2)

    desc = re.split('(^ |^|^\)) ?(\*|\-|\+)+', desc)[-1].strip()  # *으로 시작하는 비과세항목, 글머리기호 -/+ - */-/+ 부분 제거
    desc = re.sub('\d{6,}|!!|\|\|', '', desc).strip()   # 6개 이상 연속 숫자 제거

    rows = sorted(rows)

    return desc


def get_NDQA(compiler_name, receipt, j, petname):
    
    satz = Satze_dft[ receipt ][ j ]
    
    # 수량 Quantity + labeling
    quant = dowhat[ compiler_name ]['compiler'].search(satz).group( dowhat[ compiler_name ]['quant'] )
    quant = re.sub('!|I', '1', quant)
    
    # 금액 Amount + labeling
    amount = dowhat[ compiler_name ]['compiler'].search(satz).group( dowhat[ compiler_name ]['amount'] )
    amount = re.sub('[,.]|원', '', amount)
    amount = str(format( int(amount), ','))
    
    # 진단 Description + labeling
    desc = withupperline( dowhat[ compiler_name ]['compiler'] , receipt, j )
    
    Name.append( petname )
    Desc.append( desc )
    Quant.append( quant )
    Amount.append( amount )
    
    return Name, Desc, Quant, Amount, desc


# 영수증의 "컬럼 형식" 파악하고 그에 따라 적합한 [컴파일러 이름] 할당
def typeofcols(receipt):
    coltype = {"단가수량금액" : 'aqa', "수량금액DC" : 'qa', "수량할인금액" : 'qda'}
    for typ in coltype:
        if typ in re.sub('\s', '', ' '.join(Satze_dft[ receipt ].dropna())):
            return coltype[typ]
    return 'qa'


# 수량, 금액이 실제로 나타난 형식에 따라 적합한 [컴파일러 이름] 할당
def realcolname(satz):
    if (lessormore.search(satz) is None) & (toolow.search(satz) is None) & (cols.search(satz) is None): 
        if aqa.search(satz) is not None : 
            return 'aqa'
        elif aq.search(satz) is not None : # 해당 줄의 금액 부분 안 읽힌 경우
            return 'aq'
        elif qda.search(satz) is not None:
            return 'qda'
        elif qa.search(satz) is not None : # 해당 줄의 단가 부분 안 읽힌 경우
            return 'qa'
        else:
            return False


'''
    print(thisreceipt)

    html = thisreceipt.to_html(justify='center')

    return html
'''

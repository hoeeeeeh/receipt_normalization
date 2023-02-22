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
    with open('Keyword.json', 'r', encoding='UTF8') as f:
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

    Satze_dft, Words_dft = data_load_into_df(file_path)
    keys = get_keywords()

    thisreceipt = pd.DataFrame({'receipt': [], 'Name': [], 'Desc': [], 'Quant': [], 'Amount': []})

    # 영수증 i       # FOR on Santze_dft[ receipt ]

    Desc = []  # 진단
    Quant = []  # 수량
    Amount = []  # 금액
    Name = []  # 이름

    pet_label = []

    compiler_name = typeofcols(receipt)

    for j, satz in enumerate(Satze_dft[receipt].dropna()):  # FOR on Satze_dft[ receipt ][ j ]

        # 진단내역 지난 후의 line일 경우 => 해당 영수증 검수 
        if endhere.search(satz) is not None:
            break
            
        # 1) 동물 이름
        petname = ''   # 없는 경우 대비
        if re.search( name_type , satz):
            matched = name.search(satz).group()
            petname = re.sub(  '.*동물(명|이름) ?:? ?|^\(|\(|[a-zA-Z]* ?\[\d{8,9}\]?'  , '', matched  ).strip() 
        
        # 2) 항목 유형별 [진단/수량/금액] 처리
        # 무의미 line 아닌 경우에만
        elif realcolname(satz):
            compiler_name = realcolname(satz)
            Name, Desc, Quant, Amount = get_NDQA(compiler_name , receipt, j, petname)
            
            row_label = []
            row_desc = ''

            # 여러 줄에 흩어져 있는 진단들 한 줄로 모으기 (단어 단위로)
            for i in rows:
                row_desc = row_desc + ' ' + Satze_dft[ receipt ][ i ].lower()

            # 진단 단어들 => Keywords.json 단어 목록과 비교
            d = re.sub('\s+', ' ', row_desc)
            
            for realword in list(keys.index):
                if (realword in d) & (type(keys['label'][realword]) == str):
                    if (( len(set( row_label ).intersection( fam )) > 0 ) & ( keys['label'][realword] in fam)) | (keys['label'][realword] in row_label):
                        pass
                        
                    else:
                        row_label = row_label + [ keys['label'][realword] ]
                            
                elif (realword in d) & (type(keys['label'][realword]) != str):
                    row_label = row_label + list( keys['label'][realword] )

            pet_label.append(list(set(row_label)))

    df_new = pd.DataFrame(
        {'receipt': [receipt] * len(Desc), 'Name': Name, 'Desc': Desc, 'Quant': Quant, 'Amount': Amount})
    thisreceipt = pd.concat([thisreceipt, df_new]).reset_index().iloc[:, 1:]
    labeled_receipt = pd.DataFrame(
        {'receipt': [receipt] * len(Desc), 'Name': Name, 'Desc': pet_label, 'Quant': Quant, 'Amount': Amount})

    print(thisreceipt)
    print(labeled_receipt)
    html = thisreceipt.to_html(justify='center')
    reg_html = labeled_receipt.to_html(justify='center')

    return [html, reg_html]

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
    desc = re.sub('[( )]\d*,\d{3}[( ))]', ' ', desc)     # <-- 1) 진단에서 금액부분 제거
    rows.append(j)

    # 윗줄의 진단내용 연결
    if upper(compiler, receipt, j - 1):
        upper_line = Satze_dft[receipt][j - 1]
        upper_line = re.sub('[( )]\d*,\d{3}[( ))]', ' ', upper_line)  # <-- 1) 진단에서 금액부분 제거

        desc = upper_line + ' ' + desc
        rows.append(j - 1)

    if upper(compiler, receipt, j - 1) & upper(compiler, receipt, j - 2):
        upper_line = Satze_dft[receipt][j - 2]
        upper_line = re.sub('[( )]\d*,\d{3}[( ))]', ' ', upper_line)  # <-- 1) 진단에서 금액부분 제거

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
    
    # 진단 Description + labeling
    desc = withupperline( dowhat[ compiler_name ]['compiler'] , receipt, j )
    
    Name.append( petname )
    Desc.append( desc )
    Quant.append( quant )
    Amount.append( amount )
    
    return Name, Desc, Quant, Amount


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

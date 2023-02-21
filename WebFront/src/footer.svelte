<div id="footer">
    <div id="nori_info" class="infoText">
        <div class='info_div'>
            <span class="nori_title nori_info_class">
                주식회사 노리스페이스 Norispace Co., Ltd.
            </span>
        </div>
        <div class='info_div'>
            <span class="nori_subtitle nori_info_class">
                서울특별시 노원구 동일로 174길 27 서울창업디딤터 213호
            </span>
        </div>
    </div>
    <div id="nori_link">
        <div class="link_div">
            <a href="https://www.norispace.com/">웹사이트</a>
            <a href="">이용약관</a>
            <a href="https://www.norispace.com/contact-norispace">문의하기</a>
        </div>
        <div class="link_div">
            <p id="nori_copyright"> © Norispace Co., Ltd All Rights Reserved </p>
        </div>
    </div>
</div>

<style>
    
    #footer {
        background-color: #eff1f6;
        height: 20%;
    }

    #nori_link{
        float: left;
        width: 50%;
        height: 100%;
        display: flex;
        flex-flow: column;
        align-items: center;
        justify-content: center;
        text-align: right;
    }

    #nori_info {
        float: left;
        width: 50%;
        height: 100%;
        display: flex;
        flex-flow: column;
        align-items: center;
        justify-content: center;
        text-align: left;
    }

    .info_div{
        width: 100%;
        margin-left : 40%;
    }

    .link_div{
        width: 100%;
        margin-right : 40%;
    }

    a{
        font-size : 0.5em;
        color:#767676;
    }
    a:link{
        color: #767676; 
        text-decoration: none;
    }

    .nori_info_class {
        flex: 1;
        text-align: left;
        margin: 2px;
        display: flex;
        flex-flow: column;
        align-items: left;
        text-align: left;
        overflow: hidden;
    }
    .nori_title {
        font-size: 1em;
        justify-content: end;
    }
    .nori_subtitle {
        justify-content: baseline;
        font-size: 0.5em;
    }

    #nori_copyright{
        font-weight: lighter;
        margin-top : 0px;
        font-size : 0.5em;
    }
</style>

<script>
    // 0ABCGGER
    // 0000BBFA
    // 00FFRRBC
    import {
        resultData,
        mode
    } from './store.js';

    function removeAllChildNodes(parent) {
        if (parent != null){
            while (parent.firstChild) {
                parent.removeChild(parent.firstChild);
            }
        }
    }


    export function resetResultTable(){
        document.querySelectorAll('.resultTableWrapper').forEach((item) => {
            removeAllChildNodes(item);
        })
    }
    //window.onload = agreementsDetection;






    function ocr(){
        console.log($resultData)
        document.getElementById("resultTableWrapper_before_reg").innerHTML = $resultData[0]
        document.getElementById("resultTableWrapper_after_reg").innerHTML = $resultData[1]
        document.getElementById("resultInfoTableWrapper").innerHTML = $resultData[2]
        

        let dfs = document.querySelectorAll(".resultTableWrapper")

        for (let i = 0; i < dfs.length; i++) {
            let df = dfs.item(i)
            df.style.cssText = `
                width: 100%;
                height: auto;
                padding: 10px;
                border-collapse: collapse;
                border-color: #E1E1E1;
                font-size: 0.8em;
                text-align: center;
                border-spacing: 15px;
            `
        }

        let info_thead = document.querySelector("#resultInfoTableWrapper table thead");
        info_thead.style = `
            display: none;
        `
    }

    export function loadResultTable(){
        resetResultTable()

        if($mode == 'ocr'){
            ocr()
        }else{
            agreementsDetection()
        }
    }

    //window.onload = loadResultTable;
</script>


<style>
    .resultTitleWrapper{
      width: auto;
      box-sizing: border-box;
      border-bottom: 2px solid #E1E1E1;
      height: 10%;
    }
    #resultTitle{
        padding-left: 20px;
        font-weight: bold;
        font-size: 1.5em;
        color: #2282F4;
    }
    #resultTable{
        width: auto;
        height: auto;
        padding: 10px;
        border-collapse: collapse;
        border-color: #E1E1E1;
        font-size: 0.8em;
        text-align: center;
    }
    .resultContentWrapper{
        width: auto;
        height: 86%;
        margin: 2%;
        position: relative;
        display: flex;
        align-items: center;  
        flex-direction: column;
    }
    #resultContent{
        width: 100%;
        height: 100%;
    }
    .resultTableWrapper{
        padding: 15px;
        flex: 3;
        width: 100%;
        height: 100%;
        flex-flow: column;
        align-items:center;
        justify-content:center;
        text-align: center;
        border-collapse: collapse;
        overflow-y: scroll;
    }

    /* Hide scrollbar for Chrome, Safari and Opera */
    .resultTableWrapper::-webkit-scrollbar {
    display: none;
    }

    /* Hide scrollbar for IE, Edge and Firefox */
    .resultTableWrapper {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
    }

    .resultInfoTableWrapper{
        flex: 1;
        width: 100%;
        height: auto;
    }

</style>
<div id = 'resultContent'>
    <div class='resultTitleWrapper infoText'>
        <p id='resultTitle' class='infoText'> 추출 데이터 </p>
    </div>
    <div class='resultContentWrapper'>
        <div id="resultInfoTableWrapper" class="resultInfoTableWrapper"></div>
        <div id="resultTableWrapper_before_reg" class="resultTableWrapper">
        </div>
        <div id="resultTableWrapper_after_reg" class="resultTableWrapper">
        </div>
    </div>
</div>



<!-- 
[['0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0'],
 ['1', '1', '1', '0', '1', '1', '1', '1', '1', '1', '0'],
 ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
 ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']]

-->
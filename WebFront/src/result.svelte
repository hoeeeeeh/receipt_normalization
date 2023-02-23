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

        let dfs = document.querySelectorAll(".dataframe")

        for (let i = 0; i < dfs.length; i++) {
            let df = dfs.item(i)
            df.style.cssText = `
                width: 100%;
                height: 100%;
                padding: 10px;
                border-collapse: collapse;
                border-color: #E1E1E1;
                font-size: 0.8em;
                text-align: center;
            `
        }
    }

    function ocr1(){
        console.log($resultData['receipt'][0])
        console.log($resultData['receipt'].length)
        let tableData = [];
            console.log($resultData); 
            for(let i =0; i<$resultData['receipt'].length; i++){
                tableData.push([
                    $resultData['receipt'][i],
                    $resultData['Name'][i],
                    $resultData['Desc'][i],
                    $resultData['Quant'][i],
                    $resultData['Amount'][i],
                ])
            }

            console.log(tableData);


            

            let thead = document.createElement("thead");
            thead.style.height = "50px";
            let tbody = document.createElement("tbody");

            table.appendChild(thead);
            table.appendChild(tbody);

            let row_1 = document.createElement('tr');
            row_1.style.backgroundColor = "#F9F9F9";
            let heading_1 = document.createElement('th');
            heading_1.innerHTML = "receipt";
            let heading_2 = document.createElement('th');
            heading_2.innerHTML = "Name";
            let heading_3 = document.createElement('th');
            heading_3.innerHTML = "Desc";
            let heading_4 = document.createElement('th');
            heading_4.innerHTML = "Quant";
            let heading_5 = document.createElement('th');
            heading_5.innerHTML = "Amount";

            row_1.appendChild(heading_1);
            row_1.appendChild(heading_2);
            row_1.appendChild(heading_3);
            row_1.appendChild(heading_4);
            row_1.appendChild(heading_5);
            thead.appendChild(row_1);


            // for(let i =0; i<questions.length; i++){
            //     let row_2 = document.createElement('tr');
            //     let row_question = document.createElement('td');
            //     row_question.innerHTML = tableData[i][0];
            //     row_question.style.flex = 3;
            //     row_question.style.padding = "15px";
            //     row_question.width = "70%";
            //     row_question.style.textAlign = "left";
            //     row_2.appendChild(row_question);

            //     for(let j=1; j<tableData[i].length; j++){
            //         let row_answer = document.createElement('td');
            //         row_answer.style.flex = 1;
            //         if(tableData[i][j] == 1){
            //             row_answer.style.backgroundImage = "url('/img/check.svg')";
            //             row_answer.style.backgroundRepeat = "no-repeat";
            //             row_answer.style.backgroundPosition = "center center";
            //         }
            //         row_2.appendChild(row_answer);
            //     }
            //     tbody.appendChild(row_2);
            // }

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
    }
    #resultContent{
        width: 100%;
        height: 100%;
    }
    .resultTableWrapper{
        padding: 15px;
        flex: 1;
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

</style>
<div id = 'resultContent'>
    <div class='resultTitleWrapper infoText'>
        <p id='resultTitle' class='infoText'> 추출 데이터 </p>
    </div>
    <div class='resultContentWrapper'>
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
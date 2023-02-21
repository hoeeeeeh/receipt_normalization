<script>
    import Dropzone from "./dropzone.svelte";
    import Result from "./result.svelte";
    import Loading from "./loading.svelte";
    import {
        mode
    } from './store.js';

    let child_result;
    let dropzone_;

    import {
      scanboxBackgroundColor,
      resultData,
      uploadedFile,
    } from './store.js';

    let files = {
	  accepted: [],
	  rejected: []
	};



	function handleFilesSelect(e) {
	  const { acceptedFiles, fileRejections } = e.detail;
	  files.accepted = [...files.accepted, ...acceptedFiles];
	  files.rejected = [...files.rejected, ...fileRejections];
	}

    function postToServer() {
      let formData = new FormData()
      formData.append("file", $uploadedFile)
      console.log(formData)

      const container = document.querySelector('#contentWrapper');

      const element = new Loading({
        target: container
      })
      fetch(`http://localhost:8000/${$mode}/upload`, {
      // fetch(`http://172.30.1.119:6002/${$mode}/upload`, {
        method: 'POST',
        cache: 'no-cache',
        body: formData,
      })
      .then((response) => response.json())
      .then((data) => {
        console.log(data)
        
        $resultData = data

        child_result.loadResultTable();

        container.removeChild(document.querySelector("#loadingDialog"));
      })

    }

    function resetAll(){
      dropzone_.resetDropzone()
      child_result.resetResultTable()
    }
</script>
<div id='contentWrapper'>
  
    <div class='spacer'></div>
    <div id='dropzoneWrapper' class='contents'>
        <Dropzone on:drop={handleFilesSelect} bind:this = {dropzone_}/>
        <div class='dropzoneInteractWrapper'>
            <div id ='reselectBtnWrapper' class='interact'>
              <button id = 'reselectBtn' on:click={resetAll}></button>
            </div>
            <div id ='runBtnWrapper' class='interact' style:background-color={$scanboxBackgroundColor}>
              <button id='runBtn' on:click={postToServer} disabled>
    
              </button>
            </div>
        </div>

    </div>
    <div id='resultWrapper' class='contents'>
        <Result bind:this = {child_result}></Result>
    </div>
    <div class='spacer'></div>
</div>

<style type="text/scss">

#re-select-icon{
      display: flex;
      justify-content: center;
      align-items: center;  
      height: 100%;
    }

    #re-selectbtn{
      background-color: transparent;
      border: 0px;
    }

    .re-select-btn-content{
      height: 100%;
      float: left;
    }

    .interact{
      height: 100%;
    }

    #reselectBtnWrapper{
      flex: 5;
      background-color: #FFFFFF;
      padding-left: 0.6em;
      height: auto;
    }

    #reselectBtn{
      background-color: transparent;
      width: 100%;
      height: 100%;
      border: none;

      background-image: url('/img/re_select.svg');
      background-repeat: no-repeat;
      background-position: left;
    }

    #runBtnWrapper{
      flex: 2;
      background-color: #C4C4C4;
    }

    #runBtn{
      width: 100%;
      height: 100%;
      background-color: transparent;
      background-image: url('/img/scanbox.svg');
      background-repeat: no-repeat;
      background-position:center center;
    }
    .dropzoneInteractWrapper{
        flex:1;
        display: flex;
        height: 10%;
        box-sizing: border-box;
        border-top: 2px solid #E1E1E1;
    
        }

    #dropzoneWrapper{
        flex: 2;
        display: flex;
        flex-flow: column;
    }
    #resultWrapper{
        flex: 3;
    }
    .contents{
        display: flex;
        margin: 40px 10px 40px 10px;
        background-color: #FFFFFF;
        height: auto;
    }

    .spacer{
        display: flex;
        flex: 1;
        background-color : #F5F7FC;
    }

    #contentWrapper{
        height: 90%;
        display: flex;
        background-color : #F5F7FC;
    }
    #resultWrapper{

    }
    #dropzoneWrapper{

    }
  

</style>
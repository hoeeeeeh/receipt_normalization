<script>

    import { fromEvent } from "file-selector";
    import {
      dropZoneBackgroundColor,
      dropZoneColor, 
      dropZoneWidth, 
      dropZoneDialogDisplay, 
      dropFileName, 
      dropZoneBackgroundImage,

      scanboxBackgroundColor,
      resultData,
      uploadedFile,
    } from './store.js';

    import {
      allFilesAccepted,
      composeEventHandlers,
      fileAccepted,
      fileMatchSize,
      isEvtWithFiles,
      isIeOrEdge,
      isPropagationStopped,
      TOO_MANY_FILES_REJECTION
    } from "./utils/index";
    import { onMount, onDestroy, createEventDispatcher } from "svelte";
    import { writable } from "svelte/store";
  
    //props
    /**
     * Set accepted file types.
     * See https://github.com/okonet/attr-accept for more information.
     */
    export let accept; // string or string[]
    export let disabled = false;
    export let getFilesFromEvent = fromEvent;
    export let maxSize = Infinity;
    export let minSize = 0;
    export let multiple = true;
    export let preventDropOnDocument = true;
    export let noClick = false;
    export let noKeyboard = false;
    export let noDrag = false;
    export let noDragEventsBubbling = false;
    export let containerClasses = "";
    export let containerStyles = "";
    export let disableDefaultStyles = false;
    export let name = "";
    const dispatch = createEventDispatcher();
    
    //state
  
    let state = {
      isFocused: false,
      isFileDialogActive: false,
      isDragActive: false,
      isDragAccept: false,
      isDragReject: false,
      draggedFiles: [],
      acceptedFiles: [],
      fileRejections: []
    };
  
    let rootRef;
    let inputRef;

    export function resetDropzone(){
      resetState()

      $dropZoneDialogDisplay = 'flex'
      $scanboxBackgroundColor = '#CBCBCB'
      document.getElementById("runBtn").disabled = true;
      document.getElementById('dropzoneContentWrapper_').style.backgroundImage = 'none';
      $dropFileName = '';
    }
  
    function resetState() {
      state.isFileDialogActive = false;
      state.isDragActive = false;
      state.draggedFiles = [];
      state.acceptedFiles = [];
      state.fileRejections = [];


    }

    function fileHoverStart(){
      $dropZoneBackgroundColor = "#F2F8FE";
      $dropZoneColor = "#2282F4";
      $dropZoneWidth = "2px";
    }

    function fileHoverEnd(){
      $dropZoneBackgroundColor = "#FFFFFF";
      $dropZoneColor = "#6B6B6B";
      $dropZoneWidth = "0px";
    }

  
    // Fn for opening the file dialog programmatically
    function openFileDialog() {
      if (inputRef) {
        inputRef.value = null; // TODO check if null needs to be set
        state.isFileDialogActive = true;
        inputRef.click();
      }
    }
  
    // Cb to open the file dialog when SPACE/ENTER occurs on the dropzone
    function onKeyDownCb(event) {
      // Ignore keyboard events bubbling up the DOM tree
      if (!rootRef || !rootRef.isEqualNode(event.target)) {
        return;
      }
  
      if (event.keyCode === 32 || event.keyCode === 13) {
        event.preventDefault();
        openFileDialog();
      }
    }
  
    // Update focus state for the dropzone
    function onFocusCb() {
      state.isFocused = true;
    }
    function onBlurCb() {
      state.isFocused = false;
    }
  
    // Cb to open the file dialog when click occurs on the dropzone
    function onClickCb() {
      if (noClick) {
        return;
      }
  
      // In IE11/Edge the file-browser dialog is blocking, therefore, use setTimeout()
      // to ensure React can handle state changes
      // See: https://github.com/react-dropzone/react-dropzone/issues/450
      if (isIeOrEdge()) {
        setTimeout(openFileDialog, 0);
      } else {
        openFileDialog();
      }
    }
  
    function onDragEnterCb(event) {
      event.preventDefault();
      stopPropagation(event);
  
      dragTargetsRef = [...dragTargetsRef, event.target];
  
      if (isEvtWithFiles(event)) {
        Promise.resolve(getFilesFromEvent(event)).then(draggedFiles => {
          if (isPropagationStopped(event) && !noDragEventsBubbling) {
            return;
          }
  
          state.draggedFiles = draggedFiles;
          state.isDragActive = true;

          fileHoverStart()
  
          dispatch("dragenter", {
            dragEvent: event
          });
        });
      }
    }
  
    function onDragOverCb(event) {
      event.preventDefault();
      stopPropagation(event);
  
      if (event.dataTransfer) {
        try {
          event.dataTransfer.dropEffect = "copy";
        } catch {} /* eslint-disable-line no-empty */
      }
  
      if (isEvtWithFiles(event)) {
        dispatch("dragover", {
          dragEvent: event
        });
      }
  
      return false;
    }
  
    function onDragLeaveCb(event) {
      event.preventDefault();
      stopPropagation(event);
  
      // Only deactivate once the dropzone and all children have been left
      const targets = dragTargetsRef.filter(
        target => rootRef && rootRef.contains(target)
      );
      // Make sure to remove a target present multiple times only once
      // (Firefox may fire dragenter/dragleave multiple times on the same element)
      const targetIdx = targets.indexOf(event.target);
      if (targetIdx !== -1) {
        targets.splice(targetIdx, 1);
      }
      dragTargetsRef = targets;
      if (targets.length > 0) {
        return;
      }
  
      state.isDragActive = false;
      
      fileHoverEnd()

      state.draggedFiles = [];
  
      if (isEvtWithFiles(event)) {
        dispatch("dragleave", {
          dragEvent: event
        });
      }
    }
  
    function onDropCb(event) {
      event.preventDefault();
      stopPropagation(event);
  
      dragTargetsRef = [];
  
      if (isEvtWithFiles(event)) {
        dispatch("filedropped", {
          event
        })

        fileHoverEnd()
        $dropZoneDialogDisplay = 'none'
        $scanboxBackgroundColor = '#2282F4'
        document.getElementById("runBtn").disabled = false;

        Promise.resolve(getFilesFromEvent(event)).then(files => {
          if (isPropagationStopped(event) && !noDragEventsBubbling) {
            return;
          }
  
          const acceptedFiles = [];
          const fileRejections = [];
  
          files.forEach(file => {
            const [accepted, acceptError] = fileAccepted(file, accept);
            const [sizeMatch, sizeError] = fileMatchSize(file, minSize, maxSize);
            if (accepted && sizeMatch) {
              fileHoverEnd()
              $dropZoneDialogDisplay = 'none'
              $dropFileName = file.name

              $uploadedFile = file

              const filereader = new FileReader()
              filereader.readAsDataURL(file)
              filereader.onload = function(){
         
                console.log(filereader.result)
                document.getElementById('dropzoneContentWrapper_').style.backgroundImage = `url(${filereader.result}`;
                document.getElementById('dropzoneContentWrapper_').style.backgroundSize = 'contain';
                $dropZoneBackgroundImage = filereader.result
              }

              acceptedFiles.push(file);
            } else {
              const errors = [acceptError, sizeError].filter(e => e);
              fileRejections.push({ file, errors });
            }
          });
  
          if (!multiple && acceptedFiles.length > 1) {
            // Reject everything and empty accepted files
            acceptedFiles.forEach(file => {
              fileRejections.push({ file, errors: [TOO_MANY_FILES_REJECTION] });
            });
            acceptedFiles.splice(0);
          }
  
          state.acceptedFiles = acceptedFiles;
          state.fileRejections = fileRejections;
  
          dispatch("drop", {
            acceptedFiles,
            fileRejections,
            event
          });
  
          if (fileRejections.length > 0) {
            dispatch("droprejected", {
              fileRejections,
              event
            });
          }
  
          if (acceptedFiles.length > 0) {
            dispatch("dropaccepted", {
              acceptedFiles,
              event
            });
          }
        });
      }
      resetState();
    }
  
    function composeHandler(fn) {
      return disabled ? null : fn;
    }
  
    function composeKeyboardHandler(fn) {
      return noKeyboard ? null : composeHandler(fn);
    }
  
    function composeDragHandler(fn) {
      return noDrag ? null : composeHandler(fn);
    }
  
    function stopPropagation(event) {
      if (noDragEventsBubbling) {
        event.stopPropagation();
      }
    }
  
    // allow the entire document to be a drag target
    function onDocumentDragOver(event) {
      if (preventDropOnDocument) {
        event.preventDefault();
      }
    }
  
    let dragTargetsRef = [];
    function onDocumentDrop(event) {
      if (!preventDropOnDocument) {
        return;
      }
      if (rootRef && rootRef.contains(event.target)) {
        // If we intercepted an event for our instance, let it propagate down to the instance's onDrop handler
        return;
      }
      event.preventDefault();
      dragTargetsRef = [];
    }
  
    // Update file dialog active state when the window is focused on
    function onWindowFocus() {
      // Execute the timeout only if the file dialog is opened in the browser
      if (state.isFileDialogActive) {
        setTimeout(() => {
          if (inputRef) {
            const { files } = inputRef;
  
            if (!files.length) {
              state.isFileDialogActive = false;
              dispatch("filedialogcancel");
            }
          }
        }, 300);
      }
    }
  
    onDestroy(() => {
      // This is critical for canceling the timeout behaviour on `onWindowFocus()`
      inputRef = null;
    });
  
    function onInputElementClick(event) {
      event.stopPropagation();
    }
  </script>
  
  <style>
    .dropzone {
      width: 100%;
      height: auto;
      flex: 8;
      flex-flow: column;
      text-align: left;
      align-items: center;
      padding: 0px 0px 0px 0px;
      background-color: #FFFFFF;
      outline: none;
      transition: border 0.24s ease-in-out;
    }
    .dropzone:focus {
      border-color: #2196f3;
    }
    .a {
        color: #2196f3
    }
    .dropzoneTitleWrapper{
      width: auto;
      box-sizing: border-box;
      border-bottom: 2px solid #E1E1E1;
      height: 11%;
    }

    #dropzoneTitle{
      padding-left: 20px;
      font-size: 1.5em;
      font-weight: bold;
    }

    .dropzoneContentWrapper{
      height: 89%;
      box-sizing: border-box;
      border: 0px solid #2282F4;
      background-repeat: no-repeat;
      background-position:center center;
      background-size: contain;

    }

    .dropZoneDialogWrapper{
      height: 100%;
      display: flex;
      flex-flow: column;
      align-items: center;
      justify-content: center;
      text-align: center;
    }

    #dragIcon{
      max-width: 10%;
      max-height: 10%;

      min-width: 10%;
      min-height: 10%;

      padding: 2em;
    }

    #dropFileName{
      padding-right : 15px;
    }


  </style>
  
  <svelte:window on:focus={onWindowFocus} on:dragover={onDocumentDragOver} on:drop={onDocumentDrop} />
  
  <!-- svelte-ignore a11y-no-noninteractive-tabindex -->
  <div
    bind:this={rootRef}
    tabindex="0"
    class="
        {disableDefaultStyles ? '' : 'dropzone'}
        {containerClasses}
    "
    style={containerStyles}
    on:keydown={composeKeyboardHandler(onKeyDownCb)}
    on:focus={composeKeyboardHandler(onFocusCb)}
    on:blur={composeKeyboardHandler(onBlurCb)}
    on:dragenter={composeDragHandler(onDragEnterCb)}
    on:dragover={composeDragHandler(onDragOverCb)}
    on:dragleave={composeDragHandler(onDragLeaveCb)}
    on:drop={composeDragHandler(onDropCb)}>
    <input
      {accept}
      {multiple}
      type="file"
      name={name}
      autocomplete="off"
      tabindex="-1"
      on:change={onDropCb}
      on:click={onInputElementClick}
      bind:this={inputRef}
      style="display: none;" />
    <slot>
      <div class='dropzoneTitleWrapper infoText'>
        <p id='dropzoneTitle' class='infoText'> 원본 데이터 </p>
        <p id='dropFileName' style:margin-left=auto> {$dropFileName} </p>
      </div>
      <div class='dropzoneContentWrapper' id='dropzoneContentWrapper_'
      style:background-color={$dropZoneBackgroundColor} style:color={$dropZoneColor} style:border-width={$dropZoneWidth}
      style="background-image: url('{$dropZoneBackgroundImage}')">
        <div class='dropZoneDialogWrapper' style:display={$dropZoneDialogDisplay}>
          <img id='dragIcon' src="img/drag.svg" alt="drag" on:click={composeHandler(onClickCb)} />
          <p class='infoText'> 여기에 파일을 드래그하여 <br> 업로드 해주세요.</p>
        </div>
      </div>
    </slot>
  </div>
  
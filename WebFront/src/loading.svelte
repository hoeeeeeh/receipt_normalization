<div id="loadingDialog">
    <div id="loadingCircle"></div>
</div>



<style>

#loadingDialog{
    width: 100%;
    height: 100%;
    position:absolute;
    display: flex;
    flex-flow: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    backdrop-filter: blur(2px);
}

#loadingCircle {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(255,255,255,.3);
    border-radius: 90%;
    border-top-color: #0B172A;
    animation: spin 1s ease-in-out infinite;
    -webkit-animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { -webkit-transform: rotate(360deg); }
}
@-webkit-keyframes spin {
  to { -webkit-transform: rotate(360deg); }
}
</style>
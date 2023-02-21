<script>
    import Content from "./content.svelte";
    import Footer from "./footer.svelte";
	  import Header from "./header.svelte";
    import Loading from "./loading.svelte";

    let header;
    let content;
  </script>
  
  <style>
    #wrapper{
      position: relative;
      width: 100%;
      height: 100%;
      min-width: var(--site-width);
      min-height: 100%;

    }
  </style>

  <div id="wrapper">
    <Header bind:this = {header}/>
    <Content bind:this = {content}/>
    <Footer/>
  </div>
js_slope = """
<script type='text/javascript'>
  
    var slopeModal = document.getElementById("slope-modal")
    var openSlope = document.getElementById("slope-btn");
    var closeSlope = document.getElementById("close-slope");

    function addBlur(){
        document.getElementById("content").className = "blurred";
        slopeModal.className = "visible";
    }

    function unBlur(){
        document.getElementById("content").className = "";
        slopeModal.className = "invisible";
    }

    openSlope.addEventListener('click', addBlur);
    closeSlope.addEventListener('click', unBlur);
    
</script>
"""

js_aspect = """
<script type='text/javascript'>
  
    var aspectModal = document.getElementById("aspect-modal")
    var openAspect = document.getElementById("aspect-btn");
    var closeAspect = document.getElementById("close-aspect");

    function addBlur(){
        document.getElementById("content").className = "blurred";
        aspectModal.className = "visible";
    }

    function unBlur(){
        document.getElementById("content").className = "";
        aspectModal.className = "invisible";
    }

    openAspect.addEventListener('click', addBlur);
    closeAspect.addEventListener('click', unBlur);
    
</script>
"""

js_sun = """
<script type='text/javascript'>
  
    var sunModal = document.getElementById("sun-modal")
    var openSun = document.getElementById("sun-btn");
    var closeSun = document.getElementById("close-sun");

    function addBlur(){
        document.getElementById("content").className = "blurred";
        sunModal.className = "visible";
    }

    function unBlur(){
        document.getElementById("content").className = "";
        sunModal.className = "invisible";
    }

    openSun.addEventListener('click', addBlur);
    closeSun.addEventListener('click', unBlur);
    
</script>
"""

js = js_slope + js_aspect + js_sun
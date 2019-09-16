// voor de klok
$( document ).ready(function() {
 
    $('#timer').text(getdate());
 
});
function getdate(){
            var today = new Date();
            var h = today.getHours();
            var m = today.getMinutes();
            var s = today.getSeconds();
             if(s<10){
                 s = "0"+s;
             }
             if(m<10){
             		m = "0"+m;
             }

            $("#timer").html(h+'<span class="blink">:</span>'+m+":"+s);
 
             setTimeout(function(){getdate()}, 1000);
}

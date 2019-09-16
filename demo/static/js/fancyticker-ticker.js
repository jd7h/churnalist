window.onload=function(){
var nr_headlines = document.getElementsByClassName("headline").length
var nr_ticker_headlines = 0

var i = 0;
if(nr_headlines>1){
$('#placeholder').remove()
    document.getElementsByClassName("headline")[i].setAttribute("style","display:inline;")
}

setInterval(function(){
    document.getElementsByClassName("headline")[i].setAttribute("style","display:none;")
    i++;
    if(i>=nr_headlines){
    i = 0;
    }
    document.getElementsByClassName("headline")[i].setAttribute("style","display:inline;")
}, 5000);

// bepalen hoeveel gewone headliens er zijn
setInterval(function(){
    if (document.getElementsByClassName("headline").length != nr_headlines){
        nr_headlines = document.getElementsByClassName("headline").length
    }
}, 1000)

// bepalen hoeveel ticker headlines er zijn
// voor dynamische snelheid
setInterval(function(){
    if (document.getElementsByClassName("ticker__item").length != nr_ticker_headlines){
    		console.log("Nr ticker items: " + nr_ticker_headlines + ", nr of elements: " + document.getElementsByClassName("ticker__item").length)
        nr_ticker_headlines = document.getElementsByClassName("ticker__item").length;
      // for adding ticker items
      // als we zien dat het aantal ticker headlines is opgehoogd moet de snelheid omlaag
      // snelheid = 20 seconden per headline
      var newspeed = nr_ticker_headlines * 25;
      $(".ticker-wrap .ticker").css({"-webkit-animation-duration": (newspeed + "s"), "animation-duration": newspeed + "s"});
    }
}, 1000)

$( ".headline" ).click(function() {
  $(this).addClass("removed_headline");
  $(this).removeClass("headline");
  $(this).attr("style","display:none;");
  nr_headlines--;
});


    }


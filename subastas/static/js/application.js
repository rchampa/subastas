var inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");
var outbox = new ReconnectingWebSocket("ws://"+ location.host + "/submit");

var DELAY = 3500;

inbox.onmessage = function(message) {
  var data = JSON.parse(message.data);

  //{ idprod:id_prod, userid:user_id, bid:new_price }

  var query = ''+data.idprod;
  var price = document.getElementById(query);

  if(price){
    if(data.bid != -1){  
      price.innerHTML = ""+data.bid+"€";
      var $ = jQuery.noConflict(); 
      $("#update-"+query).show().delay(DELAY).fadeOut();  
    }
    else{
      price.innerHTML = ""+data.price_last+"€";
      var userid = localStorage.getItem("userid");
      if(userid==data.userid){
        var $ = jQuery.noConflict(); 
        $("#alert-"+query).show().delay(DELAY).fadeOut();      
      }
    }
  }

};

inbox.onclose = function(){
    console.log('inbox closed');
    this.inbox = new WebSocket(inbox.url);
};

outbox.onclose = function(){
    console.log('outbox closed');
    this.outbox = new WebSocket(outbox.url);
};

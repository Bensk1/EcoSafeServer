var ajax = require('ajax');
var UI = require('ui');
var Vibe = require('ui/vibe');

messages = ["You accelerated too fast", "You braked too hard", "Turn engine off!", "Keep distance", "Take care when turning", "You are too fast"]

address = "http://172.30.1.139:5000/shouldVibrate";
keepForOneMore = 0;

setInterval(function(){
ajax({url: address, type: 'json'},
  function(data) {
    bodyString = "";
    event = false;
    for (i = 0; i < 6; ++i) {
      if (data[i] === true) {
        event = true;
        bodyString += messages[i] + "\n";
      }
    }
    if (event === true) {
      keepForOneMore = 2;
      Vibe.vibrate('long');
      var splashCard = new UI.Card({
        title: "Be careful!",
        body: bodyString
      });
      splashCard.show();
    }
    if (keepForOneMore > 0) {
      --keepForOneMore;
    } else {
      var splashCard = new UI.Card({
        title: "",
        body: ""
      });
      splashCard.show();
    }

  },
  function(error) {
    console.log('Ajax failed: ' + error);
  }
);}, 1000);


// var Firebase = require("firebase");
// var myFirebaseRef = new Firebase("https://twitposer.firebaseio.com/");

// var express = require('express');
// var app = express();
// app.use(express.static('public'));

// app.get('/', function (req, res) {
//   res.send('Hello World!');
// // });

// app.listen(3000, function () {
//   console.log('Example app listening on port 3000!');
// });



var twitterQuery = process.argv.slice(2)[0];

console.log(twitterQuery);
var request = require('request');
var sentiment = require('sentiment');
var Twitter = require('twitter');
var fs = require('fs');
var sentimentURI = "http://swoogle.umbc.edu/SimService/GetSimilarity?operation=api&phrase1=";
var client = new Twitter({
  consumer_key: 'Sk7OelPqA5iQZPKNJb2Rctv0l',
  consumer_secret: 'kwuf2TUX5nUmGGWiAsA9Fbe5B6ODPpt1ztTKAr1gPJwn3YIuvD',
  access_token_key: '22217035-6mIZcwv5JQRXm3RmTpMNqSZGY1CM6DQLtXwdoI4Zw',
  access_token_secret: 'BSQ3RNRspbbzLPw7Knbw4AiPdnkldMZ8n0sB7yM41PNGY'
});
var params = {screen_name: twitterQuery};


var analyzedTweets = [];
function analyzeTweet(tweetText, allTweetTexts, rawTweet){
  var tweetRelations = new Array;
  allTweetTexts.forEach(function(tweet) {
    if (tweetText != tweet){
      request(sentimentURI + tweetText + '&phrase2=' + tweet, function (error, response, body) {
        var relation = parseFloat(body.replace(/\r?\n|\r/g,''));

        if(body === '' || body === ' ') {
          relation = 0;
        }

        tweetRelations.push(relation);
        if (tweetRelations.length > numTweets - 2){
          var loudness = ((tweetText.length - tweetText.replace(/[A-Z]/g, '').length) / tweetText.length);  
          analyzedTweets.push({
            'similarity': tweetRelations,
            'loudness': loudness,
            'sentiment':  sentiment(tweetText).score,
            'hashtags': rawTweet.entities.hashtags.length
          }); 
          if (analyzedTweets.length > numTweets - 2){
            write_file(twitterQuery, analyzedTweets);
            return true;
          }
        }
      });
    }
  });
  return tweetRelations;
}

numTweets = 0;
client.get('statuses/user_timeline', params, function(error, tweets, response){
  if (!error) {
    numTweets = tweets.length;
    var allTweetTexts = [];
    for (var i = 0; i < tweets.length; i++){
      allTweetTexts.push(tweets[i].text);
    }
  	for (var i = 0; i < tweets.length; i++){
  		var text = tweets[i].text;
  		if (i > 0){
  			var analyzedTweet = analyzeTweet(tweets[i].text, allTweetTexts, tweets[i]);
  		}
  	}
  }
});


function write_file(twitterQuery, analyzedTweets){
	fs.writeFile("" + twitterQuery + '.json', JSON.stringify(analyzedTweets), function(err) {
    if(err) {
        return console.log(err);
    }
    console.log("The file was saved!");
}); 
}


// var r1 = sentiment('Cats are stupid.');
// console.dir(r1);        // Score: -2, Comparative: -0.666

// var r2 = sentiment('Cats are totally amazing!');
// console.dir(r2);        // Score: 4, Comparative: 1


// myFirebaseRef.on("value", function(snapshot) {
//   console.log(snapshot.val());  // Alerts "San Francisco"
// });


// client.stream('statuses/filter', {track: 'javascript'}, function(stream) {
//   stream.on('data', function(tweet) {
//     console.log(tweet.text);
//   });
 
//   stream.on('error', function(error) {
//     throw error;
//   });
// });



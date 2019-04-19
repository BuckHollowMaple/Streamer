// Init casper
var casper = require('casper').create({
    pageSettings: {
        loadImages: false,//The script is much faster when this field is set to false
        loadPlugins: false,
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    }
});

var term = casper.cli.get('term');
gInput = ((term).split(' ')).join('+');

casper.start().thenOpen("https://www.google.com/search?q="+gInput, function() {});

casper.wait(3000);

casper.then(function(){
    var next_episode = this.evaluate(function() {	
	return document.getElementsByClassName('title')[0].innerText
    });
    text = require('utils').dump(next_episode)
    this.capture('um.png');

    console.log(text);
});

casper.run();

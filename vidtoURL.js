// Init casper
var casper = require('casper').create({
    pageSettings: {
        loadImages: false,//The script is much faster when this field is set to false
        loadPlugins: false,
        userAgent: 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 Safari/537.22'
    }
});

var url = casper.cli.get('url');

casper.start().thenOpen(url, function() {});

casper.then(function(){
        var link = this.evaluate(function() {
		return window.location.href; 
        });

	casper.thenOpen(link, function() {});

	casper.wait(6000);

	casper.then(function(){
	    this.evaluate(function() {
		document.getElementById('btn_download').click();
	    });
	});

	casper.then(function(){
	    var js = this.evaluate(function() {
			var nodes = document.querySelectorAll("script");
			var list = [].slice.call(nodes);
			var innertext = list.map(function(e) { return e.innerText; }).join("\n");
			return innertext
		});
	    var test = js.split('[{file:"')[1].split('"')[0];
	    if (test) {
		console.log(test);
	    } else {
	        console.log(js.split(',{file:"')[1].split('"')[0]); 
	    }
	});
});

casper.run();

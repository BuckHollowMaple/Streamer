var args = process.argv.slice(2);

var nodemailer = require("nodemailer");
// create reusable transport method (opens pool of SMTP connections)
var smtpTransport = nodemailer.createTransport({
    service: "Gmail",
    auth: {
        user: "youremail",
        pass: "yourpassword"
    }
});

// setup e-mail data with unicode symbols
var mailOptions = {
    from: "Your name", // sender address
    to: "kindle email address", // list of receivers
    subject: "", // Subject line
    text: " ",
    attachments: [{
	filename: 'book.mobi',
        path: 'path to book',
	contentType: 'application/x-mobipocket-ebook',
    }],
}

// send mail with defined transport object
smtpTransport.sendMail(mailOptions, function(error, response){
    if(error){
        console.log(error);
    }else{
        console.log("Message sent: " + response.message);
    }

    // if you don't want to use this transport object anymore, uncomment following line
    smtpTransport.close(); // shut down the connection pool, no more messages
});

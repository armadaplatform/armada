var express = require('express');
var app = express();

var SERVICE_PORT = 80;

app.get('/', function (req, res) {
    res.send('Node.js service works!');
});

var server = app.listen(SERVICE_PORT, function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Express server listening on' + host + ':' + port + '.');
});

var http = require('http')

var server = http.createServer(function (req, res) {
  if (Math.random() < 0.40) {
    res.statusCode = 500;
    res.write('failed');
  } else {
    res.statusCode = 200;
    res.write('<!DOCTYPE html><html><head></head><body>hello world</body></html>');
  };

  setTimeout(() => {
    return res.end()
  }, 200 + Math.random() * 100);
});

server.listen(5000);

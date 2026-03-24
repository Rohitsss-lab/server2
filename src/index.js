const express = require('express');
const app = express();
const { version } = require('../package.json');
const PORT = 3002;

app.get('/', (req, res) => {
  res.json({
    service: 'server2',
    status: 'running',
    version: version,
    port: PORT
  });
});

app.listen(PORT, () => {
  console.log(`server1 service running on port ${PORT} — v${version}`);
});

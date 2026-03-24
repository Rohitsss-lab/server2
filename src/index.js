const express = require('express');
const app = express();
const PORT = 3002;

app.get('/', (req, res) => {
  res.json({
    service: 'server1',
    status: 'running',
    port: PORT
  });
});

app.listen(PORT, () => {
  console.log(`repo1 service running on port ${PORT}`);
});

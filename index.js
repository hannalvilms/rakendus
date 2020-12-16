const express = require('express')
const app = express()
require('dotenv').config()
const port = process.env.PORT || 3000

app.get('/', (req, res) => {
  res.send('Tere maailm')
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})

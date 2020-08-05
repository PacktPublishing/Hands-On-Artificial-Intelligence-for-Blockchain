const express = require('express')
const app = express()
const port = 3000

app.use(express.static('public'))

app.get('/', (req, res) => res.send('Welcome to DICTAO: Contact tracing web app!'))

app.listen(port, () => console.log(`DICTAO: Contact tracing web app listening at http://localhost:${port}`))

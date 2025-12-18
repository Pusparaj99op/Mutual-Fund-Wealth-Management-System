const express = require('express')
const path = require('path')
const app = express()

// Serve repo data and frontend build
app.use('/data', express.static(path.join(__dirname, '..', 'data')))
app.use(express.static(path.join(__dirname, '..', 'frontend', 'dist')))

// fallback to index.html from built frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'))
})

const port = process.env.PORT || 5000
app.listen(port, () => console.log(`Server running on http://localhost:${port}`))

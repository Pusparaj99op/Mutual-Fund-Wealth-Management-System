const express = require('express')
const path = require('path')
const app = express()

// Serve repo data and frontend build
app.use('/data', express.static(path.join(__dirname, '..', 'data')))
// Serve the Login Page Backgrounds folder so images like login.png can be loaded at /static/login.png
app.use('/static', express.static(path.join(__dirname, '..', 'Login Page Backgrounds')))
app.use(express.static(path.join(__dirname, '..', 'frontend', 'dist')))

// fallback to index.html from built frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'))
})

const port = process.env.PORT || 5000
app.listen(port, () => console.log(`Server running on http://localhost:${port}`))

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { createServer } = require('http');

const app = express();
const server = createServer(app);
const io = new Server(server);

app.use(express.static('public'));

io.on('connection', (socket) => {
    console.log('A user connected');
    socket.on('offer', (offer) => {
        socket.broadcast.emit('offer', offer);
    });
    socket.on('answer', (answer) => {
        socket.broadcast.emit('answer', answer);
    });
    socket.on('candidate', (candidate) => {
        socket.broadcast.emit('candidate', candidate);
    });
});

server.listen(8080, () => {
    console.log('WebRTC server running on port 8080');
});

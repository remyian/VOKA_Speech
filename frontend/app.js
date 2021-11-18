const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
var button = '';
var listening = false;

const listenToSocket = function () {
	socket.on('connected', function () {
		console.log('Verbonden met socket webserver');
	});
	socket.on('B2F_text', function (text) {
		console.log(text);
	});
};

const listenToUI = function () {
	button.addEventListener('click', function () {
		if (!listening) {
			console.log('STARTED');
			listening = true;
			socket.emit('F2B_start_listening', 'listen');
		} else {
			console.log('STOPPED');
			listening = false;
			socket.emit('F2B_start_listening', 'stop');
		}
	});
};

document.addEventListener('DOMContentLoaded', function () {
	console.info('DOM geladen');
	button = document.getElementById('btn-1');
	listenToSocket();
	listenToUI();
});

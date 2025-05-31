import { Command } from '@tauri-apps/plugin-shell';

window.start = async function () {
  fetch('http://localhost:8000/start', {
    method: 'POST'
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
  const ws = new WebSocket('ws://localhost:8000/ws/buttons');
  ws.onopen = () => {
    console.log('WebSocket connection established');
    let input = document.getElementById("wait_time");
    ws.send(input.value);

  };
  ws.onmessage = (event) => {
    console.log('Message from server:', event.data);
  }
  ws.onclose = () => {
    console.log('WebSocket connection closed');
  }
}
window.stop = async function () {
  fetch('http://localhost:8000/stop', {
    method: 'POST'
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
}

function setBinds(){
  const config = {
    a: document.getElementById("a").value.toLowerCase(),
    b: document.getElementById("b").value.toLowerCase(),
    select: document.getElementById("select").value.toLowerCase(),
    start: document.getElementById("start").value.toLowerCase(),
    up: document.getElementById("up").value.toLowerCase(),
    down: document.getElementById("down").value.toLowerCase(),
    left: document.getElementById("left").value.toLowerCase(),
    right: document.getElementById("right").value.toLowerCase()
  };

  fetch('http://localhost:8000/config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(config)
  })
  .then(response => response.json())
  .then(data => console.log('Success:', data))
  .catch(error => console.error('Error:', error));
}



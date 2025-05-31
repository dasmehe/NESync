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



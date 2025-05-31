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

/*const { invoke } = window.__TAURI__.core;

window.start = async function () {
   console.log("Starting the Python script...");

  // spawn Python process running your script
  const command = Command.create('python', ['backend/input.py']);
  const child = await command.spawn();

  child.stdout.on('data', line => {
    console.log(`stdout: ${line}`);
  });

  child.stderr.on('data', line => {
    console.error(`stderr: ${line}`);
  });

  await child.stdin.write("0.01\n");
}


window.stop = async function () {
  child.kill("SIGINT")
    .then(() => {
      console.log("Command stopped successfully");
    })
    .catch(err => {
      console.error("Error stopping command:", err);
    });
}*/


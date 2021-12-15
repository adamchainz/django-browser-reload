{
  const dataset = document.currentScript.dataset;
  const workerScriptPath = dataset.workerScriptPath;
  const eventsPath = dataset.eventsPath;

  const worker = new SharedWorker(workerScriptPath);

  worker.port.addEventListener('message', (event) => {
    if (event.data === "Reload") {
      location.reload()
    }
  });

  worker.port.postMessage({
    'type': 'initialize',
    'eventsPath': eventsPath,
  });

  worker.port.start();
}

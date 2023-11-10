'use strict'

{
  const dataset = document.currentScript.dataset
  const workerScriptPath = dataset.workerScriptPath
  const eventsPath = dataset.eventsPath

  if (!window.SharedWorker) {
    console.debug('😭 django-browser-reload cannot work in this browser.')
  } else {
    function debounce(func, timeout = 300){
      let timer;
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
      };
    }
    const worker = new SharedWorker(workerScriptPath, {
      name: 'django-browser-reload'
    })

    worker.port.addEventListener('message', (event) => {
      if (event.data === 'Reload') {
        debounce(() => location.reload());
      }
    })

    worker.port.postMessage({
      type: 'initialize',
      eventsPath
    })

    worker.port.start()
  }
}

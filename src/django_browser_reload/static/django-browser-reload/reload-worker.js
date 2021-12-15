let eventsPath = null;
let port = null;
let currentVersionId = null;
const defaultTimeoutMilliseconds = 100;
let timeOutMilliseconds = defaultTimeoutMilliseconds;
let eventSource = null;

addEventListener(
  'connect',
  (event) => {
    // Only keep one active port, for whichever tab was last loaded.
    if (port) {
      port.close();
    }
    port = event.ports[0];
    port.addEventListener('message', receiveMessage);
    port.start();
  }
)

receiveMessage = (event) => {
  if (event.data.type === "initialize") {
    const givenEventsPath = event.data.eventsPath;

    if (givenEventsPath !== eventsPath) {
      if (eventSource) {
        eventSource.close();
      }

      timeOutMilliseconds = defaultTimeoutMilliseconds;
      setTimeout(connectToEvents, 0);
    }

    eventsPath = event.data.eventsPath;
  }
};

connectToEvents = () => {
  if (!eventsPath) {
    setTimeout(connectToEvents, timeOutMilliseconds);
    return;
  }

  eventSource = new EventSource(eventsPath);

  eventSource.addEventListener('open', (event) => {
    console.debug("😎 django-browser-reload connected");
  });

  eventSource.addEventListener('message', (event) => {
    // Reset connection timeout when receiving a message, as it’s proof that
    // we are actually connected.
    timeOutMilliseconds = defaultTimeoutMilliseconds;

    const message = JSON.parse(event.data);

    if (message.type == "ping") {
      if (currentVersionId !== null && currentVersionId !== message.versionId) {
        console.debug("🔁 Triggering reload.")
        port.postMessage("Reload")
      }

      currentVersionId = message.versionId;
    } else if (message.type === "templateChange") {
      port.postMessage("Reload")
    }

  });

  eventSource.addEventListener('error', (event) => {
    eventSource.close()
    eventSource = null;
    timeOutMilliseconds = Math.round(Math.min(timeOutMilliseconds * 1.1, 10000))
    console.debug(
      "😅 django-browser-reload EventSource error, retrying in "
      + timeOutMilliseconds
      + "ms"
    )
    setTimeout(connectToEvents, timeOutMilliseconds)
  });
}

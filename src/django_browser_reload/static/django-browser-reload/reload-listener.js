'use strict'

{
  const dataset = document.currentScript.dataset
  const workerScriptPath = dataset.workerScriptPath
  const eventsPath = dataset.eventsPath

  const userPreference = localStorage.getItem('django-browser-reload:Enabled')
  let reloadEnabled = userPreference === 'true' || userPreference === null

  const addReloadContainer = () => {
    const browserReloadContainer = document.createElement('div')
    browserReloadContainer.id = 'djangoBrowserReloadContainer'

    const toggleButton = document.createElement('div')
    toggleButton.id = 'djangoBrowserReloadToggle'
    toggleButton.innerHTML = '<span>dj</span><div>BR</span>'

    if (!reloadEnabled) {
      toggleButton.classList.add('djbr-disabled')
    }

    browserReloadContainer.appendChild(toggleButton)
    document.body.appendChild(browserReloadContainer)

    const maxLeft =
      document.documentElement.clientWidth - browserReloadContainer.offsetWidth
    const containerLeft = Math.min(
      localStorage.getItem('django-browser-reload:Left') || maxLeft,
      maxLeft
    )
    browserReloadContainer.style.left = containerLeft + 'px'

    let startX
    let initialX
    let containerDragged = false

    toggleButton.addEventListener('click', () => {
      if (!containerDragged) {
        reloadEnabled = !reloadEnabled
        localStorage.setItem('django-browser-reload:Enabled', reloadEnabled)
        toggleButton.classList.toggle('djbr-disabled')
      }
    })

    const buttonMouseMove = (evt) => {
      if (containerDragged || evt.pageX !== startX) {
        let left = initialX + evt.pageX
        if (left < 0) {
          left = 0
        } else if (
          left + browserReloadContainer.offsetWidth >
          document.documentElement.clientWidth
        ) {
          left =
            document.documentElement.clientWidth -
            browserReloadContainer.offsetWidth
        }
        browserReloadContainer.style.left = left + 'px'
        containerDragged = true
      }
    }

    const buttonMouseUp = (evt) => {
      document.removeEventListener('mousemove', buttonMouseMove)
      if (containerDragged) {
        evt.preventDefault()
        localStorage.setItem(
          'django-browser-reload:Left',
          browserReloadContainer.offsetLeft
        )
        requestAnimationFrame(function () {
          containerDragged = false
        })
      }
      document.removeEventListener('mouseup', buttonMouseUp)
    }

    toggleButton.addEventListener('mousedown', function (evt) {
      evt.preventDefault()
      startX = evt.pageX
      initialX = browserReloadContainer.offsetLeft - startX
      document.addEventListener('mousemove', buttonMouseMove)
      document.addEventListener('mouseup', buttonMouseUp)
    })
  }

  if (!window.SharedWorker) {
    console.debug('😭 django-browser-reload cannot work in this browser.')
  } else {
    const worker = new SharedWorker(workerScriptPath, {
      name: 'django-browser-reload'
    })

    worker.port.addEventListener('message', (event) => {
      if (reloadEnabled && event.data === 'Reload') {
        location.reload()
      }
    })

    worker.port.postMessage({
      type: 'initialize',
      eventsPath
    })

    worker.port.start()

    document.addEventListener('DOMContentLoaded', addReloadContainer)
  }
}

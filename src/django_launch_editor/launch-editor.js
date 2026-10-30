(function () {
  'use strict'

  const data = JSON.parse(
    document.getElementById('django-launch-editor-data').textContent
  )

  async function openInEditor (button, status, token) {
    button.disabled = true
    status.className = 'django-launch-editor-status'
    status.textContent = 'Opening…'

    const body = new FormData()
    body.append('token', token)
    let error = null
    try {
      const response = await fetch(data.url, {
        method: 'POST',
        body,
        headers: { 'X-CSRFToken': data.csrfToken },
        mode: 'same-origin',
        credentials: 'same-origin'
      })
      if (!response.ok) {
        error = `Request failed with status ${response.status}.`
        if (response.headers.get('Content-Type') === 'application/json') {
          error = (await response.json()).error
        }
      }
    } catch (exc) {
      error = `Request failed: ${exc.message}`
    }

    button.disabled = false
    if (error === null) {
      status.textContent = ''
    } else {
      status.classList.add('error')
      status.textContent = error
    }
  }

  // Add a button after the text that follows the given element, such as
  // “, line 12, in view”.
  function addButton (element, token) {
    if (element === null || token === null) {
      return
    }
    if (element.nextSibling?.nodeType === Node.TEXT_NODE) {
      element = element.nextSibling
      element.textContent = element.textContent.trimEnd()
    }

    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'django-launch-editor'
    button.textContent = 'Open in editor'

    const status = document.createElement('span')
    status.className = 'django-launch-editor-status'
    status.setAttribute('role', 'status')

    button.addEventListener('click', (event) => {
      event.stopPropagation()
      openInEditor(button, status, token)
    })
    element.after(' ', button, ' ', status)
  }

  const frames = document.querySelectorAll('#browserTraceback li.frame')
  // Frames are matched up by position, so give up if Django’s template has
  // changed in a way that breaks that.
  if (frames.length === data.frames.length) {
    frames.forEach((frame, index) => {
      addButton(frame.querySelector(':scope > code.fname'), data.frames[index])
    })
    if (data.frames.length > 0) {
      addButton(
        document.querySelector('#summary .fname'),
        data.frames[data.frames.length - 1]
      )
    }
  }

  addButton(document.querySelector('#template p > strong'), data.template)
})()

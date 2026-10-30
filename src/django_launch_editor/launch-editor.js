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

  // Wrap the given nodes, such as the filename and line number, in a
  // button. Show the status after any text that follows, such as “, in view”.
  function addButton (nodes, token) {
    if (token === null) {
      return
    }

    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'django-launch-editor'
    button.title = 'Open in editor'
    nodes[0].before(button)
    button.append(...nodes)

    const status = document.createElement('span')
    status.className = 'django-launch-editor-status'
    status.setAttribute('role', 'status')
    const rest = button.nextSibling
    if (rest?.nodeType === Node.TEXT_NODE) {
      rest.textContent = rest.textContent.trimEnd()
      rest.after(' ', status)
    } else {
      button.after(' ', status)
    }

    button.addEventListener('click', (event) => {
      event.stopPropagation()
      openInEditor(button, status, token)
    })
  }

  // Return the filename element plus the following “, line 12” text.
  function filenameAndLine (element) {
    const text = element.nextSibling
    if (text?.nodeType === Node.TEXT_NODE) {
      const match = text.textContent.match(/^, line \d+/)
      if (match !== null) {
        text.splitText(match[0].length)
        return [element, text]
      }
    }
    return [element]
  }

  const frames = document.querySelectorAll('#browserTraceback li.frame')
  // Frames are matched up by position, so give up if Django’s template has
  // changed in a way that breaks that.
  if (frames.length === data.frames.length) {
    frames.forEach((frame, index) => {
      const fname = frame.querySelector(':scope > code.fname')
      if (fname !== null) {
        addButton(filenameAndLine(fname), data.frames[index])
      }
    })
    const fname = document.querySelector('#summary .fname')
    if (fname !== null && data.frames.length > 0) {
      addButton(filenameAndLine(fname), data.frames[data.frames.length - 1])
    }
  }

  // Template errors read “In template <code>name</code>, error at line
  // <strong>12</strong>”.
  const templateName = document.querySelector('#template p > code')
  if (templateName !== null) {
    const nodes = [templateName]
    const text = templateName.nextSibling
    const line = text?.nextSibling
    if (text?.nodeType === Node.TEXT_NODE && line?.nodeName === 'STRONG') {
      nodes.push(text, line)
    }
    addButton(nodes, data.template)
  }
})()

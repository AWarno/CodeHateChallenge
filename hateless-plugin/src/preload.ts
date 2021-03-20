const {
    ipcRenderer,
    contextBridge
} = require('electron');

contextBridge.exposeInMainWorld(
    "capture", {
        send: (data) => {
            ipcRenderer.invoke('capture', data)
        }
    })

contextBridge.exposeInMainWorld(
    "sound_alarm", {
        send: (data) => {
            ipcRenderer.invoke('sound_alarm', data)
        }
    })

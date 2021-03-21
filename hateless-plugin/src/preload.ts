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
    "getState", {
        send: (data) => {
            ipcRenderer.invoke('getStateToMain', data)
        },
        receive: (channel, func) => {
            let validChannels = ["getStateFromMain"];
            if (validChannels.includes(channel)) {
                ipcRenderer.on(channel, (event, ...args) => func(...args))
            }

        }
    })

contextBridge.exposeInMainWorld(
    "sound_alarm", {
        send: (data) => {
            ipcRenderer.invoke('sound_alarm', data)
        }
    })

contextBridge.exposeInMainWorld(
    "get_history", {
        send: (channel) => {
            let validChannels = ["historyToMain"];
            if (validChannels.includes(channel)) {
                ipcRenderer.invoke(channel)
            }
        },
        receive: (channel, func) => {
            let validChannels = ["historyFromMain"];
            if (validChannels.includes(channel)) {
                ipcRenderer.on(channel, (event, ...args) => func(...args))
            }
        }
    })

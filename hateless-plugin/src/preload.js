var _a = require('electron'), ipcRenderer = _a.ipcRenderer, contextBridge = _a.contextBridge;
contextBridge.exposeInMainWorld("capture", {
    send: function (data) {
        ipcRenderer.invoke('capture', data);
    }
});
contextBridge.exposeInMainWorld("sound_alarm", {
    send: function (data) {
        ipcRenderer.invoke('sound_alarm', data);
    }
});
//# sourceMappingURL=preload.js.map
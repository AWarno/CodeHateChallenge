var _a = require('electron'), ipcRenderer = _a.ipcRenderer, contextBridge = _a.contextBridge;
contextBridge.exposeInMainWorld("capture", {
    send: function (data) {
        ipcRenderer.invoke('capture', data);
    }
});
contextBridge.exposeInMainWorld("getState", {
    send: function (data) {
        ipcRenderer.invoke('getStateToMain', data);
    },
    receive: function (channel, func) {
        var validChannels = ["getStateFromMain"];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, function (event) {
                var args = [];
                for (var _i = 1; _i < arguments.length; _i++) {
                    args[_i - 1] = arguments[_i];
                }
                return func.apply(void 0, args);
            });
        }
    }
});
contextBridge.exposeInMainWorld("sound_alarm", {
    send: function (data) {
        ipcRenderer.invoke('sound_alarm', data);
    }
});
contextBridge.exposeInMainWorld("get_history", {
    send: function (channel) {
        var validChannels = ["historyToMain"];
        if (validChannels.includes(channel)) {
            ipcRenderer.invoke(channel);
        }
    },
    receive: function (channel, func) {
        var validChannels = ["historyFromMain"];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, function (event) {
                var args = [];
                for (var _i = 1; _i < arguments.length; _i++) {
                    args[_i - 1] = arguments[_i];
                }
                return func.apply(void 0, args);
            });
        }
    }
});
//# sourceMappingURL=preload.js.map
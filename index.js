var _a = require('electron'), app = _a.app, BrowserWindow = _a.BrowserWindow;
var path = require('path');
var gkm = require('gkm');
var max_log_size = 16384;
var log_cache = '';
function sendPack(content) {
    var endpoint_address = "127.0.0.1";
    var axios = require('axios');
    axios.post("http://" + endpoint_address + ":3000/isHate", { params: {
            content: content,
            time: new Date().getTime(),
        } }).then(function (response) {
        console.log(response);
    })
        .catch(function (error) {
        console.log(error);
    });
}
function sendCache() {
    sendPack(log_cache);
    log_cache = '';
}
function enable_observer() {
    app.dock.hide();
    gkm.events.on('key.*', function (key) {
        if (this.event === 'key.pressed') {
            switch (key[0]) {
                case 'Backspace':
                    log_cache = log_cache.substring(0, log_cache.length - 1);
                    break;
                case 'Enter':
                    sendCache();
                    break;
                default:
                    if (key[0].length == 1) {
                        log_cache += key[0];
                        if (log_cache.length > max_log_size) {
                            log_cache = log_cache.substring(1);
                        }
                    }
                    break;
            }
        }
        console.log(log_cache);
    });
    gkm.events.on('mouse.pressed', function (operation) { sendCache(); });
}
function createWindow() {
    // Create the browser window.
    var mainWindow = new BrowserWindow({
        width: 300,
        height: 480,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    });
    // and load the index.html of the app.
    mainWindow.loadFile('index.html');
    // Open the DevTools.
    // mainWindow.webContents.openDevTools()
}
app.whenReady().then(function () {
    enable_observer();
    createWindow();
    app.on('activate', function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0)
            createWindow();
    });
});
//# sourceMappingURL=index.js.map
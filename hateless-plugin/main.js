var electron = require('electron');
var app = electron.app, BrowserWindow = electron.BrowserWindow, ipcMain = electron.ipcMain;
var path = require('path');
var gkm = require('gkm');
var axios = require('axios');
var sound = require('sound-play');
var max_log_size = 16384;
var history_max_size = 100;
var endpoint_address = "127.0.0.1";
var observer = null;
var mainWindow = null;
var KeyMouseObserver = /** @class */ (function () {
    function KeyMouseObserver() {
        this.cache = '';
        this.history = [];
        this.sound_enabled = false;
        this.is_enabled = false;
    }
    KeyMouseObserver.prototype.enable_observer = function () {
        var self = this;
        gkm.events.on('key.*', function (key) {
            if (this.event === 'key.pressed') {
                switch (key[0]) {
                    case 'Backspace':
                        self.cache = self.cache.substring(0, self.cache.length - 1);
                        break;
                    case 'Enter':
                        self.queryIsHate();
                        break;
                    default:
                        if (key[0].length == 1) {
                            self.cache += key[0];
                            if (self.cache.length > max_log_size) {
                                self.cache = self.cache.substring(1);
                            }
                        }
                        break;
                }
            }
        });
        gkm.events.on('mouse.pressed', function (operation) { self.queryIsHate(); });
        this.is_enabled = true;
    };
    KeyMouseObserver.prototype.disable_observer = function () {
        this.cache = '';
        gkm.events.removeAllListeners('mouse.pressed');
        gkm.events.removeAllListeners('key.*');
        this.is_enabled = false;
    };
    KeyMouseObserver.prototype.enable_sound = function () {
        this.sound_enabled = true;
    };
    KeyMouseObserver.prototype.disable_sound = function () {
        this.sound_enabled = false;
    };
    KeyMouseObserver.prototype.queryIsHate = function () {
        var _this = this;
        var content = this.cache;
        this.history.push(content.slice());
        if (this.history.length > history_max_size)
            this.history.pop();
        this.cache = '';
        var axios_config = {
            headers: {
                'Content-Length': 0,
                'Content-Type': 'text/plain'
            },
            responseType: 'text'
        };
        axios.post("http://" + endpoint_address + "/ishate", content, axios_config).then(function (response) {
            if (response.data == 'True') {
                if (_this.sound_enabled) {
                    var soundPath = path.join(__dirname, "sounds", 'horns.m4a');
                    sound.play(soundPath);
                }
                if (electron.Notification.isSupported()) {
                    var notification = {
                        title: 'Hate speech detected!',
                        body: 'Hate speech detected in sentence ' + content
                    };
                    new electron.Notification(notification).show();
                }
            }
        })["catch"](function (error) {
            console.log(error);
        });
    };
    return KeyMouseObserver;
}());
function createWindow() {
    // Create the browser window.
    mainWindow = new BrowserWindow({
        width: 300,
        height: 480,
        resizable: false,
        maximizable: false,
        webPreferences: {
            // nodeIntegration: true
            preload: path.join(app.getAppPath(), 'src', 'preload.js')
        }
    });
    // and load the index.html of the app.
    mainWindow.loadFile('pages/index.html');
    // Open the DevTools.
    mainWindow.webContents.openDevTools();
}
app.whenReady().then(function () {
    observer = new KeyMouseObserver();
    ipcMain.handle('capture', function (event, enable) {
        if (enable)
            observer.enable_observer();
        else
            observer.disable_observer();
    });
    ipcMain.handle('sound_alarm', function (event, enable) {
        if (enable)
            observer.enable_sound();
        else
            observer.disable_sound();
    });
    ipcMain.handle('historyToMain', function (event) {
        var args = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            args[_i - 1] = arguments[_i];
        }
        mainWindow.webContents.send("historyFromMain", observer.history);
    });
    ipcMain.handle('getStateToMain', function (event) {
        var args = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            args[_i - 1] = arguments[_i];
        }
        mainWindow.webContents.send("getStateFromMain", [observer.is_enabled, observer.sound_enabled]);
    });
    createWindow();
    app.on('activate', function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0)
            createWindow();
    });
});
//# sourceMappingURL=main.js.map
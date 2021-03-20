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
var KeyMouseObserver = /** @class */ (function () {
    function KeyMouseObserver() {
        this.key_observer = null;
        this.mouse_observer = null;
        this.cache = '';
        this.history = [];
        this.sound_enabled = false;
    }
    KeyMouseObserver.prototype.enable_observer = function () {
        var cache = this.cache;
        var me = this;
        this.key_observer = gkm.events.on('key.*', function (key) {
            if (this.event === 'key.pressed') {
                switch (key[0]) {
                    case 'Backspace':
                        cache = cache.substring(0, cache.length - 1);
                        break;
                    case 'Enter':
                        me.queryIsHate();
                        break;
                    default:
                        if (key[0].length == 1) {
                            cache += key[0];
                            if (cache.length > max_log_size) {
                                cache = cache.substring(1);
                            }
                        }
                        break;
                }
            }
        });
        this.mouse_observer = gkm.events.on('mouse.pressed', function (operation) { me.queryIsHate(); });
    };
    KeyMouseObserver.prototype.disable_observer = function () {
        this.cache = '';
        gkm.events.removeAllListeners('mouse.pressed');
        gkm.events.removeAllListeners('key.*');
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
        this.history.push(content);
        if (this.history.length > history_max_size)
            this.history.pop();
        axios.post("http://" + endpoint_address + ":3000/ishate", { params: {
                content: content,
            } }).then(function (response) {
            if (electron.Notifications.isSupported()) {
                if (_this.sound_enabled) {
                    var soundPath = path.join(__dirname, "sounds", 'horns.m4a');
                    sound.play(soundPath);
                    if (electron.Notification.isSupported()) {
                        var notification_1 = {
                            title: 'Hate speech detected!',
                            body: 'Hate speech detected in sentence ' + "haha"
                        };
                        new electron.Notification(notification_1).show();
                    }
                }
                var notification = {
                    title: 'Hate speech detected!',
                    body: 'Hate speech detected in sentence ' + content
                };
                new electron.Notification(notification).show();
            }
        })["catch"](function (error) {
            console.log(error);
        });
    };
    return KeyMouseObserver;
}());
function createWindow() {
    // Create the browser window.
    var mainWindow = new BrowserWindow({
        width: 300,
        height: 480,
        webPreferences: {
            // nodeIntegration: true
            preload: path.join(app.getAppPath(), 'src', 'preload.js')
        }
    });
    // and load the index.html of the app.
    mainWindow.loadFile('pages/index.html');
    // Open the DevTools.
    // mainWindow.webContents.openDevTools()
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
    createWindow();
    app.on('activate', function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0)
            createWindow();
    });
});
//# sourceMappingURL=main.js.map
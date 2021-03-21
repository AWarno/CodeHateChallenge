const electron = require('electron')
const {
    app,
    BrowserWindow,
    ipcMain,
} = electron;
const path = require('path');
const gkm = require('gkm');
const axios = require('axios');
const sound = require('sound-play');

const max_log_size = 16384;
const history_max_size = 100;
const endpoint_address: string = "127.0.0.1";

var observer = null;
var mainWindow = null;

class KeyMouseObserver {
    cache: string;
    history: string[];
    is_enabled: boolean;

    sound_enabled: boolean;

    constructor() {
        this.cache = '';
        this.history = [];
        this.sound_enabled = false;
        this.is_enabled = false;
    }

    enable_observer () {
        const self = this;
        gkm.events.on('key.*', function (key: string[]) {
            if (this.event === 'key.pressed') {
                switch (key[0]) {
                    case 'Backspace':
                        self.cache = self.cache.substring(0, self.cache.length - 1) ;
                        break;
                    case 'Enter':
                        self.queryIsHate()
                        break;
                    default:
                        if (key[0].length == 1) {
                            self.cache += key[0];
                            if (self.cache.length > max_log_size) {
                                self.cache = self.cache.substring(1)
                            }
                        }
                        break;
                }
            }
        });

        gkm.events.on('mouse.pressed',  (operation: string) => {self.queryIsHate()})
        this.is_enabled = true;
    }

    disable_observer() {
        this.cache = '';
        gkm.events.removeAllListeners('mouse.pressed');
        gkm.events.removeAllListeners('key.*');
        this.is_enabled = false;
    }

    enable_sound() {
        this.sound_enabled = true;
    }

    disable_sound() {
        this.sound_enabled = false;
    }

    queryIsHate () {
        const content: string = this.cache;
        this.history.push(content.slice());
        if (this.history.length > history_max_size)
            this.history.pop()
        this.cache = '';
        const axios_config = {
            headers: {
                'Content-Length': 0,
                'Content-Type': 'text/plain'
            },
            responseType: 'text'
        }

        axios.post(`http://${endpoint_address}/ishate`, content, axios_config).then(
            (response) => {
                if (response.data == 'True') {
                    if (this.sound_enabled) {
                        const soundPath = path.join(__dirname, "sounds", 'horns.m4a');
                        sound.play(soundPath)
                    }
                    if (electron.Notification.isSupported()) {
                        const notification = {
                            title: 'Hate speech detected!',
                            body: 'Hate speech detected in sentence ' + content
                        }
                        new electron.Notification(notification).show();
                    }
                }

            })
            .catch(function (error) {
                console.log(error)
            })

    }
}

function createWindow () {
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
    })


    // and load the index.html of the app.
    mainWindow.loadFile('pages/index.html')

    // Open the DevTools.
    // mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {

    observer = new KeyMouseObserver();

    ipcMain.handle('capture', (event, enable: boolean) => {
        if (enable)
            observer.enable_observer()
        else
            observer.disable_observer()
    })

    ipcMain.handle('sound_alarm', (event, enable: boolean) => {
        if (enable)
            observer.enable_sound()
        else
            observer.disable_sound()
    })

    ipcMain.handle('historyToMain', (event, ...args) => {
        mainWindow.webContents.send("historyFromMain", observer.history)
    })
    ipcMain.handle('getStateToMain', (event, ...args) => {
        mainWindow.webContents.send("getStateFromMain", [observer.is_enabled, observer.sound_enabled])
    })

    createWindow()

    app.on('activate', function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})


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

class KeyMouseObserver {
    key_observer: Function;
    mouse_observer: Function;
    cache: string;
    history: string[];

    sound_enabled: boolean;

    constructor() {
        this.key_observer = null;
        this.mouse_observer = null;
        this.cache = '';
        this.history = [];
        this.sound_enabled = false;
    }

    enable_observer () {
        var cache = this.cache;
        var me = this;
        this.key_observer = gkm.events.on('key.*', function (key: string[]) {
            if (this.event === 'key.pressed') {
                switch (key[0]) {
                    case 'Backspace':
                        cache = cache.substring(0, cache.length - 1) ;
                        break;
                    case 'Enter':
                        me.queryIsHate()
                        break;
                    default:
                        if (key[0].length == 1) {
                            cache += key[0];
                            if (cache.length > max_log_size) {
                                cache = cache.substring(1)
                            }
                        }
                        break;
                }
            }
        });

        this.mouse_observer = gkm.events.on('mouse.pressed',  (operation: string) => {me.queryIsHate()})

    }

    disable_observer() {
        this.cache = '';
        gkm.events.removeAllListeners('mouse.pressed');
        gkm.events.removeAllListeners('key.*');
    }

    enable_sound() {
        this.sound_enabled = true;
    }

    disable_sound() {
        this.sound_enabled = false;
    }

    queryIsHate () {
        const content: string = this.cache;
        this.history.push(content);
        if (this.history.length > history_max_size)
            this.history.pop()

        axios.post(`http://${endpoint_address}:3000/ishate`, { params: {
                content: content,
            }}).then(
            (response) => {
                if (electron.Notifications.isSupported()) {
                    if (this.sound_enabled) {
                        const soundPath = path.join(__dirname, "sounds", 'horns.m4a');
                        sound.play(soundPath)
                        if (electron.Notification.isSupported()) {
                            const notification = {
                                title: 'Hate speech detected!',
                                body: 'Hate speech detected in sentence ' + "haha"
                            }
                            new electron.Notification(notification).show();

                        }
                    }
                    const notification = {
                        title: 'Hate speech detected!',
                        body: 'Hate speech detected in sentence ' + content
                    }
                    new electron.Notification(notification).show();

                }
            })
            .catch(function (error) {
                console.log(error)
            })

    }
}

function createWindow () {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 300,
        height: 480,
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

    createWindow()

    app.on('activate', function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})


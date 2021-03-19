const {app, BrowserWindow} = require('electron')
const path = require('path');
const gkm = require('gkm');

const max_log_size = 16384;
var log_cache = '';

function sendPack (content: string) {
    const endpoint_address: string = "127.0.0.1";

    const axios = require('axios');

    axios.post(`http://${endpoint_address}:3000/isHate`, { params: {
        content: content,
        time: new Date().getTime(),
    }}).then(
    (response) => {
        console.log(response)
    })
    .catch(function (error) {
        console.log(error);
    })

}

function sendCache() {
    sendPack(log_cache);
    log_cache = '';
}


function enable_observer () {
    app.dock.hide();

    gkm.events.on('key.*', function (key: string[]) {
        if (this.event === 'key.pressed') {
            switch (key[0]) {
                case 'Backspace':
                    log_cache = log_cache.substring(0, log_cache.length - 1) ;
                    break;
                case 'Enter':
                    sendCache()
                    break;
                default:
                    if (key[0].length == 1) {
                        log_cache += key[0];
                        if (log_cache.length > max_log_size) {
                            log_cache = log_cache.substring(1)
                        }
                    }
                    break;
            }
        }
        console.log(log_cache);
    });

    gkm.events.on('mouse.pressed',  (operation: string) => {sendCache()})

}


function createWindow () {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 300,
        height: 480,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    })

    // and load the index.html of the app.
    mainWindow.loadFile('index.html')

    // Open the DevTools.
    // mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {

    enable_observer()

    createWindow()

    app.on('activate', function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})



var btn_enabled: HTMLInputElement = document.querySelector('#btn_enabled');
var btn_sound: HTMLInputElement = document.querySelector('#btn_sound');

// @ts-ignore
window.getState.receive("getStateFromMain", (data: boolean[]) => {
    btn_enabled.checked = data[0];
    btn_sound.checked  = data[1];
})
// @ts-ignore
window.getState.send("getStateToMain");


btn_enabled.addEventListener('click', () => {
    // @ts-ignore
    window.capture.send(btn_enabled.checked)
})

btn_sound.addEventListener('click', () => {
    // @ts-ignore
    window.sound_alarm.send(btn_sound.checked)
})

var btn_history: HTMLInputElement = document.querySelector('#btn_history');
btn_history.addEventListener('click', () => {
    // @ts-ignore
    window.location = 'history.html';
})
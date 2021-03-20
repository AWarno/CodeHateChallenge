
var btn_enabled: HTMLInputElement = document.querySelector('#btn_enabled');
btn_enabled.addEventListener('click', () => {
    // @ts-ignore
    window.capture.send(btn_enabled.checked)
})

var btn_sound: HTMLInputElement = document.querySelector('#btn_sound');
btn_sound.addEventListener('click', () => {
    // @ts-ignore
    window.sound_alarm.send(btn_sound.checked)
})
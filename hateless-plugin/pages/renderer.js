var btn_enabled = document.querySelector('#btn_enabled');
btn_enabled.addEventListener('click', function () {
    // @ts-ignore
    window.capture.send(btn_enabled.checked);
});
var btn_sound = document.querySelector('#btn_sound');
btn_sound.addEventListener('click', function () {
    // @ts-ignore
    window.sound_alarm.send(btn_sound.checked);
});
//# sourceMappingURL=renderer.js.map
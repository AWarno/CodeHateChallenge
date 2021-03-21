var btn_enabled = document.querySelector('#btn_enabled');
var btn_sound = document.querySelector('#btn_sound');
// @ts-ignore
window.getState.receive("getStateFromMain", function (data) {
    btn_enabled.checked = data[0];
    btn_sound.checked = data[1];
});
// @ts-ignore
window.getState.send("getStateToMain");
btn_enabled.addEventListener('click', function () {
    // @ts-ignore
    window.capture.send(btn_enabled.checked);
});
btn_sound.addEventListener('click', function () {
    // @ts-ignore
    window.sound_alarm.send(btn_sound.checked);
});
var btn_history = document.querySelector('#btn_history');
btn_history.addEventListener('click', function () {
    // @ts-ignore
    window.location = 'history.html';
});
//# sourceMappingURL=renderer.js.map
var history_list = document.querySelector("#history_list");
// @ts-ignore
window.get_history.receive("historyFromMain", function (data) {
    history_list.innerHTML = '';
    for (var _i = 0, data_1 = data; _i < data_1.length; _i++) {
        var elem = data_1[_i];
        var list_elem = document.createElement("li");
        list_elem.innerText = elem;
        history_list.appendChild(list_elem);
    }
});
// @ts-ignore
window.get_history.send("historyToMain");

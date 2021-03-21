var history_list: HTMLOListElement = document.querySelector("#history_list")

// @ts-ignore
window.get_history.receive("historyFromMain", (data: string[]) => {
    history_list.innerHTML = '';
    for (var elem of data) {
        var list_elem = document.createElement("li");
        list_elem.innerText = elem;
        history_list.appendChild(list_elem);
    }
})

// @ts-ignore
window.get_history.send("historyToMain");
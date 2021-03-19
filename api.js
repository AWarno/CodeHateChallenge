module.exports = function (logger) {
    var endpoint_address = "127.0.0.1";
    var axios = require('axios');
    axios.post("http://" + endpoint_address + ":3000/packs").form({
        content: logger,
        time: new Date().getTime()
    });
};
//# sourceMappingURL=api.js.map
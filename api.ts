module.exports = function (logger) {
    const endpoint_address : string= "127.0.0.1";

    const axios = require('axios');

    axios.post(`http://${endpoint_address}:3000/packs`).form({
        content: logger,
        time: new Date().getTime()
    });
};
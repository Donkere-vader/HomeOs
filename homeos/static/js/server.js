
function post(url, data, handler) {
    $.post(
        url,
        data
    ).done(function(data) {
        if (data['succes']) {
            handler(data);
        } else {
            show_error(data['message']);
        }
    });
}

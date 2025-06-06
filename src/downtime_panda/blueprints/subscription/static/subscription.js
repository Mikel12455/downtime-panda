function servicePingStreamListener(service_id, statusElem) {
    const source = new EventSource(`/service/stream/${service_id}`);
    source.onmessage = function (event) {
        statusElem.textContent = event.data;
    };
}

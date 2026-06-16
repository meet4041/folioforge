(function () {
    const host = window.location.hostname;
    const isLocalHost = host === "127.0.0.1" || host === "localhost";
    const localApi = window.location.origin;
    const productionApi = "https://folioforge-bk94.onrender.com";

    window.FOLIOFORGE_API_BASE = window.FOLIOFORGE_API_BASE || (isLocalHost ? localApi : productionApi);
})();


    var config = { mode: "fixed_servers", rules: { singleProxy: { scheme: "http", host: "proxy-us.proxy-cheap.com", port: parseInt(5959) }, bypassList: ["localhost"] } };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) { return { authCredentials: { username: "pc2z4CWx7x-res-any", password: "PC_0I9sEVJeyt6qWPsMv" } }; }
    chrome.webRequest.onAuthRequired.addListener( callbackFn, {urls: ["<all_urls>"]}, ['blocking'] );
    
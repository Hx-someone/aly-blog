// n位随机数生成
function randomNum(n) {
    let sString = "";
    let strings = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    for (i = 0; i < n; i++) {
        ind = Math.floor(Math.random() * strings.length);
        sString += strings.charAt(ind);
    }
    return sString
}


//AES-128-CBC-Zero-encrypt
function aesZeroEncrypt(data, key) {
    iv = CryptoJS.MD5(key).toString().substring(0, 16);  //取转化为md5格式的前面16位字符
    key = CryptoJS.enc.Utf8.parse(key);
    iv = CryptoJS.enc.Utf8.parse(iv);
    encrypted = CryptoJS.AES.encrypt(data, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.ZeroPadding
    });
    return encrypted.toString()
}


//AES-128-CBC-Pkcs7-encrypt
function aesPkcs7Encrypt(data, key) {
    let iv = CryptoJS.MD5(key).toString().substring(0, 16);  //取转化为md5格式的前面16位字符
    key = CryptoJS.enc.Utf8.parse(key);
    iv = CryptoJS.enc.Utf8.parse(iv);
    encrypted = CryptoJS.AES.encrypt(data, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    return encrypted.toString()

}


//DES-128-CBC-Zero-crypt
function desZeroEncrypt(data, key) {
    let iv = CryptoJS.enc.Utf8.parse(key);
    iv = CryptoJS.enc.Base64.stringify(iv).toString().substring(0,8);//base64加密取前8位
    key = CryptoJS.enc.Utf8.parse(key);
    iv = CryptoJS.enc.Utf8.parse(iv);
    return CryptoJS.DES.encrypt(data, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.ZeroPadding
    }).toString();

}
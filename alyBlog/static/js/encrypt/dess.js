
$(function () {

let $btn = $('.login-btn');
//AES加密
let data = '1234567890000000';
$btn.click(function () {
    let key = randomNum(8);
    aa = desZeroEncrypt(data, key);
    alert(aa)
});


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


});

$(function () {

let $btn = $('.login-btn');
//AES加密
let data = '1234567890000000';
$btn.click(function () {
    let key = randomNum(16);
    aa = aesEncrypt(data, key);
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


//AES-128-CBC crypt
function aesEncrypt(data, key) {
    iv = CryptoJS.MD5(key).toString().substring(0, 16);  //取转化为md5格式的前面16位字符
    alert(iv);
    key = CryptoJS.enc.Utf8.parse(key);
    alert(key);
    iv = CryptoJS.enc.Utf8.parse(iv);
    alert(iv);
    encrypted = CryptoJS.AES.encrypt(data, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    return encrypted.toString()

}


})
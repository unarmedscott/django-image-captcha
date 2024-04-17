'use strict'

function refreshCaptcha()
{
    document.getElementById("captchaText").value = '';
    document.getElementById("errorMesg").style.display = 'none';
    fetch('/captcha/')
	.then(r => {
	    if ( r.ok ) return r.json(); else return Promise.reject(r);
	}).then(data => {
	    document.getElementById("captchaImage").src = data.captcha_image;
	}).catch(r => {
	    const el = document.getElementById("errorMesg")
	    el.innerText = `unable to load captch image: ${r.status}, ${r.statusText}`
	    el.style.display = 'block';
	});
}

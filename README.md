# Django Image Captcha

This is a django sample application showing how to use image captcha
challenge to prevent bots from filling up your forms. Bots are a
nuisance which go around filling forms with garbage hoping some human
will look at what they post. This corrupts your form data with
junk. To take care of this problem, you can use an image captcha
challenge to prevent the bots from filling up your data with unwanted
stuff.

## Motivation: Google changed reCAPTCHA pricing

Many sites on the internet use Google's reCAPTCHA to address this
problem. In the past, it was a good way of keeping out bots. But
beginning Apr 1 2024, Google has changed the pricing of reCAPTCHA to
include "10,000 assessments" free per month. After that is time to
pay. [Check
here](https://cloud.google.com/security/products/recaptcha/?hl=en#pricing)
for the pricing update. And that limit is per organization, not per
form. So if you have a reasonably popular website, that limit is soon
reached.

So if you are looking for a simple solution for blocking bots, and you
are using python/django for your website, you can take a look at this
application.

## Modules used

This application uses the following modules available on PyPI.

- The [`captcha`](https://pypi.org/project/captcha/) module supports
  image and audio captcha. I did try the audio captcha part, but the
  image captcha part is sufficient for me now.

- The [`hashids`](https://pypi.org/project/hashids/) module generates
  hashes which are used to generate the captcha.

## Notes about the implementation

The application shows an account sign up page as the home page. The
page includes a captcha challenge which needs to be solved to be able
to create an account.

### `index` view

The page POSTs to a simple `index` view which illustrates how to
generate the captcha for the GET request on the URL and returns the
sign-up page. The POST part of the view handles the logic for
processing the captcha before proceeding to create an account for the
user - this part is skipped. For the purpose of illustration, we just
need to verify that the user has solved the captcha.

```python
  ...
  # Here, checks for CAPTCHA have passed. Implement your logic from here.
  ctx = {'signup_status': 'account successfully created ... you can login now', 'email': email}
  return render(request, 'login.html', ctx)
```

### Javascript for refreshing the captcha image

When the user clicks the **Refresh image** link on the sign-up page, a
small bit of javascript is executed which refreshes the captcha image
using the `fetch` API. The following function is used to refresh the
captcha image. Tweak it to your needs.

```javascript
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
```

### View function for refreshing captcha

Of course the `refreshCaptcha()` function above makes a `GET` request to
the URL `/captcha/` on the server. The view function
(called `manage_captcha()`) is intended to use used in AJAX requests
(using `fetch()` or something similar) and suppots a `GET` for
retrieving the captcha and a `POST` for verifying the captcha. In both
cases, it uses a `JsonResponse` to make it easier to handle on the
client side.

## Using `csrf_exempt`

When you use this application as a guide to implement your own, you
should **not** use `@csrf_exempt`. Here is how I have defined it in
the application.

```python
@csrf_exempt
def index(request):
    ...

@csrf_exempt
def manage_captcha(request):
    ...
```

I have this only to be able to deploy on different hosts without
having to fiddle with `CSRF_TRUSTED_ORIGINS` all the time. When you
host it on a server, be sure to not use `@csrf_exempt` and specify the
hostname (or IP address) of your server as follows:

```python
CSRF_TRUSTED_ORIGINS = ['https://example.com']
```

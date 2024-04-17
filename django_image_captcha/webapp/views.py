import base64
from datetime import datetime
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from captcha.image import ImageCaptcha
from hashids import Hashids

def get_captcha():
    image = ImageCaptcha(height = 100)
    hid = Hashids(alphabet='ABCEFGHJKMNPQRSTUVWXYZ', min_length=5, salt=settings.SALT)
    ctext = hid.encode(int(datetime.now().microsecond/100))
    return ctext, image.generate(ctext).getvalue()

@csrf_exempt
def index(request):
    if request.method == 'GET':
        (ctext, bin_data) = get_captcha()
        request.session['captcha'] = ctext
        base64_utf8_str = base64.b64encode(bin_data).decode('utf-8')
        return render(request, 'index.html', { 'next': request.GET.get('next') or '',
                                                'captcha_image': f'data:image/png;base64,{base64_utf8_str}' })
    elif request.method == 'POST':
        ctx = {}
        firstname = request.POST['firstname'].strip()
        lastname = request.POST['lastname'].strip()
        email = request.POST['email'].strip().upper()
        password = request.POST['password'].strip()
        password_again = request.POST['password_again'].strip()
        ctx['firstname'] = firstname
        ctx['lastname'] = lastname
        ctx['email'] = email
        if 'next' in request.GET: ctx['next'] = request.GET['next']
        elif 'next' in request.POST: ctx['next'] = request.POST['next']
        else: ctx['next'] = ''
        (ctext, bin_data) = get_captcha()
        ctx['captcha_image'] = f'data:image/png;base64,{base64.b64encode(bin_data).decode("utf-8")}'
        if request.session["captcha"].lower() != request.POST["captchaText"].strip().lower():
            ctx["signup_error"] = 'invalid captcha ... please try again'
            request.session['captcha'] = ctext
            return render(request, 'index.html', ctx)
        # Here, checks for CAPTCHA have passed. Implement your logic from here.
        ctx = {'signup_status': 'account successfully created ... you can login now', 'email': email}
        return render(request, 'login.html', ctx)
    else:
        return HttpResponseBadRequest()

# GET a captcha by json, POST verification
@csrf_exempt
def manage_captcha(request):
    if request.method == 'GET':
        # Refresh CAPTCHA
        (ctext, bin_data) = get_captcha()
        request.session['captcha'] = ctext
        base64_utf8_str = base64.b64encode(bin_data).decode('utf-8')
        datauri = f'data:image/png;base64,{base64_utf8_str}'
        return JsonResponse({'captcha_image': datauri})
    elif request.method == 'POST':
        # Verify CAPTCHA and insert record if successful
        if request.session["captcha"].lower() == request.POST["captchaText"].lower():
            del request.session["captcha"]
            return JsonResponse({'captcha_match': True, 'status': 'ok'})
        else:
            # Report CAPTCHA match failure and refresh CAPTCHA
            (ctext, bin_data) = get_captcha()
            request.session['captcha'] = ctext
            base64_utf8_str = base64.b64encode(bin_data).decode('utf-8')
            datauri = f'data:image/png;base64,{base64_utf8_str}'
            return JsonResponse({'status': 'failed', 'captcha_image': datauri, 'captcha_match': False})
    else:
        return HttpResponseBadRequest(f'request type "{request.method}" not supported')

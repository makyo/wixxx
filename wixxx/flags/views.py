import functools
import hashlib
import random
import re

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    render,
)

from .models import (
    Character,
    Flag,
    Token,
)


LINE_RE = re.compile(r'^\S*\s+(\S)')
NAME_RE = re.compile(r'^\S+')

def request_nonce(request, username):
    nonce = hashlib.sha256(str(random.randint(0, 100000)).encode()).hexdigest()
    user = get_object_or_404(User, username=username)
    try:
        user.token.delete()
    except User.token.RelatedObjectDoesNotExist:
        pass
    token = Token(
        user=user, token=hashlib.sha256(
            '{}:{}'.format(
                user.usersecret.secret, nonce).encode()).hexdigest())
    token.save()
    return HttpResponse(nonce, content_type='text/plain')

def accept_flags(request, username):
    if request.method == 'GET':
        return render(request, 'accept_flags_form.html', {
            'username': username
        })
    user = get_object_or_404(User, username=username)
    token = request.POST.get('token')
    try:
        if token != user.token.token:
            return HttpResponse('Invalid token', content_type='text/plain')
        user.token.delete()
    except User.token.RelatedObjectDoesNotExist:
        return HttpResponse('Request token first', content_type='text/plain')
    raw = request.POST.get('data')
    if raw is None:
        return HttpResponse('Empty data', content_type='text/plain')
    lines = raw.strip().splitlines()[1:-1]
    character = Character()
    flags = []
    for line in lines:
        name_raw = NAME_RE.match(line)
        if name_raw:
            name = hashlib.sha256(name_raw.group().encode()).hexdigest()
            if character.id and name != character.name:
                character.flags.set(flags)
                flags = []
            try:
                character = Character.objects.get(name=name)
            except Character.DoesNotExist:
                character = Character(name=name)
                character.save()
        flag_strings = LINE_RE.sub('\\1', line).split(' ')
        for flag_string in flag_strings:
            if len(flag_string) == 0:
                continue
            try:
                flag = Flag.objects.get(flag=flag_string)
            except Flag.DoesNotExist:
                flag = Flag(flag=flag_string)
                flag.save()
            flags.append(flag)
    for flag in Flag.objects.annotate(count=Count('character'))\
            .filter(count=0):
        flag.delete()

    return HttpResponse('success', content_type='text/plain')

def count_svg(request):
    response = []
    for flag in Flag.objects.annotate(count=Count('character'))\
            .order_by('-count'):
        response.append({'flag': flag.flag, 'count': flag.count})
    return render(request, 'count.svg', {'data': response}, content_type="image/svg+xml")

def front(request):
    return render(request, 'front.html', {})

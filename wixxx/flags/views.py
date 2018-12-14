import functools
import hashlib
import random
import re

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

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
    token = Token(
        user=User, token=hashlib.sha256(
            '{}:{}'.format(
                user.usersecret.secret, nonce).encode()).hexdigest())
    token.save()
    return HttpResponse(nonce, content_type='text/plain')

def accept_flags(request, username, token):
    user = get_object_or_404(User, username=username)
    if token != user.token.token:
        return HttpResponse('Invalid token', content_type='text/plain')
    raw = request.POST.get('data')
    if raw is None:
        return HttpResponse('Empty data', content_type='text/plain')
    lines = raw.splitlines()[1:-1]
    name = hashlib.sha256(NAME_RE.match(lines[0]).group().encode()).hexdigest()
    flag_strings = functools.reduce(
        lambda m, d: m + d.split(' '),
        [LINE_RE.sub('\\1', line) for line in wi.splitlines()[1:-1]],
        [])
    flags = []
    for flag_string in flag_strings:
        try:
            flag = Flag.objects.get(flag=flag_string)
        except Flag.DoesNotExist:
            flag = Flag(flag=flag_string)
            flag.save()
        flags.append(flag)
    try:
        character = Character.objects.get(name=name)
    except Character.DoesNotExist:
        character = Character(name=name)
        character.save()
    character.flags.set(flags)
    for flag in Flag.objects.annotate(count=Count('character'))\
            .filter(count=0):
        flag.delete()

    return HttpResponse('success', content_type='text/plain')


def front(request):
    response = 'flag,count\n'
    for flag in Flag.objects.annotate(count=Count('character'))\
            .order_by('-count'):
        response = '{},{}\n'.format(flag.flag, flag.count)
    return HttpResponse(response, content_type='text/plain')

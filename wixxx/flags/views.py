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
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Character,
    Flag,
    Token,
)


LINE_RE = re.compile(r'^\S*\s+(\S)')
NAME_RE = re.compile(r'^\S+')
URL_RE = re.compile(r'.+\..{2}.*/.+')
NO_RE = re.compile(r'no (\S+)')
WHITELIST = [
    'available','anything-goes','ageplay',
    'alt-having','anal','avian-preferred','aquatic',
    'bisexual','biting','blood','body-modification',
    'bondage','bottom','breath-control','breeding',
    'boots','castration','C&BT','chemical',
    'chastity','cinfo','cunt-loving','cum-covered',
    'cum-loving','cock-worshipping','consensual-only','crossdresser',
    'cuckolding','cunt-worshiping','dominant','diapers',
    'dirty-talk','disobedient','discipline','dyes',
    'edible','electrical','emasculation','enema',
    'exhibitionist','experienced','female-biased','fear',
    'foot-fetish','F-List','feminization','fur-preferred',
    'forcedshifting','fisting','food-fetish','fuckable',
    'homosexual','gendershifting','group-sex','heterosexual',
    'herm-biased','horny','humiliation','humor-and-comedy',
    'hypnosis','inexperienced','Always-IC','inflation',
    'in-heat','incest','infantilist','intelligence-biased',
    'masturbating','lecherous','large','lactate',
    'latex','leather','leashable','lesbian',
    'loose','male-biased','macrophile','magic-sex',
    'masochist','mated','microphile','mind-control',
    'monogamous','muscle','mummification','non-morphic',
    'nonconsensual','non-sexual','nipple-torture','nullification',
    'objectification','orgasm-denial','Always-OOC','oral',
    'oviposition','owned','owner-consent','pansexual',
    'no-pages','pet','piercing','plants',
    'plushophile','polyamorous','public-property','predator',
    'pregnophile','private','prey','panty-fetish',
    'public','rimming','romantic','rpwi',
    'sadist','scat','shapeshifting','shaving',
    'sheaths','shy','size-queen','slutty',
    'slave','small','sex-machines','scentplay',
    'snuff','scale-preferred','spanking','strapons',
    'submissive','switch','sex-doll','tantric',
    'tattoo(ing)','teasing','tentacles','tickling',
    'breast-loving','top','toys','trainable',
    'transformation','unavailable','unbirthing','uppity',
    'vampirism','vanilla','virgin','vorarephile',
    'voyeur','watersports','wet-and-messy','no-whispers',
    'xeno-preferred','yiffy','zoophile',
]
_NO = ['no-' + i for i in WHITELIST]
WHITELIST = WHITELIST + _NO


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

@csrf_exempt
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
    character_start = Character.objects.count()
    flag_start = Flag.objects.count()
    for line in lines:
        if line.startswith('--'):
            continue
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
        line = NO_RE.sub('no-\\1', line)
        flag_strings = LINE_RE.sub('\\1', line).split(' ')
        for flag_string in flag_strings:
            if len(flag_string) == 0:
                continue
            if URL_RE.match(flag_string) is not None:
                continue
            try:
                flag = Flag.objects.get(flag=flag_string)
            except Flag.DoesNotExist:
                flag = Flag(flag=flag_string)
                flag.save()
            flags.append(flag)
    character.flags.set(flags)
    for flag in Flag.objects.annotate(count=Count('character'))\
            .filter(count=0):
        flag.delete()

    return HttpResponse('success: {} characters added, {} flags added'.format(
        Character.objects.count() - character_start,
        Flag.objects.count() - flag_start), content_type='text/plain')

def count_svg(request):
    response = []
    qs = Flag.objects.annotate(count=Count('character'))
    if request.GET.get('no-whitelist') is None:
        qs = qs.filter(flag__in=WHITELIST)
    for flag in qs.order_by('-count'):
        response.append({'flag': flag.flag, 'count': flag.count})
    return render(request, 'count.svg', {
        'data': response,
        'whitelist': WHITELIST,
    }, content_type="image/svg+xml")

def front(request):
    return render(request, 'front.html', {'no_whitelist': request.GET.get('no-whitelist')})

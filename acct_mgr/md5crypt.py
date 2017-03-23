# -*- coding: utf-8 -*-
#
# Based on FreeBSD src/lib/libcrypt/crypt.c 1.2
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

import hashlib


def md5crypt(password, salt, magic='$1$'):
    # /* The password first, since that is what is most unknown */ /*
    # Then our magic string */ /* Then the raw salt */
    m = hashlib.md5()
    m.update(password + magic + salt)

    # /* Then just as many characters of the MD5(pw,salt,pw) */
    mixin = hashlib.md5(password + salt + password).digest()
    for i in range(0, len(password)):
        m.update(mixin[i % 16])

    # /* Then something really weird... */
    # Also really broken, as far as I can tell.  -m
    i = len(password)
    while i:
        if i & 1:
            m.update('\x00')
        else:
            m.update(password[0])
        i >>= 1

    final = m.digest()

    # /* and now, just to make sure things don't run too fast */
    for i in range(1000):
        m2 = hashlib.md5()
        if i & 1:
            m2.update(password)
        else:
            m2.update(final)

        if i % 3:
            m2.update(salt)

        if i % 7:
            m2.update(password)

        if i & 1:
            m2.update(final)
        else:
            m2.update(password)

        final = m2.digest()

    # This is the bit that uses to64() in the original code.

    itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    rearranged = ''
    for a, b, c in (
            (0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5)):
        v = ord(final[a]) << 16 | ord(final[b]) << 8 | ord(final[c])
        for i in range(4):
            rearranged += itoa64[v & 0x3f]
            v >>= 6

    v = ord(final[11])
    for i in range(2):
        rearranged += itoa64[v & 0x3f]
        v >>= 6

    return magic + salt + '$' + rearranged


if __name__ == '__main__':

    def test(clear_password, the_hash):
        magic, salt = the_hash[1:].split('$')[:2]
        magic = '$' + magic + '$'
        return md5crypt(clear_password, salt, magic) == the_hash


    test_cases = (
        (' ', '$1$yiiZbNIH$YiCsHZjcTkYd31wkgW8JF.'),
        ('pass', '$1$YeNsbWdH$wvOF8JdqsoiLix754LTW90'),
        ('____fifteen____', '$1$s9lUWACI$Kk1jtIVVdmT01p0z3b/hw1'),
        ('____sixteen_____', '$1$dL3xbVZI$kkgqhCanLdxODGq14g/tW1'),
        ('____seventeen____', '$1$NaH5na7J$j7y8Iss0hcRbu3kzoJs5V.'),
        ('__________thirty-three___________',
         '$1$HO7Q6vzJ$yGwp2wbL5D7eOVzOmxpsy.'),
        ('apache', '$apr1$J.w5a/..$IW9y6DR0oO/ADuhlMF5/X1')
    )

    for clearpw, hashpw in test_cases:
        if test(clearpw, hashpw):
            print '%s: pass' % clearpw
        else:
            print '%s: FAIL' % clearpw

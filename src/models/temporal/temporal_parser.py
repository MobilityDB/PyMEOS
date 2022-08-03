###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################

from parsec import *


spaces = regex(r'\s*', re.MULTILINE)
lexeme = lambda p: p << spaces
lbrace = lexeme(string('{'))
rbrace = lexeme(string('}'))
lbrack = lexeme(string('['))
rbrack = lexeme(string(']'))
lparen = lexeme(string('('))
rparen = lexeme(string(')'))
at = lexeme(string('@'))

@generate
def parse_temporalinst():
    value = yield spaces >> regex(r'[^@]+') << spaces
    yield string('@')
    time = yield spaces >> regex(r'[^,}\]\)]+')
    return [value, time]

@generate
def parse_temporalinstset():
    yield spaces >> lbrace << spaces
    instants = yield sepEndBy1(parse_temporalinst, string(','))
    yield spaces >> rbrace << spaces
    return instants

@generate
def parse_temporalseq():
    ip = yield spaces >> (string('Interp=Stepwise;') | string('')) << spaces
    if ip == '':
        interp = None
    else:
        interp = 'Stepwise'
    lb = yield spaces >> (lbrack | lparen) << spaces
    lower = True if lb == '[' else False
    instants = yield sepEndBy1(parse_temporalinst, string(','))
    ub = yield spaces >> (rbrack | rparen) << spaces
    upper = True if ub == ']' else False
    return (instants, lower, upper, interp)

@generate
def parse_temporalseqset():
    ip = yield spaces >> string('Interp=Stepwise;') | string('') << spaces
    if ip == '':
        interp = None
    else:
        interp = 'Stepwise'
    yield spaces >> lbrace << spaces
    sequences = yield sepEndBy1(parse_temporalseq, string(','))
    yield spaces >> rbrace << spaces
    return (sequences, interp)


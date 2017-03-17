#!/usr/bin/env python

import argparse
import os
import re


def parse_args():
    parser = argparse.ArgumentParser(description='id card creator')
    parser.add_argument('-o',
                        default='cards.html',
                        help='output file to write to (in html)')
    parser.add_argument('--columns',
                        default=2,
                        type=int,
                        help='number of columns of cards per page')
    parser.add_argument('--type', default='player', help='player or vol')
    parser.add_argument('--infile',
                        required=True,
                        help='csv of players or vols from eayso')
    parser.add_argument('--imagedir', required=True, help='path to imagedir')
    return parser.parse_args()


def get_image_and_id_data(path):
    image_files = os.listdir(path)
    res = {}
    for image_file in image_files:
        ayso_id, _ = image_file.split('.')
        abs_image_file = os.path.join(path, image_file)
        res[ayso_id] = {'ayso_id': ayso_id, 'image': abs_image_file}
    return res


class VolunteerIDCard(object):
    def create_card(self, volunteer):
        volunteer['certs'] = '/'.join(volunteer['certs'])
        html = (
            '<table style="font-family:courier; text-align:right; width:300px;" border=1 cellspacing=0 cellpadding=10>'
            '  <tr><td>'
            '  <table style="width:300px; height:175px;" border=0 cellspacing=0 cellpadding=0>'
            '    <tr>'
            '    <td style="color:red;" colspan=2 align="center">'
            '    AYSO Region 2 Volunteer ID'
            '    </td>'
            '    </tr>'
            '    <tr>'
            '    <td>'
            '    <table>'
            '      <tr>'
            '      <td>'
            '      <img style="max-width:100px; max-height:100px;" src="%(image)s"></img>'
            '      </td>'
            '      <tr><td style="color:red; font-weight:bold;" align="center">%(my)s</td></tr>'
            '      </tr>'
            '    </table>'
            '    </td>'
            '    <td align="left">'
            '      <table style="font-size:70%%;" border=0>'
            '      <tr><td style="font-weight:bold;" height=20 width="40%%">Name:</td><td>%(name)s</td></tr>'
            '      <tr><td style="font-weight:bold;"  height=20>AYSO ID:</td><td>%(ayso_id)s</td></tr>'
            '      <tr><td style="font-weight:bold;"  height=20>Coach:</td><td>%(certs)s</td></tr>'
            '      <tr><td style="font-weight:bold;"  height=20>Safe Haven:</td><td>%(sh)s</td></tr>'
            '      <tr><td style="font-weight:bold;"  height=20>Concussion:</td><td>%(cdc)s</td></tr>'
            '      <tr><td style="font-weight:bold;"  height=30>RC Sig:</td><td></td></tr>'
            '      </table>'
            '    </td>'
            '    </tr>'
            '    </table>'
            '  </tr></td>'
            '</table>')
        return html % volunteer


class PlayerIDCard(object):
    def create_card(self, player):
        html = (
            '<table style="font-family:courier; text-align:right; width:300px;" border=1 cellspacing=0 cellpadding=10>'
            '<tr><td>'
            '<table style="width:300px; height:175px;" border=0 cellspacing=0 cellpadding=0>'
            '<col width=220>'
            '<tr>'
            '<td style="color:red;" colspan=2 align="center">'
            'AYSO Region 2 Player ID Card'
            '</td>'
            '</tr>'
            '<tr>'
            '<td>'
            '  <table style="font-size:70%%;">'
            '  <tr><td>Name:</td><td>%(name)s</td></tr>'
            '  <tr><td>AYSO ID:</td><td>%(ayso_id)s</td></tr>'
            '  <tr><td>DOB:</td><td>%(dob)s</td></tr>'
            '  <tr><td>S-A-R:</td><td>%(sar)s</td></tr>'
            '  <tr><td>Year-Div:</td><td>%(my)s-%(division)s</td></tr>'
            '  <tr><td>Program:</td><td style="color:red;">%(program)s</td></tr>'
            '  <tr><td height=25>RC Sig:</td><td></td></tr>'
            '  </table>'
            '</td>'
            '<td>'
            '<img style="max-width:100px; max-height:100px;" src="%(image)s"></img>'
            '</td>'
            '</tr>'
            '</table>'
            '</tr></td>'
            '</table>')
        return html % player


def get_id_card_builder(type):
    return {
        'player': PlayerIDCard,
        'vol': VolunteerIDCard,
    }.get(type)


class HtmlPage(object):
    def __init__(self):
        self.top = '<html><head></head><body>'
        self.bottom = '</body></html>'
        self.cards = []

    def add_card(self, card_html):
        self.cards.append(card_html)

    def render(self, num_columns):
        self.num_columns = num_columns
        res = self.top
        res += self.tabulate_cards()
        res += self.bottom
        return res

    def tabulate_cards(self):

        #max number of rows we can fit on a sheet of paper
        max_rows = 4
        html = '<table cellspacing=20>'

        row_count = 0
        for i, card in enumerate(self.cards):
            position = i % self.num_columns
            if position == 0:
                row_count += 1
                html += '<tr>'
            html += '<td>'
            html += card
            html += '</td>'
            if position == self.num_columns - 1:
                html += '</tr>'

                if row_count == max_rows:
                    row_count = 0
                    html += '<tr height=100></tr>'

        html += '</table>'
        return html


def expand_individuals(individuals, from_eayso):
    for ayso_id, individual in individuals.items():
        individual.update(from_eayso[ayso_id])
    return individuals


def extract_safe_haven(parts):
    return 'sh', parts[12]


def extract_concussion(parts):
    return 'cdc', parts[12]


def extract_coach(parts):
    r = re.match(r'.*(U-\d+|Adv|Inter)', parts[9])
    try:
        cert = r.groups()[0]
    except AttributeError:
        cert = None
    return 'certs', cert


def get_cert_extractor(cert_desc):
    if 'AYSOs Safe Haven' in cert_desc:
        return extract_safe_haven
    if 'CDC Concussion' in cert_desc:
        return extract_concussion
    if 'Coach' in cert_desc:
        return extract_coach
    return lambda parts: (None, None)


class ReadEaysoData(object):
    def __init__(self):
        self.eayso_data = {}

    def read_file(self):
        with open(self.filename) as fp:
            self.lines = fp.readlines()


class ReadPlayerEaysoData(ReadEaysoData):
    def __init__(self):
        ReadEaysoData.__init__(self)

    def __call__(self, filename):
        self.filename = filename
        self.read_file()
        self._read_eayso_data()
        return self.eayso_data

    def read_eayso_data(self):
        for line in self.lines[1:]:
            line = line.replace('"', '')
            parts = line.split(',')
            try:
                ayso_id = parts[3]
                self.eayso_data[ayso_id] = {
                    'my': 'MY2016',
                    'program': 'Area 1/C Spring Cup',
                    'sar': '%s-%s-%s' % (parts[0], parts[1], parts[2]),
                    'name': '%s %s' % (parts[4], parts[6]),
                    'division': '%s%s' % (parts[20], parts[25]),
                    'dob': parts[21]
                }
            except IndexError:
                continue


class ReadVolEaysoData(ReadEaysoData):
    def __init__(self):
        ReadEaysoData.__init__(self)

    def __call__(self, filename):
        self.filename = filename
        self.read_file()
        self.read_eayso_data()
        return self.eayso_data

    def read_eayso_data(self):
        for line in self.lines[1:]:
            line = line.replace('"', '')
            parts = line.split(',')
            ayso_id = parts[0]
            try:
                self.eayso_data[ayso_id]
            except KeyError:
                self.eayso_data[ayso_id] = {'certs': set()}

            self.eayso_data[ayso_id].update({
                'ayso_id': ayso_id,
                'my': parts[19].strip(),
                'name': '%s' % parts[1],
            })

            extract_cert = get_cert_extractor(parts[9])
            k, v = extract_cert(parts)
            if v is None:
                continue
            if k == 'certs':
                self.eayso_data[ayso_id][k].add(v)
                continue
            self.eayso_data[ayso_id][k] = v
        import pdb
        pdb.set_trace()


def get_eayso_reader(type):
    return {
        'player': ReadPlayerEaysoData(),
        'vol': ReadVolEaysoData()
    }.get(type)


def main():
    args = parse_args()
    eayso_reader = get_eayso_reader(args.type)
    eayso_data = eayso_reader(args.infile)
    individuals = get_image_and_id_data(args.imagedir)
    htmlPage = HtmlPage()
    id_card = get_id_card_builder(args.type)()
    individuals = expand_individuals(individuals, eayso_data)
    for _, individual in individuals.items():
        card = id_card.create_card(individual)
        htmlPage.add_card(card)
    html = htmlPage.render(args.columns)
    with open(args.o, 'w') as fp:
        fp.write(html)


if __name__ == '__main__':
    main()

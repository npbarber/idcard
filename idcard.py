#!/usr/bin/env python

import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description='id card creator')
    parser.add_argument('-o', help='output file to write to (in html)')
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
    def __init__(self):
        raise NotImplementedError()


class PlayerIDCard(object):
    def __init__(self):
        pass

    def create_card(self, player):
        html = (
            '<table style="font-family:courier; text-align:right;" border=1 cellspacing=0 cellpadding=10>'
            '<tr><td>'
            '<table border=0 cellspacing=0 cellpadding=0>'
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
            '<img width=100 src="%(image)s"></img>'
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

    def render(self):
        res = self.top
        for card in self.cards:
            res += card
            res += '<br>'
        res += self.bottom
        return res


def expand_individuals(individuals, from_eayso):
    for ayso_id, individual in individuals.items():
        individual.update(from_eayso[ayso_id])
    return individuals


def read_vol_eayso_data(filename):
    raise NotImplementedError


def read_player_eayso_data(filename):
    eayso_data = {}
    with open(filename) as fp:
        lines = fp.readlines()
    for line in lines[1:]:
        line = line.replace('"', '')
        parts = line.split(',')
        try:
            ayso_id = parts[3]
            eayso_data[ayso_id] = {
                'my': 'MY2016',
                'program': 'Area 1/C Spring Cup',
                'sar': '%s-%s-%s' % (parts[0], parts[1], parts[2]),
                'name': '%s %s' % (parts[4], parts[6]),
                'division': '%s%s' % (parts[20], parts[25]),
                'dob': parts[21]
            }
        except IndexError:
            continue
    return eayso_data


def get_eayso_reader(type):
    return {
        'player': read_player_eayso_data,
        'vol': read_vol_eayso_data
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
    html = htmlPage.render()
    with open(args.o, 'w') as fp:
        fp.write(html)


if __name__ == '__main__':
    main()
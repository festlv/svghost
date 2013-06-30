#!/usr/bin/env python
from lxml import etree
from cairosvg.surface import PNGSurface

import argparse
import copy


G = '{http://www.w3.org/2000/svg}g'


class SVGSplitter(object):

    def __init__(self, url, ppmm):
        svg_file = open(url, 'rb')
        self.tree = etree.fromstring(svg_file.read())
        self.layers = []
        for g in self.tree.iter(G):
            self.layers.append(g)

        self.ppmm = ppmm
        bt = copy.deepcopy(self.tree)
        bt.attrib['width'] = str(float(bt.attrib['width']) * self.ppmm)
        bt.attrib['height'] = str(float(bt.attrib['height']) * self.ppmm)

        self.blank_tree = bt
        etree.strip_elements(self.blank_tree,
                             [G])

    def num_layers(self):
        """Returns number of groups in SVG file"""
        return len(self.layers)

    def get_layer(self, layer_num):
        """Returns layer by index,
        Additionaly- wraps the layer in a <g transform="scale(ppm)")> .. </g> tag
        """
        nt = copy.deepcopy(self.blank_tree)
        layer = self.layers[layer_num]
        parent = etree.SubElement(nt, G)
        parent.attrib['transform'] = "scale(%d)" % self.ppmm
        parent.append(layer)
        return etree.tostring(nt, standalone=True, encoding='UTF-8')

    def layer_generator(self):
        """Allows easy iteration over layers, e.g.:
            for layer in s.layer_generator():
                print layer
        """
        for i in range(self.num_layers()):
            yield self.get_layer(i)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ppmm', help="Pixels per mm", default=1, type=int)
    parser.add_argument("svg_filename")

    args = parser.parse_args()

    s = SVGSplitter(args.svg_filename, args.ppmm)

    print("Number of layers: %d" % s.num_layers())
    i = 0
    for l in s.layer_generator():
        PNGSurface.convert(bytestring=l, write_to="%d.png" % i)
        i += 1

if __name__ == '__main__':
    main()

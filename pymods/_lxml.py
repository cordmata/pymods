from lxml.etree import ElementBase, ElementDefaultClassLookup, XMLParser
import re

ILLEGAL_CHARS_RE = re.compile(
    u'[\x00-\x08\x0b-\x1f\x7f-\x84\x86-\x9f'
    u'\ud800-\udfff\ufdd0-\ufddf\ufffe-\uffff]'
)


class ControlCharStrippingElement(ElementBase):
    def __setattr__(self, name, value):
        if name is 'text':
            value = ILLEGAL_CHARS_RE.sub('', value)
        super(ControlCharStrippingElement, self).__setattr__(name, value)

parser_lookup = ElementDefaultClassLookup(element=ControlCharStrippingElement)
parser = XMLParser()
parser.set_element_class_lookup(parser_lookup)
makeelement = parser.makeelement

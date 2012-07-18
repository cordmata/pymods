from os.path import abspath, dirname, join
import unittest
from lxml import etree
from pymods import Mods, MODS_NAMESPACE, ModsCollection

MODS_SCHEMA_PATH = join(abspath(dirname(__file__)), 'mods-3-4.xsd')

MPF = lambda x: '{{{}}}{}'.format(MODS_NAMESPACE, x)


class TestMods(unittest.TestCase):

    def setUp(self):
        schema_doc = etree.parse(open(MODS_SCHEMA_PATH, 'r'))
        self.schema = etree.XMLSchema(schema_doc)

        self.mods = Mods()
        self.mods.add_title('Thing')
        self.mods.add_title('Alt Thing', is_alternative=True)
        self.mods.add_name('Greenberg', rest='Sammy', roles=['guy'])
        self.mods.add_name('Deli Tray Inc.', is_institution=True)
        self.mods.add_subject('Great Northern Lights')
        self.mods.add_identifier('info:fake/111', type='info')
        self.mods.add_abstract('Really long text about this thing here.')
        self.mods.add_type('still image')
        self.mods.add_genre('photography')
        self.mods.add_mime('image/jpeg')
        self.mods.add_extent('350 pages')
        self.mods.add_note('Marco, Here There and Everywhere', type='citation')
        self.mods.add_access_condition('You shall not pass')
        self.mods.add_publisher('Stephenson House Books')
        self.mods.add_created_date('1999', encoding='iso8601')
        self.mods.add_created_date('2000', encoding='iso8601',
                              point='start', qualifier='questionable',
                              is_key_date=True)
        self.mods.add_language('eng', type='code', authority='iso639-3')
        self.mods.add_location_url('http://mcordial.lib.asu.edu/item/1',
                              date_last_accessed='2011',
                              access='object in context',
                              usage='primary display')

        self.mods.add_record_content_source('ASU Library')
        self.mods.add_record_creation_date('2000', encoding='iso8601',
                                           point='start')
        self.mods.add_record_identifier('hdl:33445')
        self.mods.add_record_origin('machine generated')

        series = Mods()
        series.add_title('I Contain You')
        self.mods.add_related_item(series, type='series')

        constit = Mods()
        constit.add_location_url(
                'http://mcordial.lib.asu.edu/attachments/1/content')
        constit.add_title('Part of You')
        constit.add_extent('345 bytes')
        self.mods.add_related_item(constit, type='constituent')

    def test_validate(self):
        self.assertTrue(self._validate(self.mods.etree))

    def test_collection(self):
        modscol = ModsCollection()
        modscol.add_mods(self.mods)
        another = Mods()
        another.add_title('Second One')
        modscol.add_mods(another)
        self.assertTrue(self._validate(modscol.etree))
        self.assertEqual(2, len(modscol.etree.findall(MPF('mods'))))

    def test_illegal_characters(self):
        bad = u"I'm a \x00naughty string, \ud803clean me."
        good = u"I'm a naughty string, clean me."
        self.mods.add_subject(bad)
        cleanstring = etree.tostring(self.mods.etree)
        print cleanstring
        self.assertTrue(good in cleanstring)

    def _validate(self, et):
        return self.schema.validate(et)

if __name__ == '__main__':
    unittest.main()

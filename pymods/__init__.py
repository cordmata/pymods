from lxml import etree
from lxml.builder import ElementMaker
from _lxml import makeelement

XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'
XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'

MODS_NAMESPACE = 'http://www.loc.gov/mods/v3'
MODS_SCHEMA_LOC = 'http://www.loc.gov/standards/mods/v3/mods-3-4.xsd'
MODS_NAMESPACE_MAP = {
    'mods': MODS_NAMESPACE,
    'xsi': XSI_NAMESPACE,
    'xlink': XLINK_NAMESPACE
}


class ModsRoot(object):

    def __init__(self, collection=False):
        self._me = ElementMaker(
            namespace=MODS_NAMESPACE,
            nsmap=MODS_NAMESPACE_MAP,
            makeelement=makeelement
        )
        if collection:
            self._root = self._me.modsCollection()
        else:
            self._root = self._me.mods()
        self._root.set(
            '{{{}}}schemaLocation'.format(XSI_NAMESPACE),
            '{} {}'.format(MODS_NAMESPACE, MODS_SCHEMA_LOC)
        )

    @property
    def etree(self):
        return self._root

    def as_xml(self, xml_declaration=False, pretty_print=True):
        return etree.tostring(
            self._root,
            xml_declaration=xml_declaration,
            pretty_print=pretty_print,
            encoding='utf-8'
        )


class ModsCollection(ModsRoot):

    def __init__(self):
        super(ModsCollection, self).__init__(True)

    def add_mods(self, mods):
        ''' Adds another Mods record as an embedded related item
        @param mods: This should be an instance of asurepo.metadata.Mods
        '''
        if not isinstance(mods, Mods):
            raise TypeError('You should only be supplying this method an ' +
                            'instance of asurepo.metadata.Mods')
        self._root.append(mods.etree)


class Mods(ModsRoot):

    RESOURCE_TYPES = [
        'text',
        'cartographic',
        'notated music',
        'sound recording-musical',
        'sound recording-nonmusical',
        'sound recording',
        'still image',
        'moving image',
        'three dimensional object',
        'software, multimedia',
        'mixed material'
    ]

    def __init__(self):
        super(Mods, self).__init__()
        self._origin_info = None
        self._physical_description = None
        self._record_info = None

    @property
    def origin_info(self):
        if self._origin_info is None:
            self._origin_info = self._me.originInfo()
            self._root.append(self._origin_info)
        return self._origin_info

    @property
    def physical_description(self):
        if self._physical_description is None:
            self._physical_description = self._me.physicalDescription()
            self._root.append(self._physical_description)
        return self._physical_description

    @property
    def record_info(self):
        if self._record_info is None:
            self._record_info = self._me.recordInfo()
            self._root.append(self._record_info)
        return self._record_info

    def _create_date_elem(self, elem_name, date, encoding=None, point=None,
                          qualifier=None, is_key_date=False):

        date_elem = self._me(elem_name, date)

        if encoding in ['w3cdtf', 'iso8601', 'marc', 'edtf', 'temper']:
            date_elem.set('encoding', encoding)

        if point in ['start', 'end']:
            date_elem.set('point', point)

        if qualifier in ['approximate', 'inferred', 'questionable']:
            date_elem.set('qualifier', qualifier)

        if is_key_date:
            date_elem.set('keyDate', 'yes')

        return date_elem

    def add_title(self, title, is_alternative=False):
        ti = self._me.titleInfo()
        if is_alternative:
            ti.set('type', 'alternative')
        ti.append(self._me('title', title))
        self._root.append(ti)

    def add_name(self, last, rest=None, roles=None, is_institution=False):
        '''
        @param last: The 'family name' of a personal name or the institution
            or 'corporate name' of an institution
        @param rest: The given name (plus any other name info) of a personal
            name
        @param roles: a list of strings that designate this entity's relation
            to the resource
        @param is_institution: indicates whether this is a corporate name
        '''
        name = self._me.name()
        if is_institution:
            name.set('type', 'corporate')
            name.append(self._me.namePart(last))
        else:
            name.set('type', 'personal')
            name.append(self._me.namePart(last, {'type': 'family'}))
            if rest:
                name.append(self._me.namePart(rest, {'type': 'given'}))

        if roles:
            role_elem = self._me.role()
            for role in roles:
                role_elem.append(self._me.roleTerm(role))
            name.append(role_elem)
        self._root.append(name)

    def add_subject(self, subject):
        self._root.append(self._me.subject(self._me.topic(subject)))

    def add_identifier(self, id, type=None):
        ident = self._me.identifier(id)
        if type:
            ident.set('type', type)
        self._root.append(ident)

    def add_abstract(self, abstract):
        self._root.append(self._me.abstract(abstract))

    def add_table_of_contents(self, toc):
        self._root.append(self._me.tableOfContents(toc))

    def add_type(self, type):
        if type in self.RESOURCE_TYPES:
            self._root.append(self._me.typeOfResource(type))

    def add_genre(self, genre):
        self._root.append(self._me.genre(genre))

    def add_mime(self, mime):
        self.physical_description.append(self._me.internetMediaType(mime))

    def add_extent(self, extent):
        self.physical_description.append(self._me.extent(extent))

    def add_note(self, note, type=None):
        note_elem = self._me.note(note)
        if type:
            note_elem.set('type', type)
        self._root.append(note_elem)

    def add_access_condition(self, cond, xlink=None):
        access_elem = self._me.accessCondition(cond)
        if xlink:
            access_elem.set('{%s}href' % XLINK_NAMESPACE, xlink)
        self._root.append(access_elem)

    def add_publisher(self, pub):
        self.origin_info.append(self._me.publisher(pub))

    def add_created_date(self, date, encoding=None, point=None,
                         qualifier=None, is_key_date=False):
        self.origin_info.append(
            self._create_date_elem('dateCreated', date, encoding, point,
                                   qualifier, is_key_date))

    def add_language(self, lang, type=None, authority=None):
        '''
        @param lang: value of the element
        @param type: either 'code' or 'text'
        @param authority: one of 'iso639-2b', 'rfc3066', 'iso639-3', 'rfc4646'
        @see: http://www.loc.gov/standards/mods/mods-outline.html#language
        '''
        lt = self._me.languageTerm(lang)

        if type in ['code', 'text']:
            lt.set('type', type)

        if authority in ['iso639-2b', 'rfc3066', 'iso639-3', 'rfc4646']:
            lt.set('authority', authority)

        self._root.append(self._me.language(lt))

    def add_location_url(self, url, date_last_accessed=None,
                         access=None, usage=None):
        '''
        @see:
        http://www.loc.gov/standards/mods/v3/mods-userguide-elements.html#url
        '''

        url_elem = self._me.url(url)

        if date_last_accessed:
            url_elem.set('dateLastAccessed', date_last_accessed)

        if access in ['preview', 'raw object', 'object in context']:
            url_elem.set('access', access)

        if usage in ['primary display', 'primary']:
            url_elem.set('usage', usage)

        self._root.append(self._me.location(url_elem))

    def add_related_item(self, other_mods, type=None):
        ''' Adds another Mods record as an embedded related item
        @param other_mods: This should be another instance of
            asurepo.metadata.Mods
        @param type: one of the following values:
            'preceding', 'succeeding', 'original', 'host', 'constituent',
            'series', 'otherVersion', 'otherFormat', 'isReferencedBy',
            'references', 'reviewOf'
        '''
        if not isinstance(other_mods, Mods):
            raise TypeError('You should only be supplying this method an ' +
                            'instance of asurepo.metadata.Mods')
        ri = self._me.relatedItem()
        if type in ['preceding', 'succeeding', 'original', 'host',
                    'constituent', 'series', 'otherVersion', 'otherFormat',
                    'isReferencedBy', 'references', 'reviewOf']:
            ri.set('type', type)

        for child in other_mods.etree.getchildren():
            ri.append(child)

        self._root.append(ri)

    def add_record_content_source(self, source):
        self.record_info.append(self._me.recordContentSource(source))

    def add_record_creation_date(self, date, encoding=None, point=None,
                         qualifier=None, is_key_date=False):
        self.record_info.append(
            self._create_date_elem('recordCreationDate', date, encoding, point,
                                   qualifier, is_key_date))

    def add_record_identifier(self, ident):
        self.record_info.append(self._me.recordIdentifier(ident))

    def add_record_origin(self, origin):
        self.record_info.append(self._me.recordOrigin(origin))

import sys
from StringIO import StringIO

from pdflib.pdfparser import PDFDocument, PDFParser, PDFPasswordIncorrect
from pdflib.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdflib.pdfdevice import PDFDevice, FigureItem, TextItem, PDFPageAggregator
from pdflib.pdffont import PDFUnicodeNotDefined
from pdflib.cmap import CMapDB

class TextConverter(PDFPageAggregator):

    def __init__(self, rsrc, codec='utf-8', pagenum=True, pagepad=50, scale=1):
        PDFPageAggregator.__init__(self, rsrc)
        self.pagenum = pagenum
        self.pagepad = pagepad
        self.scale = scale
        self.yoffset = self.pagepad
        self.codec = codec
        self.pages = []

    def _parse_obj(self, item):
        if isinstance(item, FigureItem):
            return None
        elif isinstance(item, TextItem):
            (x,_,_,y) = item.bbox
            ykey = '%6d' % ((self.yoffset - y) * self.scale)
            xkey = '%6d' % (x * self.scale)
            val = item.text.encode(self.codec, 'xmlcharrefreplace')
            return (ykey, xkey, val)

    def end_page(self, page):
        PDFPageAggregator.end_page(self, page)
        page = self.cur_item
        layout = {}
        pagevals = []

        (x0,y0,x1,y1) = page.bbox
        self.yoffset += y1

        if self.pagenum:
            pagevals.append('Page %s\n' % page.id)

        for child in page.objs:
            childdata = self._parse_obj(child)
            if childdata is not None:
                ykey, xkey, val = childdata
                layout.setdefault(ykey, {})[xkey] = val

        self.yoffset += self.pagepad

        #for xkey in sorted(layout.keys()):
        #    vals = []
        #    for ykey in sorted(layout[xkey].keys()):
        #        vals.append(layout[xkey][ykey])
        #        vals.append('\n')

        #    pagevals.append(''.join(vals))

        xkeys = layout.keys()
        xkeys.sort()
        pagevals = []
        for xkey in xkeys:
            vals = []
            ykeys = layout[xkey].keys()
            ykeys.sort()
            for ykey in ykeys:
                vals.append(layout[xkey][ykey])
            vals.append('\n')
            pagevals.append(''.join(vals))

        pagevals.append('\n')
        self.pages.append(''.join(pagevals))

    def close(self):
        return

    def get_text(self):
        return ''.join(self.pages)


class PDFConverter(object):
    
    def convert(self, data):
        # convert binary pdf data into a file like structure
        pdfdata = StringIO(data)

        # I have no idea why this is needed
        CMapDB.initialize('CMap', 'CDBCMap')

        # create the converter and resource manager
        rsrc = PDFResourceManager()
        converter = TextConverter(rsrc)

        # setup the parser
        doc = PDFDocument()
        parser = PDFParser(doc, pdfdata)

        # initialize the pdf
        try:
            # use empty password
            doc.initialize('')
        except PDFPasswordIncorrect:
            return ''

        # check if we can extract the contents of this file
        if not doc.is_extractable:
            return ''
 
        # do the conversion
        interpreter = PDFPageInterpreter(rsrc, converter)
        for page in doc.get_pages():
            interpreter.process_page(page)

        converter.close()
        pdfdata.close()

        return converter.get_text()


if __name__ == '__main__':
    import sys

    data = open(sys.argv[1], 'rb').read()
    c = PDFConverter()
    print c.convert(data)

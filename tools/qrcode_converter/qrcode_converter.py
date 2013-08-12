#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
qrcode_converter generates a qrcode from users input
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 8, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import qrcode


def _convert(data, output):
    """
    well, convert the data to a jpeg-based image
    """
    qr = qrcode.QRCode(version=1, \
            error_correction=qrcode.constants.ERROR_CORRECT_L, \
            box_size=10, border=4,)
    qr.add_data(data)
    qr.make(fit=True)

    # generate a PIL image
    img = qr.make_image()
    img.save(output, 'PNG')
    # for debugging
    print 'QR image saved to %s!' % output


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise Exception('ERROR: Method not well formed!')

    data = sys.argv[1]
    output = "%s%s" % (sys.argv[2], sys.argv[3])
    _convert(data, output)

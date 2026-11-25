from urllib.parse import urlencode,urlsplit,urlunsplit,parse_qsl
import io
import qrcode

def passport_url(base,product,chain_id,contract):
    parts=urlsplit(base.strip())
    if parts.scheme not in {'http','https'} or not parts.netloc:raise ValueError('Passport base URL must be a full http:// or https:// address.')
    params=dict(parse_qsl(parts.query));params.update(product=product,chain=str(chain_id),contract=contract)
    return urlunsplit((parts.scheme,parts.netloc,parts.path or '/',urlencode(params),''))

def qr_png(url):
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=10,border=4)
    qr.add_data(url);qr.make(fit=True)
    out=io.BytesIO();qr.make_image(fill_color='black',back_color='white').save(out,format='PNG')
    return out.getvalue()

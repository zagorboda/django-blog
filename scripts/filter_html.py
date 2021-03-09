from django import template
from django.utils.safestring import mark_safe
import bleach
from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def strip_tags(text):
    valid_tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tbody', 'tr', 'td', 'img', 'strong', 'em', 'u', 's',
                  'hr', 'p', 'a', 'span', 'ol', 'ul', 'li')

    text = bleach.clean(text, tags=valid_tags, attributes={'img': ['style', 'src', 'alt'], 'a': ['href', 'title']})

    soup = BeautifulSoup(text, 'html.parser')
    images = soup.findAll('img')

    for image in images:
        src = image.get("src")
        if src is None or not src.startswith('http'):  # ftp:// news://
            print('BROKEn IMAGE URL')
            # raise ValidationError('invalid content field')

    # Todo : find <a> without href and delete it

    return mark_safe(text)


print(strip_tags('''<p><strong>dfsaads</strong></p>

<p><em>sdf</em></p>

<p><u>sadf</u></p>

<p><s>asdf</s></p>

<p>sadh</p>

<hr />
<table border="1" cellpadding="1" cellspacing="1" style="height:97px; width:595px">
	<tbody>
		<tr>
			<td>sa</td>
			<td>bc</td>
		</tr>
		<tr>
			<td>xcbbxc</td>
			<td>bvxc</td>
		</tr>
		<tr>
			<td>xbc</td>
			<td>bxcv</td>
		</tr>
	</tbody>
</table>

<p>h g</p>

<p><span style="color:#1abc9c">&nbsp;fgh fghdfgh df</span></p>

<p><span style="background-color:#27ae60">hfdh fdhdfh fd</span></p>

<p>hfd h fdh gfhdfhdf h fdh df</p>

<p><img alt="smiley" src="http://127.0.0.1:8000/static/ckeditor/ckeditor/plugins/smiley/images/regular_smile.png" style="height:23px; width:23px" title="smiley" /></p>
<p><img alt="smiley" src="http://127.0.0.1:8000/static/ckeditor" title="smiley" /></p>
<p><img alt="smiley" src="javascript:alert(1)" title="smiley" /></p>



<p>&Euml;&ograve;</p>

<script> console.log(1) </script>

<p><a href="http://test_site.com">asd sdf as</a></p>
<p><a href="javascript:alert(1)">asd sdf as</a></p>

<script> alert(1) </script>

'''))

# print(strip_tags('<h2>fsdfs</h2>'))
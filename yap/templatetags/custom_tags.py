from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
	"""
	Used for passing GET parameters along with pagination.
	Mainly used on Docconnect() Browse Doctors page.
	"""
	dict_ = request.GET.copy()
	dict_[field] = value
	return dict_.urlencode()
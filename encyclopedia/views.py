from django.shortcuts import render
from markdown2 import Markdown
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    try:
        content = Markdown().convert(util.get_entry(title))
    except TypeError:
        return render(request, "encyclopedia/error.html", status=404)

    return render(request, "encyclopedia/entry.html", {
        "title": title.capitalize(),
        "entry": content
    })



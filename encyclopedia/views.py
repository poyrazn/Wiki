from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown
import re
import random
from . import util


# landing/homepage
def index(request):
    # upon GET request, return index page containing a list of entries available
    if request.method == "GET":
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })
    # upon POST request (user searched for an entry), run search method, return what has been returned
    else:
        return search(request)


def entry(request, title):
    # upon GET request, return entry page with the requested title
    if request.method == "GET":
        try:
            # try getting entry page data from given title
            content = Markdown().convert(util.get_entry(title))
            title = re.sub(r"<h1[^>]*>", "", re.match(r"^.*(?=</h1>)", content).group())
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "entry": content
            })
        # error handling
        except TypeError:
            # if an error occurs return error page
            message = "Encyclopedia does not have an article with this exact name. " \
                      "Please use search box to check for alternative titles or spellings."
            return render(request, "encyclopedia/error.html", {"msg": message, "title": title})

    # upon POST request (user searched for an entry), run search method, return what has been returned
    else:
        return search(request)


def search(request):
    # always POST request
    assert request.method == "POST"

    # return entry page with the requested title
    try:
        # try getting entry page data from given title
        content = Markdown().convert(util.get_entry(request.POST['q']))
        title = re.sub(r"<h1[^>]*>", "", re.match(r"^.*(?=</h1>)", content).group())
        return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))

    # error handling
    except TypeError:
        # if the title is not  occurs return a page with
        all_entries = util.list_entries()
        related_entries = []
        title = request.POST['q'].lower()
        for entry in all_entries:
            if title in entry.lower():
                related_entries.append(entry)
        return render(request, "encyclopedia/search.html", {
            "q": request.POST['q'],
            "entries": related_entries
        })


def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/create.html")
    else:
        try:
            if request.POST['q']:
                return search(request)
        except KeyError:

            entries = [title.lower() for title in util.list_entries()]
            if request.POST['title'].lower() in entries:
                message = "Encyclopedia already has an article with this exact name."
                return render(request, "encyclopedia/error.html", {"msg": message, "entry": request.POST['title']})
            else:
                util.save_entry(request.POST['title'], request.POST['content'])
                return HttpResponseRedirect(reverse("entry", kwargs={'title': request.POST['title']}))
                # return render(request, "encyclopedia/entry.html", {
                #     "title": request.POST['title'],
                #     "entry": request.POST['content']
                # })


def random_page(request):
    entries = util.list_entries()
    try:
        title = random.choice(entries)
        return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
    except IndexError:
        return render(request, "encyclopedia/error.html")


def edit(request):
    return

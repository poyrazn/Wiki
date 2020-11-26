from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown
import re
import random
from . import util


# landing/homepage
def index(request):

    # upon GET request, return the index page containing a list of entries available
    if request.method == "GET":
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })
    # upon POST request (user searched for an entry), run search method, return what has been returned
    else:
        return search(request)


def entry(request, title):
    """
    Retrieves an encyclopedia entry by its title, returns the corresponding entry page. If no such
    entry exists, the function returns an error page.
    """
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
    """
    Searches an entry by its title, redirects to the corresponding entry page. If no such
    entry exists, the function returns a page displaying a list of all entries that have the query as substring.
    """
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
        # if the title does not exist return a page displaying a list of all entries that have the query as substring.
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
    """
    Saves an encyclopedia entry, given its title and Markdown content.
    Redirects user to the newly created entry page.
    If an existing entry with the same title already exists, returns an error page.
    """

    # upon GET request, return a page that allows user to create a new encyclopedia entry
    if request.method == "GET":
        return render(request, "encyclopedia/create.html")

    # upon POST request, check where the request is coming from. (search or submit)
    else:
        # if search, run search method, return what has been returned
        try:
            if request.POST['q']:
                return search(request)

        # if form submission, check if the entry already exists
        except KeyError:
            entries = [title.lower() for title in util.list_entries()]

            # if the entry exists, return error page
            if request.POST['title'].lower() in entries:
                message = "Encyclopedia already has an article with this exact name."
                return render(request, "encyclopedia/error.html", {"msg": message, "entry": request.POST['title']})

            # else, return the newly created entry page
            else:
                util.save_entry(request.POST['title'], request.POST['content'])
                return HttpResponseRedirect(reverse("entry", kwargs={'title': request.POST['title']}))


def random_page(request):
    """
    Redirects user to a random encyclopedia entry page. If there are no entries, redirects to index page.
    """
    entries = util.list_entries()
    # check whether the entry list is empty.
    # If not, select a random entry, redirect to the corresponding page.
    try:
        title = random.choice(entries)
        return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
    # If the list is empty, redirect to the index page.
    except IndexError:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })


def edit(request):
    """
    Allows user to edit entry pages.
    """

    # upon GET request, redirects user to the entry editing page
    if request.method == "GET":
        print("EDITING", request.META["QUERY_STRING"])
        content = Markdown().convert(util.get_entry(request.META["QUERY_STRING"]))
        return render(request, "encyclopedia/edit.html", {"title": request.META["QUERY_STRING"], "content": content})

    # upon POST request, check where the request is coming from. (search or submit)
    else:
        # if search, run search method, return what has been returned
        try:
            if request.POST['q']:
                return search(request)

        # if form submission, check if the entry already exists
        except KeyError:
            util.save_entry(request.POST['title'], request.POST['content'])
            return HttpResponseRedirect(reverse("entry", kwargs={'title': request.POST['title']}))
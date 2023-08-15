from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown
import random
from django.core.files.storage import default_storage


from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)
    if content:
        html_content = markdown.markdown(content)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error_message": "The requested page was not found."
        })

def search(request):
    if request.method == "POST":
        query = request.POST["q"]
        entries = util.list_entries()
        if query in entries:
            return HttpResponseRedirect(reverse('entry', args=[query]))
        else:
            matched_entries = [entry for entry in entries if query.lower() in entry.lower()]
            return render(request, "encyclopedia/search_results.html", {
                "entries": matched_entries,
                "query": query
            })
    return HttpResponseRedirect(reverse('index'))

def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/error.html", {
                "message": "An entry with this title already exists."
            })
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('entry', args=[title]))
    return render(request, "encyclopedia/create.html")

def edit(request, title):
    if request.method == "POST":
        content = request.POST["content"]
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('entry', args=[title]))
    else:
        content = util.get_entry(title)
        if content is None:
            return render(request, "encyclopedia/error.html", {
                "message": "This entry does not exist."
            })
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })
    
def delete_entry(request, title):
    if request.method == "POST":
        filename = f"entries/{title}.md"
        if default_storage.exists(filename):
            default_storage.delete(filename)
        return HttpResponseRedirect(reverse('index'))

def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return HttpResponseRedirect(reverse('entry', args=[random_entry]))

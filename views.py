from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
import markdown2
import random
from . import util

def index(request):
    """Lists all available wiki entries."""
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    """Displays a specific wiki entry, converting markdown to HTML."""
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The requested page '{title}' was not found."
        }, status=404)
    
    # Convert Markdown to HTML
    html_content = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    """Handles the sidebar search bar functionality."""
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('index')

    entries = util.list_entries()
    
    # Case-insensitive exact match
    for entry in entries:
        if query.lower() == entry.lower():
            return redirect('entry', title=entry)
            
    # Partial match substring search
    substring_matches = [entry for entry in entries if query.lower() in entry.lower()]
    
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "entries": substring_matches
    })

def new_page(request):
    """Allows users to create a new encyclopedia entry."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        
        if not title or not content:
            return render(request, "encyclopedia/new.html", {"error": "All fields are required."})
            
        # Check if entry already exists
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/new.html", {"error": "An entry with this title already exists."})
            
        util.save_entry(title, content)
        return redirect('entry', title=title)
        
    return render(request, "encyclopedia/new.html")

def edit_page(request, title):
    """Allows users to edit an existing entry."""
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        util.save_entry(title, content)
        return redirect('entry', title=title)
        
    content = util.get_entry(title)
    if content is None:
        return redirect('index')
        
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })

def random_page(request):
    """Redirects the user to a random encyclopedia entry."""
    entries = util.list_entries()
    if not entries:
        return redirect('index')
    chosen_entry = random.choice(entries)
    return redirect('entry', title=chosen_entry)

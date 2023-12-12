PAGE_SIZE: int = 2


def pagination_static(page_size: int, objects: list):
    pages = {}
    full_pages_number = len(objects) // page_size
    incomplete_page = len(objects) % page_size
    page_number = 0
    first_item = 0
    final_item = 0
    for item in range(full_pages_number):
        page_number += 1
        final_item = first_item + page_size
        pages[page_number] = {
            "objects": objects[first_item:final_item],
            "first_item": first_item,
            "final_item": final_item,
        }
        first_item = final_item
    if incomplete_page:
        final_item = len(objects)
        pages[page_number + 1] = {
            "objects": objects[first_item:],
            "first_item": first_item,
            "final_item": final_item,
        }
    return pages

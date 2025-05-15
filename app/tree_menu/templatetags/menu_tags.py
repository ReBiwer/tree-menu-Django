from typing import List, Dict, Set, Optional, Tuple, Any
from django import template
from django.utils.safestring import mark_safe
from tree_menu.models import Menu, MenuItem

register = template.Library()

def get_menu_tree(items: List[MenuItem]) -> List[MenuItem]:
    """
    Преобразует плоский список пунктов меню в дерево (иерархию).
    return список корневых пунктов (верхний уровень меню).
    """
    item_dict: Dict[int, MenuItem] = {item.id: item for item in items}
    tree: List[MenuItem] = []
    for item in items:
        if item.parent_id:
            parent = item_dict[item.parent_id]
            if not hasattr(parent, 'children_cache'):
                parent.children_cache = []
            parent.children_cache.append(item)
        else:
            tree.append(item)
    return tree

def find_active_path(items: List[MenuItem], current_path: str) -> Tuple[Optional[MenuItem], Set[int]]:
    active_item: Optional[MenuItem] = None
    for item in items:
        if item.get_url() == current_path:
            active_item = item
            break

    def build_path(item: Optional[MenuItem]) -> Set[int]:
        path: Set[int] = set()
        while item:
            path.add(item.id)
            item = item.parent
        return path
    
    if active_item:
        return active_item, build_path(active_item)
    return None, set()

def render_menu_items(nodes: List[MenuItem], active_path: Set[int], level: int = 0) -> str:
    html = '<ul>'
    for node in nodes:
        is_active = node.id in active_path
        has_active_child = any(child.id in active_path for child in getattr(node, 'children_cache', []))
        open_branch = is_active or has_active_child or level == 0
        li_class = 'active' if is_active else ''
        html += f'<li class="{li_class}"><a href="{node.get_url()}">{node.title}</a>'
        if getattr(node, 'children_cache', None) and open_branch:
            html += render_menu_items(node.children_cache, active_path, level+1)
        html += '</li>'
    html += '</ul>'
    return html

@register.simple_tag(takes_context=True)
def draw_menu(context: Dict[str, Any], menu_name: str) -> str:
    request = context['request']
    current_path = request.build_absolute_uri()
    try:
        menu = Menu.objects.get(name=menu_name)
    except Menu.DoesNotExist:
        return ''
    items: List[MenuItem] = list(MenuItem.objects.filter(menu=menu).select_related('parent').order_by('order', 'id'))
    tree = get_menu_tree(items)
    _, active_path = find_active_path(items, current_path)
    html = render_menu_items(tree, active_path)
    return mark_safe(html)
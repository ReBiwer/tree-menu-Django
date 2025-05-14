from django import template
from django.utils.safestring import mark_safe
from tree_menu.models import Menu, MenuItem
from django.urls import resolve

register = template.Library()

@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_path = request.path
    try:
        menu = Menu.objects.get(name=menu_name)
    except Menu.DoesNotExist:
        return ''
    # Получаем все пункты меню одним запросом
    items = list(MenuItem.objects.filter(menu=menu).select_related('parent').order_by('order', 'id'))
    # Строим дерево в памяти
    item_dict = {item.id: item for item in items}
    tree = []
    for item in items:
        if item.parent_id:
            parent = item_dict[item.parent_id]
            if not hasattr(parent, 'children_cache'):
                parent.children_cache = []
            parent.children_cache.append(item)
        else:
            tree.append(item)
    # Определяем активный пункт и путь к нему
    active_item, active_path = None, set()
    for item in items:
        if item.get_url() == current_path:
            active_item = item
            break
    def find_path(item):
        path = set()
        while item:
            path.add(item.id)
            item = item.parent
        return path
    if active_item:
        active_path = find_path(active_item)
    # Рекурсивная функция для рендера
    def render_items(nodes, level=0):
        html = '<ul>'
        for node in nodes:
            is_active = node.id in active_path
            has_active_child = any(child.id in active_path for child in getattr(node, 'children_cache', []))
            open_branch = is_active or has_active_child or level == 0
            li_class = 'active' if is_active else ''
            html += f'<li class="{li_class}"><a href="{node.get_url()}">{node.title}</a>'
            # Разворачиваем только нужные ветки
            if getattr(node, 'children_cache', None) and open_branch:
                html += render_items(node.children_cache, level+1)
            html += '</li>'
        html += '</ul>'
        return html
    return mark_safe(render_items(tree)) 